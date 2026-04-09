from __future__ import annotations

import asyncio
import contextlib
import random
import re
import secrets
import string
from collections import Counter
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

from fastapi import WebSocket

from .config import use_llm_generation
from .data.snippets import get_match_snippets
from .llm_generator import generate_match_problems, prefetch_problems, verify_submission
from .storage import StateStore

COUNTDOWN_SECONDS = 5
ROUND_SECONDS = 90
MATCH_ROUNDS = 3


@dataclass
class Player:
    id: str
    public_id: str
    name: str
    score: int = 0
    is_host: bool = False


@dataclass
class Connection:
    websocket: WebSocket
    player_id: str
    session_token: str


@dataclass
class Lobby:
    code: str
    players: list[Player]
    stage: str = "lobby"
    language_votes: dict[str, str] = field(default_factory=dict)
    difficulty_votes: dict[str, str] = field(default_factory=dict)
    selected_language: str = "Python"
    selected_difficulty: str = "Easy"
    current_snippet: dict[str, Any] | None = None
    countdown_remaining: int = COUNTDOWN_SECONDS
    round_remaining: int = ROUND_SECONDS
    winner_name: str | None = None
    winner_submission: str | None = None
    round_plan: list[dict[str, Any]] = field(default_factory=list)
    current_round_index: int = 0
    correct_submissions: list[dict[str, Any]] = field(default_factory=list)
    round_submissions: list[dict[str, Any]] = field(default_factory=list)


class LobbyManager:
    def __init__(self, store: StateStore) -> None:
        self.store = store
        self.lobbies: dict[str, Lobby] = {}
        self.connections: dict[str, list[Connection]] = {}
        self.sessions: dict[str, dict[str, str]] = {}
        self.countdown_tasks: dict[str, asyncio.Task[None]] = {}
        self.round_tasks: dict[str, asyncio.Task[None]] = {}
        self._restore_state()

    async def create_lobby(self, player_name: str) -> dict[str, Any]:
        cleaned_name = self._clean_name(player_name)
        code = self._generate_code()
        player = Player(id=self._new_id(), public_id=self._new_public_id(), name=cleaned_name, is_host=True)
        session_token = self._new_session_token()
        lobby = Lobby(code=code, players=[player])
        self.lobbies[code] = lobby
        self.connections[code] = []
        self.sessions[session_token] = {"lobby_code": code, "player_id": player.id}
        self._persist_state()
        return self.serialize_lobby(lobby, player.id, session_token)

    async def join_lobby(self, player_name: str, lobby_code: str) -> dict[str, Any]:
        lobby = self.get_lobby(lobby_code)
        if lobby.stage != "lobby":
            raise ValueError("You can only join a lobby before the match starts.")

        cleaned_name = self._clean_name(player_name)
        if any(player.name.lower() == cleaned_name.lower() for player in lobby.players):
            raise ValueError("Choose a different name. That player name is already taken.")

        player = Player(id=self._new_id(), public_id=self._new_public_id(), name=cleaned_name)
        session_token = self._new_session_token()
        lobby.players.append(player)
        self.sessions[session_token] = {"lobby_code": lobby.code, "player_id": player.id}
        self._persist_state()
        await self.broadcast_state(lobby.code)
        return self.serialize_lobby(lobby, player.id, session_token)

    async def vote(self, lobby_code: str, session_token: str, language: str, difficulty: str) -> dict[str, Any]:
        lobby, player = self._require_session_player(lobby_code, session_token)
        if lobby.stage != "lobby":
            raise ValueError("Votes are locked once the match starts.")

        lobby.language_votes[player.id] = language
        lobby.difficulty_votes[player.id] = difficulty
        self._persist_state()
        await self.broadcast_state(lobby_code)
        return self.serialize_lobby(lobby, player.id)

    async def start_round(self, lobby_code: str, session_token: str) -> dict[str, Any]:
        lobby, player = self._require_session_player(lobby_code, session_token)
        if not player.is_host:
            raise ValueError("Only the host can start the round.")
        if lobby.stage != "lobby":
            raise ValueError("You can only start a match from the lobby.")
        if len(lobby.players) < 1:
            raise ValueError("At least one player is required to start a match.")

        lobby.selected_language = self._winning_vote(lobby.language_votes, "Python")
        lobby.selected_difficulty = self._winning_vote(lobby.difficulty_votes, "Easy")

        # Try LLM generation first, fall back to hardcoded snippets
        llm_problems = None
        if use_llm_generation():
            llm_problems = generate_match_problems(
                lobby.selected_language,
                lobby.selected_difficulty,
                count=MATCH_ROUNDS,
            )

        if llm_problems:
            lobby.round_plan = [deepcopy(p) for p in llm_problems]
        else:
            lobby.round_plan = [
                deepcopy(snippet)
                for snippet in get_match_snippets(
                    lobby.selected_language,
                    lobby.selected_difficulty,
                    round_count=MATCH_ROUNDS,
                )
            ]

        lobby.current_round_index = 0
        self._reset_scores(lobby)
        self._prepare_round(lobby)
        self._cancel_task(self.countdown_tasks.pop(lobby.code, None))
        self._cancel_task(self.round_tasks.pop(lobby.code, None))
        self._persist_state()
        await self.broadcast_state(lobby_code)
        self.countdown_tasks[lobby.code] = asyncio.create_task(self._run_countdown(lobby.code))
        return self.serialize_lobby(lobby, player.id)

    async def submit_answer(self, lobby_code: str, session_token: str, code_submission: str) -> dict[str, Any]:
        lobby, player = self._require_session_player(lobby_code, session_token)

        if lobby.stage != "active" or not lobby.current_snippet:
            payload = self.serialize_lobby(lobby, player.id)
            payload["submissionFeedback"] = {
                "status": "blocked",
                "message": "This round is not currently accepting answers.",
            }
            return payload

        normalized_submission = self._normalize_code(code_submission)
        # Store raw submission for potential LLM verification
        if lobby.current_snippet and lobby.current_snippet.get("_llm_generated"):
            lobby.current_snippet["_last_raw_submission"] = code_submission.strip()
        is_correct = self._is_correct_submission(lobby.current_snippet, normalized_submission)
        existing_submission = next(
            (entry for entry in lobby.round_submissions if entry["player_id"] == player.id),
            None,
        )

        if existing_submission:
            payload = self.serialize_lobby(lobby, player.id)
            payload["submissionFeedback"] = {
                "status": "submitted",
                "correct": existing_submission.get("is_correct", False),
                "message": "Your submission is already recorded. Wait for the round to finish.",
            }
            return payload

        submission_entry = {
            "player_id": player.id,
            "player_public_id": player.public_id,
            "player_name": player.name,
            "submission": code_submission.strip(),
            "submitted": True,
            "is_correct": is_correct,
            "solve_order": None,
            "time_remaining": lobby.round_remaining,
            "explanation": None,
        }
        lobby.round_submissions.append(submission_entry)

        if is_correct:
            submission_entry["solve_order"] = len(lobby.correct_submissions) + 1
            lobby.correct_submissions.append(
                {
                    "player_id": player.id,
                    "player_public_id": player.public_id,
                    "player_name": player.name,
                    "submission": code_submission.strip(),
                    "solve_order": submission_entry["solve_order"],
                    "time_remaining": lobby.round_remaining,
                    "explanation": None,
                }
            )
            self._sync_round_leader(lobby)

        if len(lobby.round_submissions) >= len(lobby.players):
            self._finalize_round(lobby)

        self._persist_state()
        await self.broadcast_state(lobby_code)

        payload = self.serialize_lobby(lobby, player.id)
        payload["submissionFeedback"] = {
            "status": "submitted",
            "correct": is_correct,
            "message": (
                "Correct submission recorded. Waiting for round results."
                if is_correct
                else "Submission recorded. Waiting for round results."
            ),
        }
        return payload

    async def submit_explanation(self, lobby_code: str, session_token: str, explanation: str) -> dict[str, Any]:
        lobby, player = self._require_session_player(lobby_code, session_token)
        if lobby.stage not in {"active", "results"}:
            raise ValueError("You can only save an explanation during or after a round.")

        for entry in lobby.correct_submissions:
            if entry["player_id"] == player.id:
                entry["explanation"] = explanation.strip()
                self._persist_state()
                await self.broadcast_state(lobby.code)
                return {"saved": True, "message": "Explanation saved."}

        raise ValueError("Submit a correct fix before saving an explanation.")

    async def replay_round(self, lobby_code: str, session_token: str) -> dict[str, Any]:
        lobby, player = self._require_session_player(lobby_code, session_token)
        if not player.is_host:
            raise ValueError("Only the host can replay the round.")
        if lobby.stage != "results":
            raise ValueError("You can only continue after a round ends.")

        if lobby.current_round_index + 1 < len(lobby.round_plan):
            lobby.current_round_index += 1
            self._prepare_round(lobby)
            self._cancel_task(self.countdown_tasks.pop(lobby.code, None))
            self._cancel_task(self.round_tasks.pop(lobby.code, None))
            self._persist_state()
            await self.broadcast_state(lobby_code)
            self.countdown_tasks[lobby.code] = asyncio.create_task(self._run_countdown(lobby.code))
            return self.serialize_lobby(lobby, player.id)

        lobby.stage = "lobby"
        lobby.current_snippet = None
        lobby.round_plan = []
        lobby.current_round_index = 0
        lobby.countdown_remaining = COUNTDOWN_SECONDS
        lobby.round_remaining = ROUND_SECONDS
        lobby.winner_name = None
        lobby.winner_submission = None
        lobby.correct_submissions = []
        lobby.round_submissions = []
        self._cancel_task(self.countdown_tasks.pop(lobby.code, None))
        self._cancel_task(self.round_tasks.pop(lobby.code, None))
        self._persist_state()
        await self.broadcast_state(lobby_code)
        return self.serialize_lobby(lobby, player.id)

    async def register_socket(self, lobby_code: str, session_token: str, websocket: WebSocket) -> None:
        lobby, player = self._require_session_player(lobby_code, session_token)
        await websocket.accept()
        self.connections.setdefault(lobby.code, []).append(
            Connection(websocket=websocket, player_id=player.id, session_token=session_token)
        )
        await websocket.send_json({"type": "state", "payload": self.serialize_lobby(lobby, player.id)})

    async def disconnect_socket(self, lobby_code: str, session_token: str, websocket: WebSocket) -> None:
        code = lobby_code.strip().upper()
        sockets = self.connections.get(code, [])
        connection = next((item for item in sockets if item.websocket is websocket), None)
        if connection:
            sockets.remove(connection)

        session = self.sessions.pop(session_token, None)
        if not session:
            return

        lobby = self.lobbies.get(code)
        if not lobby:
            return

        player_id = session["player_id"]
        lobby.players = [player for player in lobby.players if player.id != player_id]
        lobby.language_votes.pop(player_id, None)
        lobby.difficulty_votes.pop(player_id, None)
        lobby.correct_submissions = [entry for entry in lobby.correct_submissions if entry["player_id"] != player_id]
        lobby.round_submissions = [entry for entry in lobby.round_submissions if entry["player_id"] != player_id]

        if not lobby.players:
            self._delete_lobby(code)
            return

        if not any(player.is_host for player in lobby.players):
            lobby.players[0].is_host = True

        self._sync_round_leader(lobby)
        if lobby.stage == "active" and len(lobby.round_submissions) >= len(lobby.players):
            self._finalize_round(lobby)

        self._persist_state()
        await self.broadcast_state(code)

    async def broadcast_state(self, lobby_code: str) -> None:
        lobby = self.get_lobby(lobby_code)
        dead_connections: list[Connection] = []

        for connection in self.connections.get(lobby.code, []):
            try:
                await connection.websocket.send_json(
                    {"type": "state", "payload": self.serialize_lobby(lobby, connection.player_id)}
                )
            except RuntimeError:
                dead_connections.append(connection)

        for connection in dead_connections:
            await self.disconnect_socket(lobby.code, connection.session_token, connection.websocket)

    def serialize_lobby(
        self,
        lobby: Lobby,
        player_id: str | None = None,
        session_token: str | None = None,
    ) -> dict[str, Any]:
        language_tally = Counter(lobby.language_votes.values())
        difficulty_tally = Counter(lobby.difficulty_votes.values())
        current_player = self._get_player(lobby, player_id) if player_id else None

        return {
            "playerPublicId": current_player.public_id if current_player else None,
            "sessionToken": session_token,
            "code": lobby.code,
            "stage": lobby.stage,
            "selectedLanguage": lobby.selected_language,
            "selectedDifficulty": lobby.selected_difficulty,
            "countdownRemaining": lobby.countdown_remaining,
            "roundRemaining": lobby.round_remaining,
            "winner": {
                "name": lobby.winner_name,
                "submission": lobby.winner_submission,
            },
            "roundResults": [
                {
                    "playerPublicId": entry["player_public_id"],
                    "name": entry["player_name"],
                    "submission": entry["submission"],
                    "submitted": entry.get("submitted", False),
                    "isCorrect": entry.get("is_correct", False),
                    "solveOrder": entry["solve_order"],
                    "timeRemaining": entry["time_remaining"],
                    "pointsEarned": (
                        self._points_for_order(entry["solve_order"], len(lobby.players))
                        if entry.get("is_correct") and entry.get("solve_order")
                        else 0
                    ),
                    "explanation": entry.get("explanation"),
                }
                for entry in lobby.round_submissions
            ],
            "currentRound": 0 if not lobby.round_plan else lobby.current_round_index + 1,
            "totalRounds": len(lobby.round_plan),
            "hasNextRound": lobby.current_round_index + 1 < len(lobby.round_plan),
            "players": [
                {
                    "publicId": player.public_id,
                    "name": player.name,
                    "score": player.score,
                    "isHost": player.is_host,
                }
                for player in sorted(lobby.players, key=lambda current: (-current.score, current.name))
            ],
            "votes": {
                "language": {
                    "Python": language_tally.get("Python", 0),
                    "Java": language_tally.get("Java", 0),
                    "C": language_tally.get("C", 0),
                    "C++": language_tally.get("C++", 0),
                },
                "difficulty": {
                    "Easy": difficulty_tally.get("Easy", 0),
                    "Medium": difficulty_tally.get("Medium", 0),
                    "Hard": difficulty_tally.get("Hard", 0),
                },
            },
            "snippet": None if not lobby.current_snippet else self._public_snippet(lobby),
        }

    def get_lobby(self, lobby_code: str) -> Lobby:
        code = lobby_code.strip().upper()
        lobby = self.lobbies.get(code)
        if not lobby:
            raise KeyError("Lobby not found.")
        return lobby

    async def _run_countdown(self, lobby_code: str) -> None:
        try:
            lobby = self.get_lobby(lobby_code)
            while lobby.stage == "countdown" and lobby.countdown_remaining > 0:
                await asyncio.sleep(1)
                lobby.countdown_remaining -= 1
                self._persist_state()
                await self.broadcast_state(lobby_code)

            if lobby.stage != "countdown":
                return

            lobby.stage = "active"
            self._persist_state()
            await self.broadcast_state(lobby_code)
            self.round_tasks[lobby.code] = asyncio.create_task(self._run_round_timer(lobby_code))
        except asyncio.CancelledError:
            return
        finally:
            self.countdown_tasks.pop(lobby_code, None)

    async def _run_round_timer(self, lobby_code: str) -> None:
        try:
            lobby = self.get_lobby(lobby_code)
            while lobby.stage == "active" and lobby.round_remaining > 0:
                await asyncio.sleep(1)
                lobby.round_remaining -= 1
                self._persist_state()
                await self.broadcast_state(lobby_code)

            if lobby.stage == "active":
                self._finalize_round(lobby)
                self._persist_state()
                await self.broadcast_state(lobby_code)
        except asyncio.CancelledError:
            return
        finally:
            self.round_tasks.pop(lobby_code, None)

    def _prepare_round(self, lobby: Lobby) -> None:
        lobby.current_snippet = deepcopy(lobby.round_plan[lobby.current_round_index])
        lobby.stage = "countdown"
        lobby.countdown_remaining = COUNTDOWN_SECONDS
        lobby.round_remaining = ROUND_SECONDS
        lobby.winner_name = None
        lobby.winner_submission = None
        lobby.correct_submissions = []
        lobby.round_submissions = []

    def _reset_scores(self, lobby: Lobby) -> None:
        for player in lobby.players:
            player.score = 0

    def _require_session_player(self, lobby_code: str, session_token: str) -> tuple[Lobby, Player]:
        if not session_token:
            raise PermissionError("Missing session token.")

        session = self.sessions.get(session_token)
        if not session:
            raise PermissionError("Your session is no longer valid. Rejoin the lobby.")

        code = lobby_code.strip().upper()
        if session["lobby_code"] != code:
            raise PermissionError("This session does not belong to the requested lobby.")

        lobby = self.get_lobby(code)
        player = self._get_player(lobby, session["player_id"])
        return lobby, player

    def _get_player(self, lobby: Lobby, player_id: str | None) -> Player:
        if not player_id:
            raise KeyError("Player not found in lobby.")
        for player in lobby.players:
            if player.id == player_id:
                return player
        raise KeyError("Player not found in lobby.")

    def _generate_code(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = "".join(random.choices(alphabet, k=5))
            if code not in self.lobbies:
                return code

    def _new_id(self) -> str:
        return uuid4().hex[:8]

    def _new_public_id(self) -> str:
        return uuid4().hex[:10]

    def _new_session_token(self) -> str:
        return secrets.token_urlsafe(24)

    def _winning_vote(self, votes: dict[str, str], fallback: str) -> str:
        if not votes:
            return fallback
        counts = Counter(votes.values())
        return counts.most_common(1)[0][0]

    def _is_correct_submission(self, snippet: dict[str, Any], normalized_submission: str) -> bool:
        # Exact match first (fast path)
        if normalized_submission == self._normalize_code(snippet["fixed_code"]):
            return True

        # For LLM-generated problems, also try LLM verification
        if snippet.get("_llm_generated") and use_llm_generation():
            original_submission = snippet.get("_last_raw_submission", "")
            if original_submission:
                llm_result = verify_submission(snippet, original_submission)
                if llm_result:
                    return True

        return False

    def _sync_round_leader(self, lobby: Lobby) -> None:
        if not lobby.correct_submissions:
            lobby.winner_name = None
            lobby.winner_submission = None
            return

        leader = lobby.correct_submissions[0]
        lobby.winner_name = leader["player_name"]
        lobby.winner_submission = leader["submission"]

    def _finalize_round(self, lobby: Lobby) -> None:
        if lobby.stage != "active":
            return

        for entry in lobby.correct_submissions:
            player = self._get_player(lobby, entry["player_id"])
            player.score += self._points_for_order(entry["solve_order"], len(lobby.players))

        if lobby.correct_submissions:
            self._sync_round_leader(lobby)
        else:
            lobby.winner_name = "No one"
            lobby.winner_submission = "No correct fix was submitted before the timer expired."

        lobby.stage = "results"

        # Prefetch next batch of problems in background
        if use_llm_generation():
            asyncio.ensure_future(self._prefetch_problems(lobby.selected_language, lobby.selected_difficulty))

    async def _prefetch_problems(self, language: str, difficulty: str) -> None:
        """Background task to pre-generate problems for the next match."""
        try:
            await asyncio.get_event_loop().run_in_executor(None, prefetch_problems, language, difficulty)
        except Exception:
            pass  # Non-critical, silent fail

    def _points_for_order(self, solve_order: int, total_players: int) -> int:
        return max(total_players - solve_order + 1, 1)

    def _normalize_code(self, value: str) -> str:
        without_block_comments = re.sub(r"/\*.*?\*/", "", value, flags=re.S)
        without_line_comments = re.sub(r"//.*", "", without_block_comments)
        without_hash_comments = re.sub(r"#.*", "", without_line_comments)
        return re.sub(r"\s+", "", without_hash_comments).strip().lower()

    def _clean_name(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Player name cannot be blank.")
        return cleaned

    def _public_snippet(self, lobby: Lobby) -> dict[str, Any]:
        if not lobby.current_snippet:
            return None

        payload = {
            "id": lobby.current_snippet["id"],
            "language": lobby.current_snippet["language"],
            "difficulty": lobby.current_snippet["difficulty"],
            "category": lobby.current_snippet["category"],
            "title": lobby.current_snippet["title"],
            "problem_statement": lobby.current_snippet.get("problem_statement"),
            "code": lobby.current_snippet["buggy_code"],
            "buggy_code": lobby.current_snippet["buggy_code"],
            "testCases": lobby.current_snippet["test_cases"],
            "test_cases": lobby.current_snippet["test_cases"],
            "traceSteps": lobby.current_snippet["trace_steps"],
            "trace_steps": lobby.current_snippet["trace_steps"],
            "referenceFix": None,
            "explanation": None,
        }
        if lobby.stage == "results":
            payload["referenceFix"] = lobby.current_snippet["fixed_code"]
            payload["explanation"] = lobby.current_snippet["explanation"]
        return payload

    def _delete_lobby(self, lobby_code: str) -> None:
        for token, session in list(self.sessions.items()):
            if session["lobby_code"] == lobby_code:
                self.sessions.pop(token, None)

        self.lobbies.pop(lobby_code, None)
        self.connections.pop(lobby_code, None)
        self._cancel_task(self.countdown_tasks.pop(lobby_code, None))
        self._cancel_task(self.round_tasks.pop(lobby_code, None))
        self._persist_state()

    def _cancel_task(self, task: asyncio.Task[None] | None) -> None:
        if task and not task.done():
            task.cancel()

    def _persist_state(self) -> None:
        payload = {
            "lobbies": [self._serialize_lobby_for_store(lobby) for lobby in self.lobbies.values()],
            "sessions": [
                {"token": token, "lobby_code": session["lobby_code"], "player_id": session["player_id"]}
                for token, session in self.sessions.items()
            ],
        }
        self.store.save(payload)

    def _restore_state(self) -> None:
        snapshot = self.store.load()
        for lobby_payload in snapshot.get("lobbies", []):
            players = [Player(**player_payload) for player_payload in lobby_payload.get("players", [])]
            lobby = Lobby(
                code=lobby_payload["code"],
                players=players,
                stage=lobby_payload.get("stage", "lobby"),
                language_votes=lobby_payload.get("language_votes", {}),
                difficulty_votes=lobby_payload.get("difficulty_votes", {}),
                selected_language=lobby_payload.get("selected_language", "Python"),
                selected_difficulty=lobby_payload.get("selected_difficulty", "Easy"),
                current_snippet=lobby_payload.get("current_snippet"),
                countdown_remaining=lobby_payload.get("countdown_remaining", COUNTDOWN_SECONDS),
                round_remaining=lobby_payload.get("round_remaining", ROUND_SECONDS),
                winner_name=lobby_payload.get("winner_name"),
                winner_submission=lobby_payload.get("winner_submission"),
                round_plan=lobby_payload.get("round_plan", []),
                current_round_index=lobby_payload.get("current_round_index", 0),
                correct_submissions=lobby_payload.get("correct_submissions", []),
                round_submissions=lobby_payload.get("round_submissions", []),
            )
            if lobby.stage in {"countdown", "active"}:
                lobby.stage = "lobby"
                lobby.current_snippet = None
                lobby.round_plan = []
                lobby.current_round_index = 0
                lobby.countdown_remaining = COUNTDOWN_SECONDS
                lobby.round_remaining = ROUND_SECONDS
                lobby.winner_name = None
                lobby.winner_submission = None
                lobby.correct_submissions = []
                lobby.round_submissions = []

            self.lobbies[lobby.code] = lobby
            self.connections[lobby.code] = []

        for session_payload in snapshot.get("sessions", []):
            lobby = self.lobbies.get(session_payload["lobby_code"])
            if lobby and any(player.id == session_payload["player_id"] for player in lobby.players):
                self.sessions[session_payload["token"]] = {
                    "lobby_code": session_payload["lobby_code"],
                    "player_id": session_payload["player_id"],
                }

    def _serialize_lobby_for_store(self, lobby: Lobby) -> dict[str, Any]:
        return {
            "code": lobby.code,
            "players": [asdict(player) for player in lobby.players],
            "stage": lobby.stage,
            "language_votes": lobby.language_votes,
            "difficulty_votes": lobby.difficulty_votes,
            "selected_language": lobby.selected_language,
            "selected_difficulty": lobby.selected_difficulty,
            "current_snippet": lobby.current_snippet,
            "countdown_remaining": lobby.countdown_remaining,
            "round_remaining": lobby.round_remaining,
            "winner_name": lobby.winner_name,
            "winner_submission": lobby.winner_submission,
            "round_plan": lobby.round_plan,
            "current_round_index": lobby.current_round_index,
            "correct_submissions": lobby.correct_submissions,
            "round_submissions": lobby.round_submissions,
        }

    async def shutdown(self) -> None:
        for task in list(self.countdown_tasks.values()):
            self._cancel_task(task)
        for task in list(self.round_tasks.values()):
            self._cancel_task(task)

        with contextlib.suppress(Exception):
            self._persist_state()

from __future__ import annotations

import asyncio
import random
import re
import string
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from fastapi import WebSocket

from .data.snippets import get_match_snippets

COUNTDOWN_SECONDS = 5
ROUND_SECONDS = 90
MATCH_ROUNDS = 3


@dataclass
class Player:
    id: str
    name: str
    score: int = 0
    is_host: bool = False


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
    winner_id: str | None = None
    winner_name: str | None = None
    winner_submission: str | None = None
    round_plan: list[dict[str, Any]] = field(default_factory=list)
    current_round_index: int = 0


class LobbyManager:
    def __init__(self) -> None:
        self.lobbies: dict[str, Lobby] = {}
        self.connections: dict[str, list[WebSocket]] = {}

    async def create_lobby(self, player_name: str) -> dict[str, Any]:
        code = self._generate_code()
        player = Player(id=self._new_id(), name=player_name.strip(), is_host=True)
        lobby = Lobby(code=code, players=[player])
        self.lobbies[code] = lobby
        self.connections[code] = []
        return self.serialize_lobby(lobby, player.id)

    async def join_lobby(self, player_name: str, lobby_code: str) -> dict[str, Any]:
        lobby = self.get_lobby(lobby_code)
        player = Player(id=self._new_id(), name=player_name.strip())
        lobby.players.append(player)
        await self.broadcast_state(lobby.code)
        return self.serialize_lobby(lobby, player.id)

    async def vote(self, lobby_code: str, player_id: str, language: str, difficulty: str) -> dict[str, Any]:
        lobby = self.get_lobby(lobby_code)
        self._ensure_player(lobby, player_id)
        lobby.language_votes[player_id] = language
        lobby.difficulty_votes[player_id] = difficulty
        await self.broadcast_state(lobby_code)
        return self.serialize_lobby(lobby, player_id)

    async def start_round(self, lobby_code: str, player_id: str) -> dict[str, Any]:
        lobby = self.get_lobby(lobby_code)
        player = self._ensure_player(lobby, player_id)
        if not player.is_host:
            raise ValueError("Only the host can start the round.")

        lobby.selected_language = self._winning_vote(lobby.language_votes, "Python")
        lobby.selected_difficulty = self._winning_vote(lobby.difficulty_votes, "Easy")
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
        await self.broadcast_state(lobby_code)
        asyncio.create_task(self._run_countdown(lobby.code))
        return self.serialize_lobby(lobby, player_id)

    async def submit_answer(self, lobby_code: str, player_id: str, code_submission: str) -> dict[str, Any]:
        lobby = self.get_lobby(lobby_code)
        player = self._ensure_player(lobby, player_id)

        if lobby.stage != "active" or not lobby.current_snippet:
            payload = self.serialize_lobby(lobby, player_id)
            payload["submissionFeedback"] = {
                "status": "blocked",
                "message": "This round is not currently accepting answers.",
            }
            return payload

        normalized_submission = self._normalize_code(code_submission)
        is_correct = self._is_correct_submission(lobby.current_snippet, normalized_submission)

        if is_correct and lobby.winner_id is None:
            lobby.winner_id = player.id
            lobby.winner_name = player.name
            lobby.winner_submission = code_submission.strip()
            player.score += 1
            lobby.stage = "results"
            await self.broadcast_state(lobby_code)
            payload = self.serialize_lobby(lobby, player_id)
            payload["submissionFeedback"] = {
                "status": "correct",
                "message": "Correct. You won the round.",
            }
            return payload

        payload = self.serialize_lobby(lobby, player_id)
        payload["submissionFeedback"] = {
            "status": "incorrect",
            "message": "Submission received, but the fix does not match yet. Keep editing and try again.",
        }
        return payload

    async def replay_round(self, lobby_code: str, player_id: str) -> dict[str, Any]:
        lobby = self.get_lobby(lobby_code)
        player = self._ensure_player(lobby, player_id)
        if not player.is_host:
            raise ValueError("Only the host can replay the round.")

        if lobby.stage != "results":
            raise ValueError("You can only continue after a round ends.")

        if lobby.current_round_index + 1 < len(lobby.round_plan):
            lobby.current_round_index += 1
            self._prepare_round(lobby)
            await self.broadcast_state(lobby_code)
            asyncio.create_task(self._run_countdown(lobby.code))
            return self.serialize_lobby(lobby, player_id)

        lobby.stage = "lobby"
        lobby.current_snippet = None
        lobby.round_plan = []
        lobby.current_round_index = 0
        lobby.countdown_remaining = COUNTDOWN_SECONDS
        lobby.round_remaining = ROUND_SECONDS
        lobby.winner_id = None
        lobby.winner_name = None
        lobby.winner_submission = None
        await self.broadcast_state(lobby_code)
        return self.serialize_lobby(lobby, player_id)

    async def register_socket(self, lobby_code: str, websocket: WebSocket) -> None:
        lobby = self.get_lobby(lobby_code)
        await websocket.accept()
        self.connections.setdefault(lobby.code, []).append(websocket)
        await websocket.send_json({"type": "state", "payload": self.serialize_lobby(lobby)})

    def unregister_socket(self, lobby_code: str, websocket: WebSocket) -> None:
        sockets = self.connections.get(lobby_code, [])
        if websocket in sockets:
            sockets.remove(websocket)

    async def broadcast_state(self, lobby_code: str) -> None:
        lobby = self.get_lobby(lobby_code)
        dead_sockets: list[WebSocket] = []

        for socket in self.connections.get(lobby_code, []):
            try:
                await socket.send_json({"type": "state", "payload": self.serialize_lobby(lobby)})
            except RuntimeError:
                dead_sockets.append(socket)

        for socket in dead_sockets:
            self.unregister_socket(lobby_code, socket)

    def serialize_lobby(self, lobby: Lobby, player_id: str | None = None) -> dict[str, Any]:
        language_tally = Counter(lobby.language_votes.values())
        difficulty_tally = Counter(lobby.difficulty_votes.values())

        return {
            "playerId": player_id,
            "code": lobby.code,
            "stage": lobby.stage,
            "selectedLanguage": lobby.selected_language,
            "selectedDifficulty": lobby.selected_difficulty,
            "countdownRemaining": lobby.countdown_remaining,
            "roundRemaining": lobby.round_remaining,
            "winner": {
                "id": lobby.winner_id,
                "name": lobby.winner_name,
                "submission": lobby.winner_submission,
            },
            "currentRound": 0 if not lobby.round_plan else lobby.current_round_index + 1,
            "totalRounds": len(lobby.round_plan),
            "hasNextRound": lobby.current_round_index + 1 < len(lobby.round_plan),
            "players": [
                {
                    "id": player.id,
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
            "snippet": None
            if not lobby.current_snippet
            else {
                "id": lobby.current_snippet["id"],
                "language": lobby.current_snippet["language"],
                "difficulty": lobby.current_snippet["difficulty"],
                "category": lobby.current_snippet["category"],
                "title": lobby.current_snippet["title"],
                "code": lobby.current_snippet["code"],
                "referenceFix": lobby.current_snippet["fixed_code"] if lobby.stage == "results" else None,
            },
        }

    def get_lobby(self, lobby_code: str) -> Lobby:
        code = lobby_code.strip().upper()
        lobby = self.lobbies.get(code)
        if not lobby:
            raise KeyError("Lobby not found.")
        return lobby

    async def _run_countdown(self, lobby_code: str) -> None:
        lobby = self.get_lobby(lobby_code)
        # The lobby remains authoritative for timers so all connected clients
        # receive the same countdown and round state over WebSockets.
        while lobby.stage == "countdown" and lobby.countdown_remaining > 0:
            await asyncio.sleep(1)
            lobby.countdown_remaining -= 1
            await self.broadcast_state(lobby_code)

        if lobby.stage != "countdown":
            return

        lobby.stage = "active"
        await self.broadcast_state(lobby_code)
        asyncio.create_task(self._run_round_timer(lobby_code))

    async def _run_round_timer(self, lobby_code: str) -> None:
        lobby = self.get_lobby(lobby_code)
        while lobby.stage == "active" and lobby.round_remaining > 0 and lobby.winner_id is None:
            await asyncio.sleep(1)
            lobby.round_remaining -= 1
            await self.broadcast_state(lobby_code)

        if lobby.stage == "active" and lobby.winner_id is None:
            lobby.stage = "results"
            lobby.winner_name = "No one"
            lobby.winner_submission = "No correct fix was submitted before the timer expired."
            await self.broadcast_state(lobby_code)

    def _prepare_round(self, lobby: Lobby) -> None:
        lobby.current_snippet = deepcopy(lobby.round_plan[lobby.current_round_index])
        lobby.stage = "countdown"
        lobby.countdown_remaining = COUNTDOWN_SECONDS
        lobby.round_remaining = ROUND_SECONDS
        lobby.winner_id = None
        lobby.winner_name = None
        lobby.winner_submission = None

    def _reset_scores(self, lobby: Lobby) -> None:
        for player in lobby.players:
            player.score = 0

    def _ensure_player(self, lobby: Lobby, player_id: str) -> Player:
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

    def _winning_vote(self, votes: dict[str, str], fallback: str) -> str:
        if not votes:
            return fallback
        counts = Counter(votes.values())
        return counts.most_common(1)[0][0]

    def _is_correct_submission(self, snippet: dict[str, Any], normalized_submission: str) -> bool:
        return normalized_submission == self._normalize_code(snippet["fixed_code"])

    def _normalize_code(self, value: str) -> str:
        without_block_comments = re.sub(r"/\*.*?\*/", "", value, flags=re.S)
        without_line_comments = re.sub(r"//.*", "", without_block_comments)
        without_hash_comments = re.sub(r"#.*", "", without_line_comments)
        return re.sub(r"\s+", "", without_hash_comments).strip().lower()

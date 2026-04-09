from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config import allowed_origins, state_file_path
from .data.snippets import ALL_SNIPPETS, get_problem_by_id, get_public_problem_by_id
from .game_state import LobbyManager
from .models.schemas import (
    CreateLobbyRequest,
    JoinLobbyRequest,
    RunTraceRequest,
    SubmitAnswerRequest,
    SubmitExplanationRequest,
    SubmitHypothesisRequest,
    SubmitSolutionRequest,
    VoteRequest,
)
from .storage import StateStore

store = StateStore(state_file_path())
manager = LobbyManager(store)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await manager.shutdown()


app = FastAPI(title="GLITCHLABS API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Session-Token"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


def _get_unified_problem(problem_id: str) -> dict:
    if problem_id.startswith("llm-"):
        from .llm_generator import get_generated_problem
        prob = get_generated_problem(problem_id)
        if prob:
            return prob
        raise KeyError("LLM generated problem not found or expired from memory.")
    return get_problem_by_id(problem_id)


@app.get("/problem/{problem_id}")
def get_problem(problem_id: str) -> dict:
    try:
        problem = _get_unified_problem(problem_id)
        return {
            "id": problem["id"],
            "language": problem["language"],
            "difficulty": problem["difficulty"],
            "category": problem["category"],
            "title": problem["title"],
            "problem_statement": problem["problem_statement"],
            "buggy_code": problem["buggy_code"],
            "test_cases": problem["test_cases"],
        }
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/questions")
def get_questions() -> list[dict[str, str]]:
    return [{"id": question["id"], "title": question["title"]} for question in ALL_SNIPPETS]


@app.post("/submit-hypothesis")
def submit_hypothesis(payload: SubmitHypothesisRequest) -> dict:
    try:
        problem = _get_unified_problem(payload.problem_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    correct = payload.selected_hypothesis == problem["bug_type"]
    return {
        "correct": correct,
        "actual_bug_type": problem["bug_type"],
        "explanation": (
            "Your hypothesis matches the underlying bug class."
            if correct
            else f"This problem is a {problem['bug_type'].replace('_', ' ')}. {problem['explanation']}"
        ),
    }


@app.post("/run-trace")
def run_trace(payload: RunTraceRequest) -> dict:
    try:
        problem = _get_unified_problem(payload.problem_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {"execution_steps": problem["trace_steps"]}


@app.post("/submit-solution")
def submit_solution(payload: SubmitSolutionRequest) -> dict:
    try:
        problem = _get_unified_problem(payload.problem_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    normalize = lambda value: "".join(value.split()).lower()
    correct = normalize(payload.code_submission) == normalize(problem["correct_code"])
    
    # Fallback to LLM verification if exact match fails
    if not correct and problem.get("_llm_generated"):
        from .config import use_llm_generation
        if use_llm_generation():
            from .llm_generator import verify_submission
            llm_result = verify_submission(problem, payload.code_submission)
            if llm_result:
                correct = True

    return {"correct": correct, "explanation": problem["explanation"]}


@app.post("/api/lobbies")
async def create_lobby(payload: CreateLobbyRequest) -> dict:
    try:
        return await manager.create_lobby(payload.player_name)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/api/lobbies/join")
async def join_lobby(payload: JoinLobbyRequest) -> dict:
    try:
        return await manager.join_lobby(payload.player_name, payload.lobby_code)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/api/lobbies/{lobby_code}/vote")
async def vote(
    lobby_code: str,
    payload: VoteRequest,
    x_session_token: str = Header(default="", alias="X-Session-Token"),
) -> dict:
    try:
        return await manager.vote(lobby_code, x_session_token, payload.language, payload.difficulty)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.post("/api/lobbies/{lobby_code}/start")
async def start_round(lobby_code: str, x_session_token: str = Header(default="", alias="X-Session-Token")) -> dict:
    try:
        return await manager.start_round(lobby_code, x_session_token)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.post("/api/lobbies/{lobby_code}/submit")
async def submit_answer(
    lobby_code: str,
    payload: SubmitAnswerRequest,
    x_session_token: str = Header(default="", alias="X-Session-Token"),
) -> dict:
    try:
        return await manager.submit_answer(lobby_code, x_session_token, payload.code_submission)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error


@app.post("/api/lobbies/{lobby_code}/explain")
async def submit_explanation(
    lobby_code: str,
    payload: SubmitExplanationRequest,
    x_session_token: str = Header(default="", alias="X-Session-Token"),
) -> dict:
    try:
        return await manager.submit_explanation(lobby_code, x_session_token, payload.explanation)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.post("/api/lobbies/{lobby_code}/replay")
async def replay_round(lobby_code: str, x_session_token: str = Header(default="", alias="X-Session-Token")) -> dict:
    try:
        return await manager.replay_round(lobby_code, x_session_token)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.websocket("/ws/lobbies/{lobby_code}")
async def lobby_socket(websocket: WebSocket, lobby_code: str) -> None:
    session_token = websocket.query_params.get("token", "")
    try:
        await manager.register_socket(lobby_code, session_token, websocket)
        while True:
            await websocket.receive_text()
    except KeyError:
        await websocket.close(code=4404)
    except PermissionError:
        await websocket.close(code=4401)
    except WebSocketDisconnect:
        await manager.disconnect_socket(lobby_code.upper(), session_token, websocket)

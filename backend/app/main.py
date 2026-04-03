from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .data.snippets import get_problem_by_id
from .game_state import LobbyManager
from .models.schemas import (
    CreateLobbyRequest,
    JoinLobbyRequest,
    ReplayRoundRequest,
    RunTraceRequest,
    StartRoundRequest,
    SubmitAnswerRequest,
    SubmitHypothesisRequest,
    SubmitSolutionRequest,
    VoteRequest,
)

app = FastAPI(title="GLITCHLABS API")
manager = LobbyManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/problem/{problem_id}")
def get_problem(problem_id: str) -> dict:
    try:
        return get_problem_by_id(problem_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/submit-hypothesis")
def submit_hypothesis(payload: SubmitHypothesisRequest) -> dict:
    try:
        problem = get_problem_by_id(payload.problem_id)
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
        problem = get_problem_by_id(payload.problem_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {"execution_steps": problem["trace_steps"]}


@app.post("/submit-solution")
def submit_solution(payload: SubmitSolutionRequest) -> dict:
    try:
        problem = get_problem_by_id(payload.problem_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    normalize = lambda value: "".join(value.split()).lower()
    correct = normalize(payload.code_submission) == normalize(problem["correct_code"])
    return {"correct": correct, "explanation": problem["explanation"]}


@app.post("/api/lobbies")
async def create_lobby(payload: CreateLobbyRequest) -> dict:
    return await manager.create_lobby(payload.player_name)


@app.post("/api/lobbies/join")
async def join_lobby(payload: JoinLobbyRequest) -> dict:
    try:
        return await manager.join_lobby(payload.player_name, payload.lobby_code)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/lobbies/{lobby_code}/vote")
async def vote(lobby_code: str, payload: VoteRequest) -> dict:
    try:
        return await manager.vote(lobby_code, payload.player_id, payload.language, payload.difficulty)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/lobbies/{lobby_code}/start")
async def start_round(lobby_code: str, payload: StartRoundRequest) -> dict:
    try:
        return await manager.start_round(lobby_code, payload.player_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error


@app.post("/api/lobbies/{lobby_code}/submit")
async def submit_answer(lobby_code: str, payload: SubmitAnswerRequest) -> dict:
    try:
        return await manager.submit_answer(lobby_code, payload.player_id, payload.code_submission)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/lobbies/{lobby_code}/replay")
async def replay_round(lobby_code: str, payload: ReplayRoundRequest) -> dict:
    try:
        return await manager.replay_round(lobby_code, payload.player_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error


@app.websocket("/ws/lobbies/{lobby_code}")
async def lobby_socket(websocket: WebSocket, lobby_code: str) -> None:
    try:
        await manager.register_socket(lobby_code, websocket)
        while True:
            await websocket.receive_text()
    except KeyError:
        await websocket.close(code=4404)
    except WebSocketDisconnect:
        manager.unregister_socket(lobby_code.upper(), websocket)

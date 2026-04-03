from typing import Literal

from pydantic import BaseModel, Field


Language = Literal["Python", "Java", "C", "C++"]
Difficulty = Literal["Easy", "Medium", "Hard"]


class CreateLobbyRequest(BaseModel):
    player_name: str = Field(min_length=1, max_length=24)


class JoinLobbyRequest(BaseModel):
    player_name: str = Field(min_length=1, max_length=24)
    lobby_code: str = Field(min_length=5, max_length=5)


class VoteRequest(BaseModel):
    player_id: str
    language: Language
    difficulty: Difficulty


class StartRoundRequest(BaseModel):
    player_id: str


class SubmitAnswerRequest(BaseModel):
    player_id: str
    code_submission: str = Field(min_length=1, max_length=10000)


class ReplayRoundRequest(BaseModel):
    player_id: str


class SubmitHypothesisRequest(BaseModel):
    problem_id: str
    selected_hypothesis: str


class RunTraceRequest(BaseModel):
    problem_id: str


class SubmitSolutionRequest(BaseModel):
    problem_id: str
    code_submission: str = Field(min_length=1, max_length=10000)

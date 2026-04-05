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
    language: Language
    difficulty: Difficulty


class SubmitAnswerRequest(BaseModel):
    code_submission: str = Field(min_length=1, max_length=10000)


class SubmitHypothesisRequest(BaseModel):
    problem_id: str
    selected_hypothesis: str


class RunTraceRequest(BaseModel):
    problem_id: str


class SubmitSolutionRequest(BaseModel):
    problem_id: str
    code_submission: str = Field(min_length=1, max_length=10000)


class SubmitExplanationRequest(BaseModel):
    explanation: str = Field(min_length=1, max_length=2000)

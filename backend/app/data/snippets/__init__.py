from copy import deepcopy
from random import shuffle

from .arrays import SNIPPETS as ARRAY_SNIPPETS
from .binary_search import SNIPPETS as BINARY_SEARCH_SNIPPETS
from .dp import SNIPPETS as DP_SNIPPETS
from .hashing import SNIPPETS as HASHING_SNIPPETS
from .recursion import SNIPPETS as RECURSION_SNIPPETS
from .sliding_window import SNIPPETS as SLIDING_WINDOW_SNIPPETS
from .stack_queue import SNIPPETS as STACK_QUEUE_SNIPPETS
from .strings import SNIPPETS as STRING_SNIPPETS

ALL_SNIPPETS = [
    *ARRAY_SNIPPETS,
    *STRING_SNIPPETS,
    *BINARY_SEARCH_SNIPPETS,
    *HASHING_SNIPPETS,
    *STACK_QUEUE_SNIPPETS,
    *SLIDING_WINDOW_SNIPPETS,
    *RECURSION_SNIPPETS,
    *DP_SNIPPETS,
]

PROBLEMS = ALL_SNIPPETS


def _build_problem_statement(problem: dict) -> str:
    existing = problem.get("problem_statement")
    if existing:
        return existing

    test_cases = problem.get("test_cases", [])
    sample_case = test_cases[0] if test_cases else {}
    expected_output = sample_case.get("expected_output", "")
    sample_input = sample_case.get("input", "")
    title = problem.get("title", "this snippet")
    category = problem.get("category", "logic")

    statement = f"Debug the {problem['language']} snippet '{title}'. It should produce the expected output"
    if expected_output:
        compact_output = str(expected_output).replace("\n", ", ")
        statement += f" ({compact_output})"
    statement += f" for the given scenario and behave correctly for this {category} task."

    if sample_input:
        statement += f" Sample input/context: {sample_input}."

    return statement


def _with_problem_statement(problem: dict) -> dict:
    enriched = deepcopy(problem)
    enriched["problem_statement"] = _build_problem_statement(enriched)
    return enriched


def get_problem_by_id(problem_id: str) -> dict:
    for problem in ALL_SNIPPETS:
        if problem["id"] == problem_id:
            return _with_problem_statement(problem)
    raise KeyError("Problem not found.")


def get_public_problem_by_id(problem_id: str) -> dict:
    problem = get_problem_by_id(problem_id)
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


def get_matching_snippet(language: str, difficulty: str) -> dict:
    normalized_language = language.strip().lower()
    normalized_difficulty = difficulty.strip().lower()

    for problem in ALL_SNIPPETS:
        if (
            problem["language"].lower() == normalized_language
            and problem["difficulty"].lower() == normalized_difficulty
        ):
            return _with_problem_statement(problem)

    return _with_problem_statement(ALL_SNIPPETS[0])


def get_match_snippets(language: str, preferred_difficulty: str, round_count: int = 3) -> list[dict]:
    normalized_language = language.strip().lower()
    normalized_difficulty = preferred_difficulty.strip().lower()
    difficulty_order = ["easy", "medium", "hard"]

    matching_snippets = [
        _with_problem_statement(problem)
        for problem in ALL_SNIPPETS
        if problem["language"].strip().lower() == normalized_language
    ]

    if not matching_snippets:
        matching_snippets = [_with_problem_statement(problem) for problem in ALL_SNIPPETS]

    def sort_key(problem: dict) -> tuple[int, int, str]:
        difficulty = problem["difficulty"].strip().lower()
        preferred_rank = 0 if difficulty == normalized_difficulty else 1
        try:
            difficulty_rank = difficulty_order.index(difficulty)
        except ValueError:
            difficulty_rank = len(difficulty_order)
        return (preferred_rank, difficulty_rank, problem["id"])

    ordered_snippets = sorted(matching_snippets, key=sort_key)

    if len(ordered_snippets) > round_count:
        tail = ordered_snippets[1:]
        shuffle(tail)
        ordered_snippets = [ordered_snippets[0], *tail]

    return ordered_snippets[:round_count]


__all__ = [
    "ALL_SNIPPETS",
    "PROBLEMS",
    "get_match_snippets",
    "get_matching_snippet",
    "get_problem_by_id",
    "get_public_problem_by_id",
]

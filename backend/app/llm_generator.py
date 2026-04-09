"""LLM-powered problem generation using Google Gemini.

Generates unique debugging challenges at match start and provides
secondary submission verification when exact string matching fails.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any
from uuid import uuid4

from .config import hf_api_key

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory cache: avoids redundant API calls for same language/difficulty
# ---------------------------------------------------------------------------
_problem_cache: dict[str, list[list[dict[str, Any]]]] = {}
_MAX_CACHE_PER_KEY = 5

# Registry of all uniquely generated problems (for frontend /problem/id fetching)
_generated_registry: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_GENERATION_PROMPT = """You are an expert coding instructor creating debugging challenges for a competitive multiplayer debugging game called GLITCHLABS.

Generate {count} UNIQUE debugging problems in **{language}** at **{difficulty}** difficulty.

## Bug Difficulty Guidelines
- **Easy**: syntax errors (missing colons, semicolons, brackets), wrong variable names, typos in keywords, incorrect string formatting
- **Medium**: off-by-one errors, wrong comparison operators (< vs <=), incorrect loop bounds, state update ordering bugs, wrong arithmetic operators, missing break/return statements
- **Hard**: subtle logic errors, unhandled edge cases (empty input, negative numbers, overflow), wrong algorithm approach, incorrect recursion base cases, mutation bugs, floating point comparison issues

## Requirements for EACH problem
1. Write a short, self-contained code snippet (8-25 lines) with EXACTLY ONE intentional bug
2. The bug must be realistic — something a real student would accidentally write
3. The code must be plausible and look almost correct at first glance
4. The correct code should be the MINIMAL fix (change as few characters as possible)
5. Provide 1-2 test cases showing the difference between buggy and correct output
6. Provide 2-4 trace steps showing execution of the BUGGY code, with one step marked as suspicious
7. Each trace step must reference a valid line number from the buggy code (1-indexed)
8. The explanation must clearly identify the root cause of the bug

## Bug Types (use one per problem)
- `syntax_error` — missing/wrong syntax tokens
- `condition_issue` — wrong comparison or boolean logic
- `loop_issue` — wrong loop bounds, off-by-one, infinite loop
- `state_bug` — wrong variable initialization or update order
- `edge_case_issue` — fails on empty, negative, or boundary inputs
- `logic_issue` — fundamentally wrong approach to a sub-problem
- `type_error` — wrong type usage or missing type conversion

## Output Format
Return a JSON array of exactly {count} objects. Each object must have this EXACT structure:
```json
{{
    "language": "{language}",
    "difficulty": "{difficulty}",
    "category": "the bug_type value from above",
    "title": "A short, engaging name for the program itself (e.g. 'Fibonacci Generator', 'Login Validator')",
    "problem_statement": "A clear 1-2 sentence description of what the program is SUPPOSED to do if it was working correctly",
    "buggy_code": "the code WITH THE BUG INCLUDED. Do NOT put the fixed code here!",
    "correct_code": "the complete fixed code as a single string",
    "fixed_code": "same as correct_code",
    "bug_type": "one of the bug types listed above",
    "test_cases": [
        {{
            "input": "description of input or empty string if none",
            "expected_output": "what correct code produces",
            "actual_output": "what buggy code produces"
        }}
    ],
    "trace_steps": [
        {{
            "line": 1,
            "note": "What happens at this line during execution",
            "variables": {{"var_name": "value"}},
            "suspicious": false
        }},
        {{
            "line": 3,
            "note": "This is where the bug manifests",
            "variables": {{"var_name": "wrong_value"}},
            "suspicious": true
        }}
    ],
    "explanation": "Clear explanation of the bug and why the fix works"
}}
```

IMPORTANT:
- Return ONLY the JSON array, no markdown, no code fences, no extra text
- `fixed_code` must be identical to `correct_code`
- Exactly ONE trace step should have `"suspicious": true`
- Make each problem about a DIFFERENT topic (don't repeat similar problems)
- The buggy code and correct code must be complete, runnable snippets
"""

_VERIFY_PROMPT = """You are a code review expert. A student is trying to fix a bug in the following code.

## Original Buggy Code
```{language}
{buggy_code}
```

## Known Correct Fix
```{language}
{correct_code}
```

## Bug Description
{explanation}

## Student's Submission
```{language}
{submission}
```

Does the student's submission correctly fix the bug described above? The code must:
1. Fix the specific bug mentioned in the explanation
2. Produce the correct output for all test cases
3. Not introduce any new bugs

Reply with ONLY a JSON object: {{"correct": true}} or {{"correct": false, "reason": "brief explanation"}}
"""


def _get_client():
    from huggingface_hub import InferenceClient
    api_key = hf_api_key()
    if not api_key:
        raise RuntimeError("HF_TOKEN environment variable is not set")
    return InferenceClient("meta-llama/Llama-3.1-8B-Instruct", token=api_key)


def generate_match_problems(
    language: str,
    difficulty: str,
    count: int = 3,
) -> list[dict[str, Any]] | None:
    """Generate unique debugging problems using Gemini.

    Returns a list of problem dicts matching the hardcoded snippet format,
    or None if generation fails (caller should fall back to hardcoded snippets).
    """
    cache_key = f"{language.lower()}-{difficulty.lower()}"

    # Check cache first
    if cache_key in _problem_cache and _problem_cache[cache_key]:
        cached = _problem_cache[cache_key].pop(0)
        logger.info("Serving cached LLM problems for %s", cache_key)
        return cached

    try:
        client = _get_client()
        prompt = _GENERATION_PROMPT.format(
            count=count,
            language=language,
            difficulty=difficulty,
        )

        logger.info("Requesting %d %s/%s problems from HuggingFace...", count, language, difficulty)
        start_time = time.time()

        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.8,
        )

        elapsed = time.time() - start_time
        logger.info("HuggingFace responded in %.1fs", elapsed)

        raw_text = response.choices[0].message.content
        if not raw_text:
            logger.warning("HuggingFace returned empty response")
            return None

        # Strip markdown codeblocks if Llama included them
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        # Extremely basic auto-repair for cut-off JSON arrays
        if raw_text.startswith("[") and not raw_text.endswith("]"):
            # Truncate at the last valid complete object
            close_idx = raw_text.rfind("}")
            if close_idx != -1:
                raw_text = raw_text[:close_idx+1] + "]"

        try:
            problems = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.warning("HuggingFace returned invalid JSON: %s", raw_text)
            return None

        if not isinstance(problems, list) or len(problems) < 1:
            logger.warning("Gemini returned invalid format: expected list, got %s", type(problems))
            return None

        # Validate and enrich each problem
        validated = []
        for i, problem in enumerate(problems[:count]):
            enriched = _validate_and_enrich(problem, language, difficulty, i)
            if enriched:
                validated.append(enriched)

        if not validated:
            logger.warning("No valid problems after validation")
            return None

        logger.info("Successfully generated %d problems", len(validated))
        return validated

    except Exception:
        logger.exception("Failed to generate problems via Gemini")
        return None


def verify_submission(
    problem: dict[str, Any],
    submitted_code: str,
) -> bool | None:
    """Use Gemini to verify if a submission correctly fixes the bug.

    Returns True/False, or None if the verification itself fails.
    This is a fallback for when exact string matching fails.
    """
    try:
        client = _get_client()
        prompt = _VERIFY_PROMPT.format(
            language=problem.get("language", ""),
            buggy_code=problem.get("buggy_code", ""),
            correct_code=problem.get("correct_code", problem.get("fixed_code", "")),
            explanation=problem.get("explanation", ""),
            submission=submitted_code,
        )

        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.0,
        )

        raw_text = response.choices[0].message.content
        if not raw_text:
            return None

        # Clean JSON markdown blocks
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        print(f"[LLM VERIFY] Raw response: {raw_text}")

        import re
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            raw_text = match.group(0)

        try:
            result = json.loads(raw_text)
            correct_val = result.get("correct", False)
            if isinstance(correct_val, str):
                return correct_val.lower() == "true"
            return bool(correct_val)
        except json.JSONDecodeError:
            logger.warning("HuggingFace verify returned invalid JSON: %s", raw_text)
            return None

    except Exception:
        logger.exception("Failed to verify submission via Gemini")
        return None


def prefetch_problems(language: str, difficulty: str, count: int = 3) -> None:
    """Pre-generate and cache problems in the background.

    Called after serving a match to have problems ready for the next one.
    """
    cache_key = f"{language.lower()}-{difficulty.lower()}"

    if cache_key in _problem_cache and len(_problem_cache[cache_key]) >= _MAX_CACHE_PER_KEY:
        return

    problems = generate_match_problems(language, difficulty, count)
    if problems:
        _problem_cache.setdefault(cache_key, []).append(problems)
        logger.info("Prefetched problems cached for %s (total: %d sets)", cache_key, len(_problem_cache[cache_key]))


def _validate_and_enrich(
    problem: dict[str, Any],
    language: str,
    difficulty: str,
    index: int,
) -> dict[str, Any] | None:
    """Validate a generated problem and fill in any missing fields."""
    required_fields = ["buggy_code", "correct_code", "bug_type", "title"]
    for field_name in required_fields:
        if not problem.get(field_name):
            logger.warning("Problem %d missing required field: %s", index, field_name)
            return None

    problem_id = f"llm-{language.lower()[:2]}-{difficulty.lower()}-{uuid4().hex[:6]}"

    enriched = {
        "id": problem_id,
        "language": language,
        "difficulty": difficulty,
        "category": problem.get("category", problem.get("bug_type", "logic")),
        "title": problem["title"],
        "problem_statement": problem.get("problem_statement", f"Debug the {language} snippet '{problem['title']}'."),
        "buggy_code": problem["buggy_code"],
        "correct_code": problem["correct_code"],
        "fixed_code": problem.get("fixed_code", problem["correct_code"]),
        "code": problem["buggy_code"],
        "bug_type": problem["bug_type"],
        "test_cases": problem.get("test_cases", [{"input": "", "expected_output": "correct output", "actual_output": "buggy output"}]),
        "trace_steps": _validate_trace_steps(problem.get("trace_steps", [])),
        "explanation": problem.get("explanation", "Fix the bug in the code."),
        "_llm_generated": True,
    }
    
    _generated_registry[problem_id] = enriched
    return enriched


def _validate_trace_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ensure trace steps have the correct structure."""
    validated = []
    for step in steps:
        validated.append({
            "line": step.get("line", 1),
            "note": step.get("note", ""),
            "variables": step.get("variables", {}),
            "suspicious": step.get("suspicious", False),
        })

    # Ensure at least one suspicious step
    if validated and not any(step["suspicious"] for step in validated):
        validated[-1]["suspicious"] = True

    # If no steps at all, provide a minimal fallback
    if not validated:
        validated = [
            {"line": 1, "note": "Code execution begins.", "variables": {}, "suspicious": False},
            {"line": 2, "note": "A bug is present in the logic.", "variables": {}, "suspicious": True},
        ]

    return validated

def get_generated_problem(problem_id: str) -> dict[str, Any] | None:
    """Retrieve an LLM-generated problem by ID."""
    return _generated_registry.get(problem_id)

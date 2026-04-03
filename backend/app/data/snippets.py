from __future__ import annotations

from copy import deepcopy
from random import shuffle


def _problem(
    *,
    problem_id: str,
    language: str,
    difficulty: str,
    title: str,
    buggy_code: str,
    correct_code: str,
    bug_type: str,
    explanation: str,
    expected_output: str,
    actual_output: str,
    trace_steps: list[dict],
    category: str | None = None,
) -> dict:
    return {
        "id": problem_id,
        "language": language,
        "difficulty": difficulty,
        "category": category or bug_type.replace("_", " "),
        "title": title,
        "buggy_code": buggy_code,
        "correct_code": correct_code,
        "bug_type": bug_type,
        "test_cases": [
            {
                "input": "",
                "expected_output": expected_output,
                "actual_output": actual_output,
            }
        ],
        "explanation": explanation,
        "trace_steps": trace_steps,
        # Backward-compatible aliases for the lobby serializer and existing code.
        "code": buggy_code,
        "fixed_code": correct_code,
    }


PROBLEMS = [
    _problem(
        problem_id="py-easy-syntax-1",
        language="Python",
        difficulty="Easy",
        title="Loop Printer",
        buggy_code="""numbers = [1, 2, 3]

for number in numbers
    print(number)""",
        correct_code="""numbers = [1, 2, 3]

for number in numbers:
    print(number)""",
        bug_type="condition_issue",
        category="syntax",
        explanation="Python requires a colon after the `for` header. Without it, execution never reaches the loop body.",
        expected_output="1\n2\n3",
        actual_output="SyntaxError: expected ':'",
        trace_steps=[
            {"line": 1, "note": "The list is created successfully.", "variables": {"numbers": "[1, 2, 3]"}},
            {
                "line": 3,
                "note": "The parser stops here because the loop header is incomplete.",
                "variables": {"error": "missing ':'"},
                "suspicious": True,
            },
        ],
    ),
    _problem(
        problem_id="py-medium-off-by-one-1",
        language="Python",
        difficulty="Medium",
        title="Last Item Miss",
        buggy_code="""items = ["axe", "map", "torch"]

for index in range(len(items) - 1):
    print(items[index])""",
        correct_code="""items = ["axe", "map", "torch"]

for index in range(len(items)):
    print(items[index])""",
        bug_type="loop_issue",
        category="off-by-one",
        explanation="The loop stops one step too early. `range(len(items) - 1)` only visits indices 0 and 1, so the final item is skipped.",
        expected_output="axe\nmap\ntorch",
        actual_output="axe\nmap",
        trace_steps=[
            {"line": 1, "note": "Create the inventory list.", "variables": {"items": '["axe", "map", "torch"]'}},
            {"line": 3, "note": "The loop starts with `range(2)`.", "variables": {"index": 0, "len(items)": 3}},
            {"line": 4, "note": "First item is printed.", "variables": {"index": 0, 'items[index]': '"axe"', "output": '"axe"'}},
            {"line": 3, "note": "Second iteration begins.", "variables": {"index": 1}},
            {"line": 4, "note": "Second item is printed.", "variables": {"index": 1, 'items[index]': '"map"', "output": '"axe\\nmap"'}},
            {
                "line": 3,
                "note": "The loop exits before `index = 2`, so `torch` is never reached.",
                "variables": {"next_index": 2, "suspicion": "loop boundary"},
                "suspicious": True,
            },
        ],
    ),
    _problem(
        problem_id="py-hard-runtime-1",
        language="Python",
        difficulty="Hard",
        title="Safe Profile Access",
        buggy_code="""profile = {"name": "Ria", "skills": ["python", "fastapi"]}

print(profile["xp"])""",
        correct_code="""profile = {"name": "Ria", "skills": ["python", "fastapi"]}

print(profile.get("xp", 0))""",
        bug_type="edge_case_issue",
        category="runtime",
        explanation="The code assumes the `xp` key always exists. A guarded lookup handles the missing-key edge case safely.",
        expected_output="0",
        actual_output="KeyError: 'xp'",
        trace_steps=[
            {"line": 1, "note": "Build the profile dictionary.", "variables": {"profile": '{"name": "Ria", "skills": ["python", "fastapi"]}'}},
            {
                "line": 3,
                "note": "Direct dictionary access fails because `xp` is missing.",
                "variables": {"lookup_key": '"xp"', "error": "KeyError"},
                "suspicious": True,
            },
        ],
    ),
    _problem(
        problem_id="java-easy-syntax-1",
        language="Java",
        difficulty="Easy",
        title="Missing Semicolon",
        buggy_code="""public class Main {
    public static void main(String[] args) {
        int score = 10
        System.out.println(score);
    }
}""",
        correct_code="""public class Main {
    public static void main(String[] args) {
        int score = 10;
        System.out.println(score);
    }
}""",
        bug_type="condition_issue",
        category="syntax",
        explanation="The assignment statement is missing a semicolon, so compilation fails before the program can run.",
        expected_output="10",
        actual_output="Compilation error near `int score = 10`",
        trace_steps=[
            {"line": 3, "note": "The compiler expects the statement to terminate.", "variables": {"score": 10}},
            {"line": 3, "note": "Missing semicolon prevents execution.", "variables": {"error": "expected ';'"},"suspicious": True},
        ],
    ),
    _problem(
        problem_id="java-medium-logic-1",
        language="Java",
        difficulty="Medium",
        title="Max Finder",
        buggy_code="""public class Main {
    public static void main(String[] args) {
        int[] scores = {72, 88, 91, 67};
        int highest = 0;

        for (int score : scores) {
            if (score < highest) {
                highest = score;
            }
        }

        System.out.println(highest);
    }
}""",
        correct_code="""public class Main {
    public static void main(String[] args) {
        int[] scores = {72, 88, 91, 67};
        int highest = 0;

        for (int score : scores) {
            if (score > highest) {
                highest = score;
            }
        }

        System.out.println(highest);
    }
}""",
        bug_type="condition_issue",
        category="logic",
        explanation="The comparison is reversed. The program only updates `highest` when a score is smaller than the current best, so it never captures the maximum.",
        expected_output="91",
        actual_output="0",
        trace_steps=[
            {"line": 3, "note": "The score array is initialized.", "variables": {"scores": "{72, 88, 91, 67}"}},
            {"line": 4, "note": "Start with `highest = 0`.", "variables": {"highest": 0}},
            {"line": 6, "note": "First loop value arrives.", "variables": {"score": 72, "highest": 0}},
            {
                "line": 7,
                "note": "The condition `72 < 0` is false, so `highest` never updates.",
                "variables": {"comparison": "72 < 0", "highest": 0},
                "suspicious": True,
            },
        ],
    ),
    _problem(
        problem_id="java-hard-runtime-1",
        language="Java",
        difficulty="Hard",
        title="String Length Guard",
        buggy_code="""public class Main {
    public static void main(String[] args) {
        String name = null;
        System.out.println(name.length());
    }
}""",
        correct_code="""public class Main {
    public static void main(String[] args) {
        String name = null;
        System.out.println(name == null ? 0 : name.length());
    }
}""",
        bug_type="edge_case_issue",
        category="runtime",
        explanation="`name` can be null, so calling `.length()` directly crashes. Guarding the null case preserves execution.",
        expected_output="0",
        actual_output="NullPointerException",
        trace_steps=[
            {"line": 3, "note": "The string reference is null.", "variables": {"name": "null"}},
            {"line": 4, "note": "Calling `.length()` on null throws immediately.", "variables": {"error": "NullPointerException"}, "suspicious": True},
        ],
    ),
    _problem(
        problem_id="c-easy-syntax-1",
        language="C",
        difficulty="Easy",
        title="Printf Semicolon",
        buggy_code="""#include <stdio.h>

int main() {
    printf("Hello, BugBattle!")
    return 0;
}""",
        correct_code="""#include <stdio.h>

int main() {
    printf("Hello, BugBattle!");
    return 0;
}""",
        bug_type="condition_issue",
        category="syntax",
        explanation="The `printf` statement is missing its terminating semicolon, so the program fails to compile.",
        expected_output="Hello, BugBattle!",
        actual_output="Compilation error after `printf`",
        trace_steps=[
            {"line": 4, "note": "The compiler parses the print call.", "variables": {"call": 'printf("Hello, BugBattle!")'}},
            {"line": 4, "note": "Missing semicolon stops compilation.", "variables": {"error": "expected ';'"},"suspicious": True},
        ],
    ),
    _problem(
        problem_id="c-medium-off-by-one-1",
        language="C",
        difficulty="Medium",
        title="Array Walk",
        buggy_code="""#include <stdio.h>

int main() {
    int nums[4] = {3, 5, 8, 13};

    for (int i = 0; i <= 4; i++) {
        printf("%d\\n", nums[i]);
    }

    return 0;
}""",
        correct_code="""#include <stdio.h>

int main() {
    int nums[4] = {3, 5, 8, 13};

    for (int i = 0; i < 4; i++) {
        printf("%d\\n", nums[i]);
    }

    return 0;
}""",
        bug_type="loop_issue",
        category="off-by-one",
        explanation="The loop allows `i` to become 4, but the last valid array index is 3. That extra iteration reads past the array boundary.",
        expected_output="3\n5\n8\n13",
        actual_output="3\n5\n8\n13\n(undefined read)",
        trace_steps=[
            {"line": 4, "note": "Initialize the array.", "variables": {"nums": "{3, 5, 8, 13}"}},
            {"line": 6, "note": "Loop reaches the final safe value.", "variables": {"i": 3, "nums[i]": 13}},
            {
                "line": 6,
                "note": "The condition still allows `i = 4`, which is outside the array.",
                "variables": {"i": 4, "max_index": 3},
                "suspicious": True,
            },
        ],
    ),
    _problem(
        problem_id="c-hard-logic-1",
        language="C",
        difficulty="Hard",
        title="Pass Rule",
        buggy_code="""#include <stdio.h>

int main() {
    int score = 84;

    if (score <= 50) {
        printf("Pass\\n");
    } else {
        printf("Fail\\n");
    }

    return 0;
}""",
        correct_code="""#include <stdio.h>

int main() {
    int score = 84;

    if (score >= 50) {
        printf("Pass\\n");
    } else {
        printf("Fail\\n");
    }

    return 0;
}""",
        bug_type="condition_issue",
        category="logic",
        explanation="The pass condition is flipped. Scores above 50 should pass, but the current branch treats them as failures.",
        expected_output="Pass",
        actual_output="Fail",
        trace_steps=[
            {"line": 4, "note": "The score is assigned.", "variables": {"score": 84}},
            {
                "line": 6,
                "note": "The comparison `84 <= 50` is false, so execution falls into the wrong branch.",
                "variables": {"comparison": "84 <= 50", "branch": "else"},
                "suspicious": True,
            },
        ],
    ),
    _problem(
        problem_id="cpp-easy-syntax-1",
        language="C++",
        difficulty="Easy",
        title="Missing Include Namespace",
        buggy_code="""#include <iostream>

int main() {
    cout << "BugBattle" << std::endl;
    return 0;
}""",
        correct_code="""#include <iostream>

int main() {
    std::cout << "BugBattle" << std::endl;
    return 0;
}""",
        bug_type="state_bug",
        category="syntax",
        explanation="`cout` lives inside the `std` namespace. Without `std::`, the symbol lookup fails at compile time.",
        expected_output="BugBattle",
        actual_output="Compilation error: `cout` was not declared",
        trace_steps=[
            {"line": 4, "note": "The compiler looks up `cout`.", "variables": {"symbol": "cout"}},
            {"line": 4, "note": "Namespace qualifier is missing.", "variables": {"error": "undeclared identifier"}, "suspicious": True},
        ],
    ),
    _problem(
        problem_id="cpp-medium-runtime-1",
        language="C++",
        difficulty="Medium",
        title="Pointer Guard",
        buggy_code="""#include <iostream>

int main() {
    int* value = nullptr;
    std::cout << *value << std::endl;
    return 0;
}""",
        correct_code="""#include <iostream>

int main() {
    int* value = nullptr;
    if (value != nullptr) {
        std::cout << *value << std::endl;
    }
    return 0;
}""",
        bug_type="edge_case_issue",
        category="runtime",
        explanation="The pointer can be null, so dereferencing it is unsafe. Guarding the pointer avoids undefined behavior.",
        expected_output="(no output)",
        actual_output="Segmentation fault / crash",
        trace_steps=[
            {"line": 4, "note": "The pointer is explicitly null.", "variables": {"value": "nullptr"}},
            {"line": 5, "note": "Dereferencing `nullptr` causes a crash.", "variables": {"operation": "*value", "error": "invalid access"}, "suspicious": True},
        ],
    ),
    _problem(
        problem_id="cpp-hard-off-by-one-1",
        language="C++",
        difficulty="Hard",
        title="Vector Loop",
        buggy_code="""#include <iostream>
#include <vector>

int main() {
    std::vector<int> levels = {3, 5, 8, 13};

    for (int i = 0; i <= levels.size(); i++) {
        std::cout << levels[i] << std::endl;
    }

    return 0;
}""",
        correct_code="""#include <iostream>
#include <vector>

int main() {
    std::vector<int> levels = {3, 5, 8, 13};

    for (int i = 0; i < levels.size(); i++) {
        std::cout << levels[i] << std::endl;
    }

    return 0;
}""",
        bug_type="loop_issue",
        category="off-by-one",
        explanation="`i <= levels.size()` allows one extra iteration, so the code reads `levels[4]` even though the last valid index is 3.",
        expected_output="3\n5\n8\n13",
        actual_output="3\n5\n8\n13\n(undefined read)",
        trace_steps=[
            {"line": 5, "note": "Create the vector with four values.", "variables": {"levels.size()": 4}},
            {"line": 7, "note": "Normal iteration reaches `i = 3` safely.", "variables": {"i": 3, "levels[i]": 13}},
            {"line": 7, "note": "The condition still passes for `i = 4`, which is out of bounds.", "variables": {"i": 4, "max_index": 3}, "suspicious": True},
        ],
    ),
]


def get_problem_by_id(problem_id: str) -> dict:
    for problem in PROBLEMS:
        if problem["id"] == problem_id:
            return deepcopy(problem)
    raise KeyError("Problem not found.")


def get_matching_snippet(language: str, difficulty: str) -> dict:
    normalized_language = language.strip().lower()
    normalized_difficulty = difficulty.strip().lower()

    for problem in PROBLEMS:
        if (
            problem["language"].lower() == normalized_language
            and problem["difficulty"].lower() == normalized_difficulty
        ):
            return deepcopy(problem)

    return deepcopy(PROBLEMS[0])


def get_match_snippets(language: str, preferred_difficulty: str, round_count: int = 3) -> list[dict]:
    normalized_language = language.strip().lower()
    normalized_difficulty = preferred_difficulty.strip().lower()
    difficulty_order = ["easy", "medium", "hard"]

    matching_snippets = [
        deepcopy(problem)
        for problem in PROBLEMS
        if problem["language"].strip().lower() == normalized_language
    ]

    if not matching_snippets:
        matching_snippets = [deepcopy(problem) for problem in PROBLEMS]

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

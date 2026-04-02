from __future__ import annotations

from random import shuffle


SNIPPETS = [
    {
        "id": "py-easy-syntax-1",
        "language": "Python",
        "difficulty": "Easy",
        "category": "syntax",
        "title": "Loop Printer",
        "code": """numbers = [1, 2, 3]

for number in numbers
    print(number)""",
        "fixed_code": """numbers = [1, 2, 3]

for number in numbers:
    print(number)""",
    },
    {
        "id": "py-medium-off-by-one-1",
        "language": "Python",
        "difficulty": "Medium",
        "category": "off-by-one",
        "title": "Last Item Miss",
        "code": """items = ["axe", "map", "torch"]

for index in range(len(items) - 1):
    print(items[index])""",
        "fixed_code": """items = ["axe", "map", "torch"]

for index in range(len(items)):
    print(items[index])""",
    },
    {
        "id": "py-hard-runtime-1",
        "language": "Python",
        "difficulty": "Hard",
        "category": "runtime",
        "title": "Safe Profile Access",
        "code": """profile = {"name": "Ria", "skills": ["python", "fastapi"]}

print(profile["xp"])""",
        "fixed_code": """profile = {"name": "Ria", "skills": ["python", "fastapi"]}

print(profile.get("xp", 0))""",
    },
    {
        "id": "java-easy-syntax-1",
        "language": "Java",
        "difficulty": "Easy",
        "category": "syntax",
        "title": "Missing Semicolon",
        "code": """public class Main {
    public static void main(String[] args) {
        int score = 10
        System.out.println(score);
    }
}""",
        "fixed_code": """public class Main {
    public static void main(String[] args) {
        int score = 10;
        System.out.println(score);
    }
}""",
    },
    {
        "id": "java-medium-logic-1",
        "language": "Java",
        "difficulty": "Medium",
        "category": "logic",
        "title": "Max Finder",
        "code": """public class Main {
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
        "fixed_code": """public class Main {
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
    },
    {
        "id": "java-hard-runtime-1",
        "language": "Java",
        "difficulty": "Hard",
        "category": "runtime",
        "title": "String Length Guard",
        "code": """public class Main {
    public static void main(String[] args) {
        String name = null;
        System.out.println(name.length());
    }
}""",
        "fixed_code": """public class Main {
    public static void main(String[] args) {
        String name = null;
        System.out.println(name == null ? 0 : name.length());
    }
}""",
    },
    {
        "id": "c-easy-syntax-1",
        "language": "C",
        "difficulty": "Easy",
        "category": "syntax",
        "title": "Printf Semicolon",
        "code": """#include <stdio.h>

int main() {
    printf("Hello, BugBattle!")
    return 0;
}""",
        "fixed_code": """#include <stdio.h>

int main() {
    printf("Hello, BugBattle!");
    return 0;
}""",
    },
    {
        "id": "c-medium-off-by-one-1",
        "language": "C",
        "difficulty": "Medium",
        "category": "off-by-one",
        "title": "Array Walk",
        "code": """#include <stdio.h>

int main() {
    int nums[4] = {3, 5, 8, 13};

    for (int i = 0; i <= 4; i++) {
        printf("%d\\n", nums[i]);
    }

    return 0;
}""",
        "fixed_code": """#include <stdio.h>

int main() {
    int nums[4] = {3, 5, 8, 13};

    for (int i = 0; i < 4; i++) {
        printf("%d\\n", nums[i]);
    }

    return 0;
}""",
    },
    {
        "id": "c-hard-logic-1",
        "language": "C",
        "difficulty": "Hard",
        "category": "logic",
        "title": "Pass Rule",
        "code": """#include <stdio.h>

int main() {
    int score = 84;

    if (score <= 50) {
        printf("Pass\\n");
    } else {
        printf("Fail\\n");
    }

    return 0;
}""",
        "fixed_code": """#include <stdio.h>

int main() {
    int score = 84;

    if (score >= 50) {
        printf("Pass\\n");
    } else {
        printf("Fail\\n");
    }

    return 0;
}""",
    },
    {
        "id": "cpp-easy-syntax-1",
        "language": "C++",
        "difficulty": "Easy",
        "category": "syntax",
        "title": "Missing Include Namespace",
        "code": """#include <iostream>

int main() {
    cout << "BugBattle" << std::endl;
    return 0;
}""",
        "fixed_code": """#include <iostream>

int main() {
    std::cout << "BugBattle" << std::endl;
    return 0;
}""",
    },
    {
        "id": "cpp-medium-runtime-1",
        "language": "C++",
        "difficulty": "Medium",
        "category": "runtime",
        "title": "Pointer Guard",
        "code": """#include <iostream>

int main() {
    int* value = nullptr;
    std::cout << *value << std::endl;
    return 0;
}""",
        "fixed_code": """#include <iostream>

int main() {
    int* value = nullptr;
    if (value != nullptr) {
        std::cout << *value << std::endl;
    }
    return 0;
}""",
    },
    {
        "id": "cpp-hard-off-by-one-1",
        "language": "C++",
        "difficulty": "Hard",
        "category": "off-by-one",
        "title": "Vector Loop",
        "code": """#include <iostream>
#include <vector>

int main() {
    std::vector<int> levels = {3, 5, 8, 13};

    for (int i = 0; i <= levels.size(); i++) {
        std::cout << levels[i] << std::endl;
    }

    return 0;
}""",
        "fixed_code": """#include <iostream>
#include <vector>

int main() {
    std::vector<int> levels = {3, 5, 8, 13};

    for (int i = 0; i < levels.size(); i++) {
        std::cout << levels[i] << std::endl;
    }

    return 0;
}""",
    },
]


def get_matching_snippet(language: str, difficulty: str) -> dict:
    normalized_language = language.strip().lower()
    normalized_difficulty = difficulty.strip().lower()

    for snippet in SNIPPETS:
        if (
            snippet["language"].lower() == normalized_language
            and snippet["difficulty"].lower() == normalized_difficulty
        ):
            return snippet

    return SNIPPETS[0]


def get_match_snippets(language: str, preferred_difficulty: str, round_count: int = 3) -> list[dict]:
    normalized_language = language.strip().lower()
    normalized_difficulty = preferred_difficulty.strip().lower()
    difficulty_order = ["easy", "medium", "hard"]

    matching_snippets = [
        snippet for snippet in SNIPPETS if snippet["language"].strip().lower() == normalized_language
    ]

    if not matching_snippets:
        matching_snippets = SNIPPETS[:]

    def sort_key(snippet: dict) -> tuple[int, int, str]:
        difficulty = snippet["difficulty"].strip().lower()
        preferred_rank = 0 if difficulty == normalized_difficulty else 1
        try:
            difficulty_rank = difficulty_order.index(difficulty)
        except ValueError:
            difficulty_rank = len(difficulty_order)
        return (preferred_rank, difficulty_rank, snippet["id"])

    ordered_snippets = sorted(matching_snippets, key=sort_key)

    if len(ordered_snippets) > round_count:
        tail = ordered_snippets[1:]
        shuffle(tail)
        ordered_snippets = [ordered_snippets[0], *tail]

    return ordered_snippets[:round_count]

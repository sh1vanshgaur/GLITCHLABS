export const HYPOTHESIS_OPTIONS = [
  {
    value: "loop_issue",
    label: "Loop issue",
    description: "Off-by-one, wrong iteration bounds, or a loop skipping the right data."
  },
  {
    value: "condition_issue",
    label: "Condition issue",
    description: "An `if` or `else` branch is using the wrong comparison or operator."
  },
  {
    value: "edge_case_issue",
    label: "Edge case issue",
    description: "The code breaks on empty input, boundaries, or missing values."
  },
  {
    value: "state_bug",
    label: "State bug",
    description: "A variable update or stored value drifts away from the intended state."
  },
  {
    value: "performance_issue",
    label: "Performance issue",
    description: "The logic works, but it does unnecessary work or scales poorly."
  }
];

export const DEBUG_PROBLEMS = [
  {
    id: "py-medium-off-by-one-1",
    title: "Last Item Miss",
    language: "Python",
    difficulty: "Medium",
    buggy_code: `items = ["axe", "map", "torch"]

for index in range(len(items) - 1):
    print(items[index])`,
    correct_code: `items = ["axe", "map", "torch"]

for index in range(len(items)):
    print(items[index])`,
    bug_type: "loop_issue",
    test_cases: [
      {
        input: `items = ["axe", "map", "torch"]`,
        expected_output: "axe\nmap\ntorch",
        actual_output: "axe\nmap"
      }
    ],
    explanation:
      "The loop stops one index too early, so the last item is never printed. The range should cover the full length of the array.",
    trace_steps: [
      {
        line: 1,
        note: "Initialize the list with three items.",
        variables: {
          items: '["axe", "map", "torch"]'
        }
      },
      {
        line: 3,
        note: "Start the loop. `range(len(items) - 1)` becomes `range(2)`.",
        variables: {
          index: 0,
          "len(items)": 3
        }
      },
      {
        line: 4,
        note: "First iteration prints the first value.",
        variables: {
          index: 0,
          'items[index]': '"axe"',
          output: '"axe"'
        }
      },
      {
        line: 3,
        note: "Second iteration begins.",
        variables: {
          index: 1,
          "len(items)": 3
        }
      },
      {
        line: 4,
        note: "Second iteration prints the second value.",
        variables: {
          index: 1,
          'items[index]': '"map"',
          output: '"axe\\nmap"'
        }
      },
      {
        line: 3,
        note: "Loop ends before `index = 2`, so `torch` is skipped.",
        variables: {
          next_index: 2,
          suspicious: "Loop boundary stops too soon."
        },
        suspicious: true
      }
    ]
  }
];

export function getDebugProblem(problemId) {
  return DEBUG_PROBLEMS.find((problem) => problem.id === problemId) ?? DEBUG_PROBLEMS[0];
}

export function getHypothesisLabel(value) {
  return HYPOTHESIS_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

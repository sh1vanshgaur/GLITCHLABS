SNIPPETS = [{'id': 'py-easy-syntax-1',
  'language': 'Python',
  'difficulty': 'Easy',
  'category': 'syntax',
  'title': 'Loop Printer',
  'problem_statement': None,
  'buggy_code': 'numbers = [1, 2, 3]\n\nfor number in numbers\n    print(number)',
  'correct_code': 'numbers = [1, 2, 3]\n\nfor number in numbers:\n    print(number)',
  'bug_type': 'condition_issue',
  'test_cases': [{'input': '', 'expected_output': '1\n2\n3', 'actual_output': "SyntaxError: expected ':'"}],
  'explanation': 'Python requires a colon after the `for` header. Without it, execution never reaches the loop body.',
  'trace_steps': [{'line': 1, 'note': 'The list is created successfully.', 'variables': {'numbers': '[1, 2, 3]'}},
                  {'line': 3,
                   'note': 'The parser stops here because the loop header is incomplete.',
                   'variables': {'error': "missing ':'"},
                   'suspicious': True}],
  'code': 'numbers = [1, 2, 3]\n\nfor number in numbers\n    print(number)',
  'fixed_code': 'numbers = [1, 2, 3]\n\nfor number in numbers:\n    print(number)'},
 {'id': 'py-medium-off-by-one-1',
  'language': 'Python',
  'difficulty': 'Medium',
  'category': 'off-by-one',
  'title': 'Last Item Miss',
  'problem_statement': None,
  'buggy_code': 'items = ["axe", "map", "torch"]\n\nfor index in range(len(items) - 1):\n    print(items[index])',
  'correct_code': 'items = ["axe", "map", "torch"]\n\nfor index in range(len(items)):\n    print(items[index])',
  'bug_type': 'loop_issue',
  'test_cases': [{'input': '', 'expected_output': 'axe\nmap\ntorch', 'actual_output': 'axe\nmap'}],
  'explanation': 'The loop stops one step too early. `range(len(items) - 1)` only visits indices 0 and 1, so the final item is skipped.',
  'trace_steps': [{'line': 1, 'note': 'Create the inventory list.', 'variables': {'items': '["axe", "map", "torch"]'}},
                  {'line': 3, 'note': 'The loop starts with `range(2)`.', 'variables': {'index': 0, 'len(items)': 3}},
                  {'line': 4,
                   'note': 'First item is printed.',
                   'variables': {'index': 0, 'items[index]': '"axe"', 'output': '"axe"'}},
                  {'line': 3, 'note': 'Second iteration begins.', 'variables': {'index': 1}},
                  {'line': 4,
                   'note': 'Second item is printed.',
                   'variables': {'index': 1, 'items[index]': '"map"', 'output': '"axe\\nmap"'}},
                  {'line': 3,
                   'note': 'The loop exits before `index = 2`, so `torch` is never reached.',
                   'variables': {'next_index': 2, 'suspicion': 'loop boundary'},
                   'suspicious': True}],
  'code': 'items = ["axe", "map", "torch"]\n\nfor index in range(len(items) - 1):\n    print(items[index])',
  'fixed_code': 'items = ["axe", "map", "torch"]\n\nfor index in range(len(items)):\n    print(items[index])'},
 {'id': 'java-medium-logic-1',
  'language': 'Java',
  'difficulty': 'Medium',
  'category': 'logic',
  'title': 'Max Finder',
  'problem_statement': None,
  'buggy_code': 'public class Main {\n'
                '    public static void main(String[] args) {\n'
                '        int[] scores = {72, 88, 91, 67};\n'
                '        int highest = 0;\n'
                '\n'
                '        for (int score : scores) {\n'
                '            if (score < highest) {\n'
                '                highest = score;\n'
                '            }\n'
                '        }\n'
                '\n'
                '        System.out.println(highest);\n'
                '    }\n'
                '}',
  'correct_code': 'public class Main {\n'
                  '    public static void main(String[] args) {\n'
                  '        int[] scores = {72, 88, 91, 67};\n'
                  '        int highest = 0;\n'
                  '\n'
                  '        for (int score : scores) {\n'
                  '            if (score > highest) {\n'
                  '                highest = score;\n'
                  '            }\n'
                  '        }\n'
                  '\n'
                  '        System.out.println(highest);\n'
                  '    }\n'
                  '}',
  'bug_type': 'condition_issue',
  'test_cases': [{'input': '', 'expected_output': '91', 'actual_output': '0'}],
  'explanation': 'The comparison is reversed. The program only updates `highest` when a score is smaller than the current best, so it never captures the maximum.',
  'trace_steps': [{'line': 3, 'note': 'The score array is initialized.', 'variables': {'scores': '{72, 88, 91, 67}'}},
                  {'line': 4, 'note': 'Start with `highest = 0`.', 'variables': {'highest': 0}},
                  {'line': 6, 'note': 'First loop value arrives.', 'variables': {'score': 72, 'highest': 0}},
                  {'line': 7,
                   'note': 'The condition `72 < 0` is false, so `highest` never updates.',
                   'variables': {'comparison': '72 < 0', 'highest': 0},
                   'suspicious': True}],
  'code': 'public class Main {\n'
          '    public static void main(String[] args) {\n'
          '        int[] scores = {72, 88, 91, 67};\n'
          '        int highest = 0;\n'
          '\n'
          '        for (int score : scores) {\n'
          '            if (score < highest) {\n'
          '                highest = score;\n'
          '            }\n'
          '        }\n'
          '\n'
          '        System.out.println(highest);\n'
          '    }\n'
          '}',
  'fixed_code': 'public class Main {\n'
                '    public static void main(String[] args) {\n'
                '        int[] scores = {72, 88, 91, 67};\n'
                '        int highest = 0;\n'
                '\n'
                '        for (int score : scores) {\n'
                '            if (score > highest) {\n'
                '                highest = score;\n'
                '            }\n'
                '        }\n'
                '\n'
                '        System.out.println(highest);\n'
                '    }\n'
                '}'},
 {'id': 'c-medium-off-by-one-1',
  'language': 'C',
  'difficulty': 'Medium',
  'category': 'off-by-one',
  'title': 'Array Walk',
  'problem_statement': None,
  'buggy_code': '#include <stdio.h>\n'
                '\n'
                'int main() {\n'
                '    int nums[4] = {3, 5, 8, 13};\n'
                '\n'
                '    for (int i = 0; i <= 4; i++) {\n'
                '        printf("%d\\n", nums[i]);\n'
                '    }\n'
                '\n'
                '    return 0;\n'
                '}',
  'correct_code': '#include <stdio.h>\n'
                  '\n'
                  'int main() {\n'
                  '    int nums[4] = {3, 5, 8, 13};\n'
                  '\n'
                  '    for (int i = 0; i < 4; i++) {\n'
                  '        printf("%d\\n", nums[i]);\n'
                  '    }\n'
                  '\n'
                  '    return 0;\n'
                  '}',
  'bug_type': 'loop_issue',
  'test_cases': [{'input': '', 'expected_output': '3\n5\n8\n13', 'actual_output': '3\n5\n8\n13\n(undefined read)'}],
  'explanation': 'The loop allows `i` to become 4, but the last valid array index is 3. That extra iteration reads past the array boundary.',
  'trace_steps': [{'line': 4, 'note': 'Initialize the array.', 'variables': {'nums': '{3, 5, 8, 13}'}},
                  {'line': 6, 'note': 'Loop reaches the final safe value.', 'variables': {'i': 3, 'nums[i]': 13}},
                  {'line': 6,
                   'note': 'The condition still allows `i = 4`, which is outside the array.',
                   'variables': {'i': 4, 'max_index': 3},
                   'suspicious': True}],
  'code': '#include <stdio.h>\n'
          '\n'
          'int main() {\n'
          '    int nums[4] = {3, 5, 8, 13};\n'
          '\n'
          '    for (int i = 0; i <= 4; i++) {\n'
          '        printf("%d\\n", nums[i]);\n'
          '    }\n'
          '\n'
          '    return 0;\n'
          '}',
  'fixed_code': '#include <stdio.h>\n'
                '\n'
                'int main() {\n'
                '    int nums[4] = {3, 5, 8, 13};\n'
                '\n'
                '    for (int i = 0; i < 4; i++) {\n'
                '        printf("%d\\n", nums[i]);\n'
                '    }\n'
                '\n'
                '    return 0;\n'
                '}'},
 {'id': 'cpp-hard-off-by-one-1',
  'language': 'C++',
  'difficulty': 'Hard',
  'category': 'off-by-one',
  'title': 'Vector Loop',
  'problem_statement': None,
  'buggy_code': '#include <iostream>\n'
                '#include <vector>\n'
                '\n'
                'int main() {\n'
                '    std::vector<int> levels = {3, 5, 8, 13};\n'
                '\n'
                '    for (int i = 0; i <= levels.size(); i++) {\n'
                '        std::cout << levels[i] << std::endl;\n'
                '    }\n'
                '\n'
                '    return 0;\n'
                '}',
  'correct_code': '#include <iostream>\n'
                  '#include <vector>\n'
                  '\n'
                  'int main() {\n'
                  '    std::vector<int> levels = {3, 5, 8, 13};\n'
                  '\n'
                  '    for (int i = 0; i < levels.size(); i++) {\n'
                  '        std::cout << levels[i] << std::endl;\n'
                  '    }\n'
                  '\n'
                  '    return 0;\n'
                  '}',
  'bug_type': 'loop_issue',
  'test_cases': [{'input': '', 'expected_output': '3\n5\n8\n13', 'actual_output': '3\n5\n8\n13\n(undefined read)'}],
  'explanation': '`i <= levels.size()` allows one extra iteration, so the code reads `levels[4]` even though the last valid index is 3.',
  'trace_steps': [{'line': 5, 'note': 'Create the vector with four values.', 'variables': {'levels.size()': 4}},
                  {'line': 7,
                   'note': 'Normal iteration reaches `i = 3` safely.',
                   'variables': {'i': 3, 'levels[i]': 13}},
                  {'line': 7,
                   'note': 'The condition still passes for `i = 4`, which is out of bounds.',
                   'variables': {'i': 4, 'max_index': 3},
                   'suspicious': True}],
  'code': '#include <iostream>\n'
          '#include <vector>\n'
          '\n'
          'int main() {\n'
          '    std::vector<int> levels = {3, 5, 8, 13};\n'
          '\n'
          '    for (int i = 0; i <= levels.size(); i++) {\n'
          '        std::cout << levels[i] << std::endl;\n'
          '    }\n'
          '\n'
          '    return 0;\n'
          '}',
  'fixed_code': '#include <iostream>\n'
                '#include <vector>\n'
                '\n'
                'int main() {\n'
                '    std::vector<int> levels = {3, 5, 8, 13};\n'
                '\n'
                '    for (int i = 0; i < levels.size(); i++) {\n'
                '        std::cout << levels[i] << std::endl;\n'
                '    }\n'
                '\n'
                '    return 0;\n'
                '}'},
 {'id': 'py-easy-arrays-1',
  'language': 'Python',
  'difficulty': 'Easy',
  'category': 'arrays',
  'title': 'Negative Max Tracker',
  'problem_statement': 'Print the maximum score from the list. The list may contain only negative numbers, so the running state must be initialized carefully.',
  'buggy_code': 'scores = [-5, -2, -9]\n'
                '\n'
                'best = 0\n'
                'for score in scores:\n'
                '    if score > best:\n'
                '        best = score\n'
                '\n'
                'print(best)',
  'correct_code': 'scores = [-5, -2, -9]\n'
                  '\n'
                  'best = scores[0]\n'
                  'for score in scores:\n'
                  '    if score > best:\n'
                  '        best = score\n'
                  '\n'
                  'print(best)',
  'bug_type': 'edge_case_issue',
  'test_cases': [{'input': 'scores = [-5, -2, -9]', 'expected_output': '-2', 'actual_output': '0'},
                 {'input': 'scores = [4, 1, 7]', 'expected_output': '7', 'actual_output': '7'}],
  'explanation': 'The code assumes the maximum should start at `0`. That works only when at least one non-negative number exists. For all-negative arrays, the state never updates to the real maximum.',
  'trace_steps': [{'line': 1,
                   'note': 'The array is loaded with only negative values.',
                   'variables': {'scores': '[-5, -2, -9]'}},
                  {'line': 3,
                   'note': 'The running maximum starts at `0`, which is not in the array.',
                   'variables': {'best': 0},
                   'suspicious': True},
                  {'line': 4,
                   'note': 'Every comparison fails because each score is smaller than `0`.',
                   'variables': {'score': -2, 'best': 0}},
                  {'line': 7,
                   'note': 'The final answer still reflects the bad initial state.',
                   'variables': {'printed': 0}}],
  'code': 'scores = [-5, -2, -9]\n'
          '\n'
          'best = 0\n'
          'for score in scores:\n'
          '    if score > best:\n'
          '        best = score\n'
          '\n'
          'print(best)',
  'fixed_code': 'scores = [-5, -2, -9]\n'
                '\n'
                'best = scores[0]\n'
                'for score in scores:\n'
                '    if score > best:\n'
                '        best = score\n'
                '\n'
                'print(best)'},
 {'id': 'py-medium-arrays-1',
  'language': 'Python',
  'difficulty': 'Medium',
  'category': 'arrays',
  'title': 'Shifted Prefix Average',
  'problem_statement': 'Build and print the running floor-average after each number arrives. The bug is a state-update ordering mistake students often make in prefix calculations.',
  'buggy_code': 'nums = [4, 8, 6, 2]\n'
                '\n'
                'total = 0\n'
                'averages = []\n'
                '\n'
                'for index in range(len(nums)):\n'
                '    averages.append(total // (index + 1))\n'
                '    total += nums[index]\n'
                '\n'
                'print(averages)',
  'correct_code': 'nums = [4, 8, 6, 2]\n'
                  '\n'
                  'total = 0\n'
                  'averages = []\n'
                  '\n'
                  'for index in range(len(nums)):\n'
                  '    total += nums[index]\n'
                  '    averages.append(total // (index + 1))\n'
                  '\n'
                  'print(averages)',
  'bug_type': 'state_bug',
  'test_cases': [{'input': 'nums = [4, 8, 6, 2]', 'expected_output': '[4, 6, 6, 5]', 'actual_output': '[0, 2, 4, 4]'},
                 {'input': 'nums = [5, 5]', 'expected_output': '[5, 5]', 'actual_output': '[0, 2]'}],
  'explanation': 'The average is recorded before the current number is added into the running total. That shifts every prefix result one step behind.',
  'trace_steps': [{'line': 3, 'note': 'The running sum starts at zero.', 'variables': {'total': 0}},
                  {'line': 6,
                   'note': 'At index `0`, the code divides the stale total before adding `4`.',
                   'variables': {'index': 0, 'total': 0},
                   'suspicious': True},
                  {'line': 7,
                   'note': 'Only after storing the wrong average does the sum catch up.',
                   'variables': {'total_after_update': 4}},
                  {'line': 9,
                   'note': 'Every later prefix is shifted by the same ordering bug.',
                   'variables': {'averages': '[0, 2, 4, 4]'}}],
  'code': 'nums = [4, 8, 6, 2]\n'
          '\n'
          'total = 0\n'
          'averages = []\n'
          '\n'
          'for index in range(len(nums)):\n'
          '    averages.append(total // (index + 1))\n'
          '    total += nums[index]\n'
          '\n'
          'print(averages)',
  'fixed_code': 'nums = [4, 8, 6, 2]\n'
                '\n'
                'total = 0\n'
                'averages = []\n'
                '\n'
                'for index in range(len(nums)):\n'
                '    total += nums[index]\n'
                '    averages.append(total // (index + 1))\n'
                '\n'
                'print(averages)'}]

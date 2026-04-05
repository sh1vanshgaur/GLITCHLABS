SNIPPETS = [{'id': 'java-easy-syntax-1',
  'language': 'Java',
  'difficulty': 'Easy',
  'category': 'syntax',
  'title': 'Missing Semicolon',
  'problem_statement': None,
  'buggy_code': 'public class Main {\n'
                '    public static void main(String[] args) {\n'
                '        int score = 10\n'
                '        System.out.println(score);\n'
                '    }\n'
                '}',
  'correct_code': 'public class Main {\n'
                  '    public static void main(String[] args) {\n'
                  '        int score = 10;\n'
                  '        System.out.println(score);\n'
                  '    }\n'
                  '}',
  'bug_type': 'condition_issue',
  'test_cases': [{'input': '', 'expected_output': '10', 'actual_output': 'Compilation error near `int score = 10`'}],
  'explanation': 'The assignment statement is missing a semicolon, so compilation fails before the program can run.',
  'trace_steps': [{'line': 3, 'note': 'The compiler expects the statement to terminate.', 'variables': {'score': 10}},
                  {'line': 3,
                   'note': 'Missing semicolon prevents execution.',
                   'variables': {'error': "expected ';'"},
                   'suspicious': True}],
  'code': 'public class Main {\n'
          '    public static void main(String[] args) {\n'
          '        int score = 10\n'
          '        System.out.println(score);\n'
          '    }\n'
          '}',
  'fixed_code': 'public class Main {\n'
                '    public static void main(String[] args) {\n'
                '        int score = 10;\n'
                '        System.out.println(score);\n'
                '    }\n'
                '}'},
 {'id': 'java-hard-runtime-1',
  'language': 'Java',
  'difficulty': 'Hard',
  'category': 'runtime',
  'title': 'String Length Guard',
  'problem_statement': None,
  'buggy_code': 'public class Main {\n'
                '    public static void main(String[] args) {\n'
                '        String name = null;\n'
                '        System.out.println(name.length());\n'
                '    }\n'
                '}',
  'correct_code': 'public class Main {\n'
                  '    public static void main(String[] args) {\n'
                  '        String name = null;\n'
                  '        System.out.println(name == null ? 0 : name.length());\n'
                  '    }\n'
                  '}',
  'bug_type': 'edge_case_issue',
  'test_cases': [{'input': '', 'expected_output': '0', 'actual_output': 'NullPointerException'}],
  'explanation': '`name` can be null, so calling `.length()` directly crashes. Guarding the null case preserves execution.',
  'trace_steps': [{'line': 3, 'note': 'The string reference is null.', 'variables': {'name': 'null'}},
                  {'line': 4,
                   'note': 'Calling `.length()` on null throws immediately.',
                   'variables': {'error': 'NullPointerException'},
                   'suspicious': True}],
  'code': 'public class Main {\n'
          '    public static void main(String[] args) {\n'
          '        String name = null;\n'
          '        System.out.println(name.length());\n'
          '    }\n'
          '}',
  'fixed_code': 'public class Main {\n'
                '    public static void main(String[] args) {\n'
                '        String name = null;\n'
                '        System.out.println(name == null ? 0 : name.length());\n'
                '    }\n'
                '}'},
 {'id': 'c-easy-syntax-1',
  'language': 'C',
  'difficulty': 'Easy',
  'category': 'syntax',
  'title': 'Printf Semicolon',
  'problem_statement': None,
  'buggy_code': '#include <stdio.h>\n\nint main() {\n    printf("Hello, BugBattle!")\n    return 0;\n}',
  'correct_code': '#include <stdio.h>\n\nint main() {\n    printf("Hello, BugBattle!");\n    return 0;\n}',
  'bug_type': 'condition_issue',
  'test_cases': [{'input': '', 'expected_output': 'Hello, BugBattle!', 'actual_output': 'Compilation error after `printf`'}],
  'explanation': 'The `printf` statement is missing its terminating semicolon, so the program fails to compile.',
  'trace_steps': [{'line': 4, 'note': 'The compiler parses the print call.', 'variables': {'call': 'printf("Hello, BugBattle!")'}},
                  {'line': 4,
                   'note': 'Missing semicolon stops compilation.',
                   'variables': {'error': "expected ';'"},
                   'suspicious': True}],
  'code': '#include <stdio.h>\n\nint main() {\n    printf("Hello, BugBattle!")\n    return 0;\n}',
  'fixed_code': '#include <stdio.h>\n\nint main() {\n    printf("Hello, BugBattle!");\n    return 0;\n}'},
 {'id': 'cpp-easy-syntax-1',
  'language': 'C++',
  'difficulty': 'Easy',
  'category': 'syntax',
  'title': 'Missing Include Namespace',
  'problem_statement': None,
  'buggy_code': '#include <iostream>\n\nint main() {\n    cout << "BugBattle" << std::endl;\n    return 0;\n}',
  'correct_code': '#include <iostream>\n\nint main() {\n    std::cout << "BugBattle" << std::endl;\n    return 0;\n}',
  'bug_type': 'state_bug',
  'test_cases': [{'input': '', 'expected_output': 'BugBattle', 'actual_output': 'Compilation error: `cout` was not declared'}],
  'explanation': '`cout` lives inside the `std` namespace. Without `std::`, the symbol lookup fails at compile time.',
  'trace_steps': [{'line': 4, 'note': 'The compiler looks up `cout`.', 'variables': {'symbol': 'cout'}},
                  {'line': 4,
                   'note': 'Namespace qualifier is missing.',
                   'variables': {'error': 'undeclared identifier'},
                   'suspicious': True}],
  'code': '#include <iostream>\n\nint main() {\n    cout << "BugBattle" << std::endl;\n    return 0;\n}',
  'fixed_code': '#include <iostream>\n\nint main() {\n    std::cout << "BugBattle" << std::endl;\n    return 0;\n}'},
 {'id': 'java-easy-strings-1',
  'language': 'Java',
  'difficulty': 'Easy',
  'category': 'strings',
  'title': 'Duplicate Letter Cleaner',
  'problem_statement': 'Remove consecutive duplicate characters from the string and print the cleaned result. This is a small string-state debugging question, not a new algorithm.',
  'buggy_code': 'public class Main {\n'
                '    public static void main(String[] args) {\n'
                '        String text = "baalloon";\n'
                '        StringBuilder cleaned = new StringBuilder();\n'
                '        cleaned.append(text.charAt(0));\n'
                '\n'
                '        for (int i = 1; i < text.length(); i++) {\n'
                '            if (text.charAt(i) == text.charAt(i - 1)) {\n'
                '                cleaned.append(text.charAt(i));\n'
                '            }\n'
                '        }\n'
                '\n'
                '        System.out.println(cleaned.toString());\n'
                '    }\n'
                '}',
  'correct_code': 'public class Main {\n'
                  '    public static void main(String[] args) {\n'
                  '        String text = "baalloon";\n'
                  '        StringBuilder cleaned = new StringBuilder();\n'
                  '        cleaned.append(text.charAt(0));\n'
                  '\n'
                  '        for (int i = 1; i < text.length(); i++) {\n'
                  '            if (text.charAt(i) != text.charAt(i - 1)) {\n'
                  '                cleaned.append(text.charAt(i));\n'
                  '            }\n'
                  '        }\n'
                  '\n'
                  '        System.out.println(cleaned.toString());\n'
                  '    }\n'
                  '}',
  'bug_type': 'condition_issue',
  'test_cases': [{'input': 'text = "baalloon"', 'expected_output': 'balon', 'actual_output': 'bao'},
                 {'input': 'text = "miss"', 'expected_output': 'mis', 'actual_output': 'ms'}],
  'explanation': 'The branch is reversed. The code appends repeated letters instead of appending letters only when the current character changes.',
  'trace_steps': [{'line': 3, 'note': 'The first character is seeded correctly.', 'variables': {'cleaned': '"b"'}},
                  {'line': 7,
                   'note': 'At the first repeated `a`, the condition passes and appends a duplicate instead of skipping it.',
                   'variables': {'current': "'a'", 'previous': "'a'"},
                   'suspicious': True},
                  {'line': 12,
                   'note': 'Only repeated runs survive, so unique transitions are lost.',
                   'variables': {'printed': '"bao"'}}],
  'code': 'public class Main {\n'
          '    public static void main(String[] args) {\n'
          '        String text = "baalloon";\n'
          '        StringBuilder cleaned = new StringBuilder();\n'
          '        cleaned.append(text.charAt(0));\n'
          '\n'
          '        for (int i = 1; i < text.length(); i++) {\n'
          '            if (text.charAt(i) == text.charAt(i - 1)) {\n'
          '                cleaned.append(text.charAt(i));\n'
          '            }\n'
          '        }\n'
          '\n'
          '        System.out.println(cleaned.toString());\n'
          '    }\n'
          '}',
  'fixed_code': 'public class Main {\n'
                '    public static void main(String[] args) {\n'
                '        String text = "baalloon";\n'
                '        StringBuilder cleaned = new StringBuilder();\n'
                '        cleaned.append(text.charAt(0));\n'
                '\n'
                '        for (int i = 1; i < text.length(); i++) {\n'
                '            if (text.charAt(i) != text.charAt(i - 1)) {\n'
                '                cleaned.append(text.charAt(i));\n'
                '            }\n'
                '        }\n'
                '\n'
                '        System.out.println(cleaned.toString());\n'
                '    }\n'
                '}'},
 {'id': 'java-medium-strings-1',
  'language': 'Java',
  'difficulty': 'Medium',
  'category': 'strings',
  'title': 'Missing Final Run',
  'problem_statement': 'Run-length encode the string by printing each character followed by its count. The bug is a classic end-of-loop omission.',
  'buggy_code': 'public class Main {\n'
                '    public static void main(String[] args) {\n'
                '        String text = "aaabbc";\n'
                '        StringBuilder encoded = new StringBuilder();\n'
                '        int count = 1;\n'
                '\n'
                '        for (int i = 1; i < text.length(); i++) {\n'
                '            if (text.charAt(i) == text.charAt(i - 1)) {\n'
                '                count++;\n'
                '            } else {\n'
                '                encoded.append(text.charAt(i - 1)).append(count);\n'
                '                count = 1;\n'
                '            }\n'
                '        }\n'
                '\n'
                '        System.out.println(encoded.toString());\n'
                '    }\n'
                '}',
  'correct_code': 'public class Main {\n'
                  '    public static void main(String[] args) {\n'
                  '        String text = "aaabbc";\n'
                  '        StringBuilder encoded = new StringBuilder();\n'
                  '        int count = 1;\n'
                  '\n'
                  '        for (int i = 1; i < text.length(); i++) {\n'
                  '            if (text.charAt(i) == text.charAt(i - 1)) {\n'
                  '                count++;\n'
                  '            } else {\n'
                  '                encoded.append(text.charAt(i - 1)).append(count);\n'
                  '                count = 1;\n'
                  '            }\n'
                  '        }\n'
                  '\n'
                  '        encoded.append(text.charAt(text.length() - 1)).append(count);\n'
                  '        System.out.println(encoded.toString());\n'
                  '    }\n'
                  '}',
  'bug_type': 'edge_case_issue',
  'test_cases': [{'input': 'text = "aaabbc"', 'expected_output': 'a3b2c1', 'actual_output': 'a3b2'},
                 {'input': 'text = "zz"', 'expected_output': 'z2', 'actual_output': ''}],
  'explanation': 'The loop only appends a run when it sees a change. The final run never sees a following change, so it is silently dropped.',
  'trace_steps': [{'line': 5, 'note': 'The count begins at one for the first character.', 'variables': {'count': 1}},
                  {'line': 9,
                   'note': 'When the loop reaches `c`, no later character forces its run to flush.',
                   'variables': {'last_char': "'c'", 'count': 1},
                   'suspicious': True},
                  {'line': 15,
                   'note': 'The encoded string is printed before the final run is appended.',
                   'variables': {'printed': '"a3b2"'}}],
  'code': 'public class Main {\n'
          '    public static void main(String[] args) {\n'
          '        String text = "aaabbc";\n'
          '        StringBuilder encoded = new StringBuilder();\n'
          '        int count = 1;\n'
          '\n'
          '        for (int i = 1; i < text.length(); i++) {\n'
          '            if (text.charAt(i) == text.charAt(i - 1)) {\n'
          '                count++;\n'
          '            } else {\n'
          '                encoded.append(text.charAt(i - 1)).append(count);\n'
          '                count = 1;\n'
          '            }\n'
          '        }\n'
          '\n'
          '        System.out.println(encoded.toString());\n'
          '    }\n'
          '}',
  'fixed_code': 'public class Main {\n'
                '    public static void main(String[] args) {\n'
                '        String text = "aaabbc";\n'
                '        StringBuilder encoded = new StringBuilder();\n'
                '        int count = 1;\n'
                '\n'
                '        for (int i = 1; i < text.length(); i++) {\n'
                '            if (text.charAt(i) == text.charAt(i - 1)) {\n'
                '                count++;\n'
                '            } else {\n'
                '                encoded.append(text.charAt(i - 1)).append(count);\n'
                '                count = 1;\n'
                '            }\n'
                '        }\n'
                '\n'
                '        encoded.append(text.charAt(text.length() - 1)).append(count);\n'
                '        System.out.println(encoded.toString());\n'
                '    }\n'
                '}'}]

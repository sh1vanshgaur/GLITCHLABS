export const GAME_STAGES = {
  LOBBY: "lobby",
  COUNTDOWN: "countdown",
  ACTIVE: "active",
  RESULTS: "results"
};

export const DEFAULT_LOBBY_STATE = {
  code: "GLTCH",
  stage: GAME_STAGES.LOBBY,
  host: "Player One",
  winner: "ByteBandit",
  winnerAnswer: "The loop never reaches the last item because the range ends too early.",
  players: [
    { id: "p1", name: "Player One", score: 2, isHost: true },
    { id: "p2", name: "ByteBandit", score: 1, isHost: false },
    { id: "p3", name: "NullNomad", score: 0, isHost: false }
  ],
  languageVotes: {
    Python: 2,
    JavaScript: 1
  },
  difficultyVotes: {
    Easy: 1,
    Medium: 2,
    Hard: 0
  }
};

const snippets = [
  {
    id: "py-easy-off-by-one",
    language: "Python",
    difficulty: "Easy",
    category: "Off-by-one",
    title: "Score Summation",
    code: `scores = [8, 12, 15, 20]
total = 0

for index in range(len(scores) - 1):
    total += scores[index]

print(total)`,
    acceptedAnswers: ["last item", "range(len(scores) - 1)", "off by one"],
    explanation:
      "The loop stops before the final score, so the last element is never added. It should iterate through the full list."
  },
  {
    id: "js-medium-logic",
    language: "JavaScript",
    difficulty: "Medium",
    category: "Logic",
    title: "Access Gate",
    code: `function canEnter(age, hasTicket) {
  if (age >= 18 || hasTicket) {
    return true;
  }

  return false;
}

console.log(canEnter(16, true));`,
    acceptedAnswers: ["should be &&", "or should be and", "logic"],
    explanation:
      "The condition uses OR, allowing underage users in with only a ticket. If both conditions are required, the operator should be AND."
  },
  {
    id: "py-hard-runtime",
    language: "Python",
    difficulty: "Hard",
    category: "Runtime",
    title: "Profile Loader",
    code: `profile = {"name": "Aarav", "skills": ["python", "api"]}

print(profile["experience"])`,
    acceptedAnswers: ["keyerror", "experience key", "missing key"],
    explanation:
      "The dictionary has no 'experience' key, so direct access raises a KeyError at runtime."
  },
  {
    id: "js-hard-syntax",
    language: "JavaScript",
    difficulty: "Hard",
    category: "Syntax",
    title: "Leaderboard Formatter",
    code: `const winners = ["Mira", "Jay", "Noah"];

for (let i = 0; i < winners.length; i++) {
  console.log(winners[i]);
}`,
    acceptedAnswers: ["missing )", "syntax", "closing parenthesis"],
    explanation:
      "The for-loop declaration is missing the closing parenthesis before the opening brace, which causes a syntax error."
  },
  {
    id: "js-easy-runtime",
    language: "JavaScript",
    difficulty: "Easy",
    category: "Runtime",
    title: "Inventory Count",
    code: `const items = null;
console.log(items.length);`,
    acceptedAnswers: ["null", "cannot read", "runtime"],
    explanation:
      "The code tries to access .length on null, which throws a runtime TypeError."
  },
  {
    id: "py-medium-syntax",
    language: "Python",
    difficulty: "Medium",
    category: "Syntax",
    title: "Pending Tasks",
    code: `tasks = ["tests", "docs", "deploy"]

for task in tasks
    print(task)`,
    acceptedAnswers: ["missing colon", "syntax", "for task in tasks"],
    explanation:
      "The for statement is missing a colon, so Python raises a syntax error before execution."
  }
];

export function sampleSnippet(language, difficulty) {
  const exactMatch = snippets.find(
    (snippet) => snippet.language === language && snippet.difficulty === difficulty
  );

  return exactMatch ?? snippets[0];
}

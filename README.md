# GLITCHLABS

GLITCHLABS is a real-time debugging game where players enter a lobby, receive the same broken snippet, and work through a guided debugging flow before submitting a fix.

The current version is no longer just a simple "find the right code" race. It now supports a structured learning flow with:

- problem statements
- sample behavior
- hypothesis checking
- execution tracing
- edit submission tracking
- per-step progress feedback
- multi-round match flow

## What The Project Solves

Most coding platforms train writing from scratch. GLITCHLABS focuses on debugging, which is a more realistic day-to-day engineering skill.

Students are expected to:

1. understand what the code is supposed to do
2. identify what behavior is wrong
3. trace the bug step by step
4. submit a fix
5. explain the root cause

## Current Product Scope

### Lobby And Match Features

- Create and join lobbies with a short room code
- Solo play is allowed
- Multiplayer play is supported in the same lobby
- Host-controlled round start
- Language and difficulty voting
- Shared countdown before each round
- Best-of-3 style multi-round flow inside a single match
- Replay to the next problem or return to lobby after the final round
- Live lobby sync through WebSockets

### Debugging Flow Features

- Step 1: Hypothesis
- Step 2: Trace
- Step 3: Edit
- Step 4: Result

The round UI now includes:

- a clear problem statement
- observed behavior vs expected behavior
- a behavior insight layer
- sample input/context when available
- a persistent round progress tracker
- step states that reflect correctness, not only navigation

### Submission And Result Behavior

- Hypothesis correctness is checked and preserved visually in the step tracker
- Trace is treated as a neutral progression step
- Edit submissions are recorded even when logically wrong
- Wrong edit submissions do not send the player back to hypothesis
- Result state preserves what happened during the round truthfully
- Final results can distinguish:
  - correct submission
  - submitted but incorrect
  - no submission

## Supported Challenge Types

### Languages

- Python
- Java
- C
- C++

### Difficulty Levels

- Easy
- Medium
- Hard

### Categories In Dataset

- syntax
- logic
- runtime
- off-by-one
- binary search
- hashing
- recursion
- sliding window
- stack/queue
- arrays
- strings
- dp

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI
- Realtime: WebSockets
- State: in-memory + JSON persistence
- Data: curated local snippet dataset

## Repository Structure

```text
minor project/
├── backend/
│   ├── app/
│   │   ├── data/
│   │   │   └── snippets/
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── config.py
│   │   ├── game_state.py
│   │   ├── main.py
│   │   └── storage.py
│   ├── runtime/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## How A Round Works

1. A player creates a lobby and becomes host.
2. Players optionally vote on language and difficulty.
3. The host starts the match.
4. The game enters a short shared countdown.
5. Everyone receives the same debugging problem.
6. The player reads the problem statement and behavior mismatch.
7. The player locks a bug hypothesis.
8. The player steps through trace mode.
9. The player edits and submits a fix.
10. The app records the submission and preserves its correctness state.
11. The result step and final results show what happened in the round.

## Learning-Oriented UI Notes

The current debugging screen is designed to reduce guessing.

Instead of only showing buggy code and raw output, it now includes:

- `problem_statement`
- sample expected behavior
- behavior insight text
- a visible trace-mode guidance callout
- a persistent progress sidebar on desktop

The step sidebar supports:

- `completed-success`
- `completed-failed`
- `completed-neutral`
- `current`
- `pending`
- `upcoming`

This means the flow tells a truthful story of player performance instead of marking every past step as simply "done."

## Backend API Overview

### Utility Endpoints

- `GET /health`
- `GET /questions`
- `GET /problem/{problem_id}`

### Single-Problem Debugging Endpoints

- `POST /submit-hypothesis`
- `POST /run-trace`
- `POST /submit-solution`

### Lobby / Match Endpoints

- `POST /api/lobbies`
- `POST /api/lobbies/join`
- `POST /api/lobbies/{lobby_code}/vote`
- `POST /api/lobbies/{lobby_code}/start`
- `POST /api/lobbies/{lobby_code}/submit`
- `POST /api/lobbies/{lobby_code}/explain`
- `POST /api/lobbies/{lobby_code}/replay`
- `WS /ws/lobbies/{lobby_code}`

### Example: Questions Endpoint

`GET /questions` returns a compact list like:

```json
[
  { "id": "py-easy-syntax-1", "title": "Loop Printer" },
  { "id": "py-medium-off-by-one-1", "title": "Last Item Miss" }
]
```

## Run Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend default URL:

- [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL:

- [http://127.0.0.1:5173](http://127.0.0.1:5173)

## Environment Notes

### Backend

- `GLITCHLABS_ALLOWED_ORIGINS`
- `GLITCHLABS_STATE_FILE`

### Frontend

- `VITE_API_BASE_URL`
- `VITE_WS_BASE_URL`

If these are not set, the frontend defaults to the same hostname on port `8000` for API and WebSocket communication.

## Current Verification Status

Recently verified in this codebase:

- backend Python modules compile successfully
- frontend production build succeeds with `npm run build`
- solo start works
- multi-round submission reset works
- second-round stale submission bug was fixed
- `/questions` endpoint returns the expected list shape

## Important Design Decisions

- No full auth system yet; sessions are lightweight and local-friendly
- No database yet; current persistence uses a JSON state file
- Snippets are curated for deterministic checking and trace design
- Real-time sync is used only where lobby/match state needs it
- The app remains a single-page frontend for faster iteration

## Known Limitations

- Temporary WebSocket disconnect handling is still a weak area
- Exact code checking is strict and still has room for smarter normalization
- Incorrect edit submissions are recorded once per round and then locked
- The dataset is curated, so content breadth is still limited

## Future Improvements

- More snippet packs and categories
- Better reconnect handling for multiplayer sessions
- More flexible accepted solution matching
- Richer round analytics and scoreboard history
- Host moderation controls
- Persistent user profiles and match history
- Public deployment with a proper database

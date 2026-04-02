# BugBattle

BugBattle is a multiplayer debugging game where players in the same lobby race to fix a bug in a shared code snippet.

## Problem Statement

Debugging is a critical real-world programming skill, but most learning platforms focus more on code writing than bug fixing. This project gamifies debugging to make practice engaging, competitive, and measurable.

## What This MVP Includes

- Landing page with a strong game identity
- Create lobby and join lobby using a short room code
- Real-time lobby sync with WebSockets
- Connected players list
- Host-controlled round start
- Player voting for language and difficulty
- Shared countdown before the round begins
- One curated buggy snippet shown to all players
- Round timer
- Editable code submission flow
- First correct fix wins
- Results screen with winner, winning fix, reference fix, and scoreboard
- Replay in the same lobby

## Supported Challenge Types

- Languages: Python, Java, C, C++
- Difficulty: Easy, Medium, Hard
- Bug categories: syntax, logic, runtime, off-by-one

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI
- Realtime: WebSockets
- State: In-memory lobby/game state
- Data: Curated local snippet pool

## Design Direction

BugBattle uses a dark UI with a clean "VS Code meets indie game" feel. The visuals lean into a poster-like title treatment, glowing accents, editorial composition, and readable code panels so the interface feels playful but still practical for debugging.

## Folder Structure

```text
minor project/
├── backend/
│   ├── app/
│   │   ├── data/
│   │   │   └── snippets.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── game_state.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── hooks/
│   │   │   └── useLobbyGame.js
│   │   ├── lib/
│   │   │   └── utils.js
│   │   ├── styles/
│   │   │   └── global.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## How The Game Works

1. A player creates a lobby and becomes the host.
2. Other players join using the lobby code.
3. Players vote on language and difficulty.
4. The host starts the round.
5. The server begins a synchronized countdown.
6. All players receive the same buggy code snippet.
7. Players inspect the snippet, edit the code, and submit their fix.
8. The first correct fix ends the round and awards a point.
9. Everyone sees the results screen, winning code, reference fix, and updated scoreboard.
10. The host can replay another round in the same lobby.

## Run Locally

### 1. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs on [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 2. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on [http://127.0.0.1:5173](http://127.0.0.1:5173)

## Verified During Build

- Python backend modules compile successfully
- FastAPI endpoints for create, join, vote, and start round were smoke-tested with `TestClient`
- Frontend production build succeeds with `npm run build`

## Strong Sensible Decisions

- No authentication system was added to keep setup fast and local-friendly
- No database was added because in-memory state is enough for an MVP demo
- Curated snippets were used instead of live AI generation for reliability and exact fix checking
- WebSockets are used only where real-time sync matters, keeping the architecture small
- The frontend is a single-page flow instead of a multi-route app to reduce complexity

## Future Scope

- Multiple rounds with best-of-three match flow
- More snippet packs and bug categories
- More snippet packs and additional accepted fix variants
- Host controls for kicking players and locking votes
- Persistent scoreboard and match history
- Public deployment with a lightweight database

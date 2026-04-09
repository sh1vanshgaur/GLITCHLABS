import { useEffect, useMemo, useState } from "react";
import DebugFlowManager from "./components/DebugFlowManager";
import { useLobbyGame } from "./hooks/useLobbyGame";
import { formatSeconds } from "./lib/utils";

const languages = ["Python", "Java", "C", "C++"];
const difficulties = ["Easy", "Medium", "Hard"];

const mascotPalette = ["#00ff41", "#00f0ff", "#ff00ff", "#ffb800", "#ff3e3e", "#7b61ff", "#00ffa3", "#ff6090"];

const infoCards = [
  {
    icon: "$>",
    title: "About",
    content: "GLITCHLABS is a multiplayer debugging game where everyone gets the same broken snippet and races to submit the correct fix."
  },
  {
    icon: "//",
    title: "Why GLITCHLABS?",
    content: "It turns bug fixing into a fast social challenge, helping players practice logic, speed, and clean debugging under pressure."
  },
  {
    icon: ">>",
    title: "How to play",
    content: "Enter a name, join a room, vote for language and difficulty, then fix the buggy code before anyone else."
  }
];

export default function App() {
  const {
    state,
    status,
    error,
    submissionFeedback,
    currentPlayer,
    createLobby,
    joinLobby,
    vote,
    startRound,
    submitAnswer,
    submitExplanation,
    replayRound
  } = useLobbyGame();

  const [playerName, setPlayerName] = useState("quantum");
  const [joinCode, setJoinCode] = useState("GLTCH");
  const [editedCode, setEditedCode] = useState("");
  const [voteLanguage, setVoteLanguage] = useState("Python");
  const [voteDifficulty, setVoteDifficulty] = useState("Easy");
  const [activeSnippetId, setActiveSnippetId] = useState(null);
  const [selectedAvatarColor, setSelectedAvatarColor] = useState(mascotPalette[5]);

  const currentSnippet = useMemo(() => state.snippet, [state.snippet]);
  const isLandingLike = state.stage === "landing" || state.stage === "lobby";

  useEffect(() => {
    if (state.stage === "active" && currentSnippet && currentSnippet.id !== activeSnippetId) {
      setEditedCode(currentSnippet.code);
      setActiveSnippetId(currentSnippet.id);
    }

    if (state.stage !== "active") {
      setActiveSnippetId(null);
    }
  }, [activeSnippetId, currentSnippet, state.stage]);

  async function handleCreateLobby() {
    try {
      await createLobby(playerName || "Host");
    } catch {
      // Hook already stores displayable errors.
    }
  }

  async function handleJoinLobby() {
    try {
      await joinLobby(playerName || "Player", joinCode || "GLTCH");
    } catch {
      // Hook already stores displayable errors.
    }
  }

  async function handleVote(language, difficulty) {
    setVoteLanguage(language);
    setVoteDifficulty(difficulty);

    try {
      await vote(language, difficulty);
    } catch {
      // Hook already stores displayable errors.
    }
  }

  async function handleStartRound() {
    try {
      await vote(voteLanguage, voteDifficulty);
      await startRound();
      setEditedCode("");
    } catch {
      // Hook already stores displayable errors.
    }
  }

  async function handleSubmitAnswer(codeToSubmit) {
    if (!codeToSubmit.trim()) {
      return null;
    }

    try {
      return await submitAnswer(codeToSubmit);
    } catch {
      // Hook already stores displayable errors.
      return null;
    }
  }

  async function handleSaveExplanation(explanation) {
    if (!explanation.trim()) {
      return null;
    }

    return await submitExplanation(explanation);
  }

  async function handleReplayRound() {
    try {
      await replayRound();
      setEditedCode("");
    } catch {
      // Hook already stores displayable errors.
    }
  }

  return (
    <div className="app-shell">
      <BackgroundLayer />
      <div className="page-wrap">
        <header className="hero-header">
          <div className="logo-wrap">
            <div className="logo-mark" data-text="GLITCHLABS" aria-hidden="true">
              GLITCHLABS<span className="logo-cursor">_</span>
            </div>
            <p className="logo-subtitle">debug // compete // conquer</p>
          </div>
        </header>

        {isLandingLike ? (
          <main>
            <section className="landing-stage">
              <div className={`play-card ${state.stage === "lobby" ? "play-card--lobby" : ""}`}>
                <div className={`play-card__body ${state.stage === "lobby" ? "play-card__body--lobby" : ""}`}>
                  <div className="play-card__main">
                    <div className={`play-card__top ${state.stage === "lobby" ? "play-card__top--lobby" : ""}`}>
                      <div className="field-group">
                        <label className="field-label" htmlFor="player-name">Your name</label>
                        <input
                          className="arcade-input"
                          id="player-name"
                          maxLength={20}
                          onChange={(event) => setPlayerName(event.target.value)}
                          placeholder="enter name"
                          value={playerName}
                        />
                      </div>
                      <div className="field-group">
                        <label className="field-label" htmlFor="language-select">Language</label>
                        <select
                          className="arcade-select"
                          id="language-select"
                          onChange={(event) => handleVote(event.target.value, voteDifficulty)}
                          value={voteLanguage}
                        >
                          {languages.map((language) => (
                            <option key={language} value={language}>
                              {language}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div className="mascot-stage">
                      <div className="terminal-bar">
                        <span className="terminal-dot terminal-dot--red" />
                        <span className="terminal-dot terminal-dot--yellow" />
                        <span className="terminal-dot terminal-dot--green" />
                        <span style={{ marginLeft: '0.5rem' }}>status.exe</span>
                      </div>
                      <FaceStage avatarColor={selectedAvatarColor} stage={state.stage} status={status} />
                      <AvatarColorPicker
                        colors={mascotPalette}
                        selectedColor={selectedAvatarColor}
                        onSelectColor={setSelectedAvatarColor}
                      />
                      <div className="status-badge">{status}</div>
                    </div>

                    <div className="action-stack">
                      <p className="helper-copy">Create a room and share the code with your friends.</p>
                      <button className="arcade-button arcade-button--primary" onClick={handleCreateLobby} type="button">
                        Create Room
                      </button>
                      <p className="helper-copy">Joining a friend? Type their room code below, then join.</p>
                      <button className="arcade-button arcade-button--secondary" onClick={handleJoinLobby} type="button">
                        Join Room
                      </button>
                    </div>

                    <div className="lobby-tools">
                      <div className="field-group">
                        <label className="field-label" htmlFor="room-code">Room code</label>
                        <input
                          className="arcade-input arcade-input--code"
                          id="room-code"
                          maxLength={5}
                          onChange={(event) => setJoinCode(event.target.value.toUpperCase())}
                          placeholder="ENTER CODE"
                          value={joinCode}
                        />
                      </div>
                      <div className="difficulty-row">
                        {difficulties.map((difficulty) => (
                          <button
                            className={`chip-button ${voteDifficulty === difficulty ? "chip-button--active" : ""}`}
                            key={difficulty}
                            onClick={() => handleVote(voteLanguage, difficulty)}
                            type="button"
                          >
                            {difficulty}
                          </button>
                        ))}
                      </div>
                    </div>

                    {error ? <p className="feedback-strip feedback-strip--error">{error}</p> : null}
                  </div>

                  {state.stage === "lobby" ? (
                    <LobbyPanel
                      currentPlayer={currentPlayer}
                      lobbyState={state}
                      onStartRound={handleStartRound}
                      onVoteChange={handleVote}
                      voteDifficulty={voteDifficulty}
                      voteLanguage={voteLanguage}
                    />
                  ) : null}
                </div>
              </div>
            </section>

            <section className="info-grid">
              {infoCards.map((card) => (
                <article className="info-panel" key={card.title}>
                  <div className="info-panel__icon">{card.icon}</div>
                  <h2>{card.title}</h2>
                  <p>{card.content}</p>
                </article>
              ))}
            </section>
          </main>
        ) : null}

        {state.stage === "countdown" ? (
          <CountdownScreen
            countdown={state.countdownRemaining}
            currentRound={state.currentRound}
            lobbyCode={state.code}
            totalRounds={state.totalRounds}
          />
        ) : null}

        {state.stage === "active" && currentSnippet ? (
          <GameScreen
            editedCode={editedCode}
            onCodeChange={setEditedCode}
            onSaveExplanation={handleSaveExplanation}
            onSubmitAnswer={handleSubmitAnswer}
            currentRound={state.currentRound}
            roundTimer={state.roundRemaining}
            submissionFeedback={submissionFeedback}
            snippet={currentSnippet}
            totalRounds={state.totalRounds}
          />
        ) : null}

        {state.stage === "results" && currentSnippet ? (
          <ResultsScreen currentPlayer={currentPlayer} lobbyState={state} onReplayRound={handleReplayRound} snippet={currentSnippet} />
        ) : null}
      </div>
    </div>
  );
}

function BackgroundLayer() {
  return (
    <div className="bg-layer" aria-hidden="true">
      <div className="bg-grid" />
      <div className="bg-aurora bg-aurora--1" />
      <div className="bg-aurora bg-aurora--2" />
      <div className="bg-aurora bg-aurora--3" />
      <div className="bg-scanline-bar" />
      <div className="bg-noise" />
      <div className="bg-particles">
        {Array.from({ length: 20 }).map((_, i) => (
          <span
            key={i}
            className="bg-particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${60 + Math.random() * 40}%`,
              animationDelay: `${Math.random() * 12}s`,
              animationDuration: `${8 + Math.random() * 10}s`,
              fontSize: `${8 + Math.random() * 6}px`,
              opacity: 0
            }}
          >
            {['0', '1', '{', '}', '<', '>', '/', ';', '(', ')', '=', '#', '$', '%', '&', '|', '!', '?', '*', '+'][i % 20]}
          </span>
        ))}
      </div>
    </div>
  );
}

function FaceStage({ avatarColor, stage, status }) {
  const face = stage === "landing" ? "^_^" : stage === "lobby" ? "-_-" : stage === "countdown" ? "0_0" : status === "Error" ? "x_x" : ">_<";

  return (
    <div className="face-stage">
      <span className="face-arrow">&lt;</span>
      <div className="face-bubble" style={{ borderColor: `${avatarColor}55`, boxShadow: `0 0 20px ${avatarColor}22, inset 0 0 20px ${avatarColor}11` }}>
        {face}
      </div>
      <span className="face-arrow">&gt;</span>
    </div>
  );
}

function AvatarColorPicker({ colors, onSelectColor, selectedColor }) {
  return (
    <div className="avatar-color-picker" role="radiogroup" aria-label="Avatar color">
      {colors.map((color, index) => {
        const isActive = color === selectedColor;

        return (
          <button
            aria-checked={isActive}
            aria-label={`Avatar color ${index + 1}`}
            className={`avatar-swatch ${isActive ? "avatar-swatch--active" : ""}`}
            key={color}
            onClick={() => onSelectColor(color)}
            role="radio"
            style={{ "--swatch-color": color }}
            type="button"
          />
        );
      })}
    </div>
  );
}

function LobbyPanel({ currentPlayer, lobbyState, onStartRound, onVoteChange, voteLanguage, voteDifficulty }) {
  const isHost = currentPlayer?.isHost ?? false;
  const hasEnoughPlayers = lobbyState.players.length >= 1;
  const canStart = isHost && hasEnoughPlayers;

  return (
    <div className="lobby-panel">
      <div className="lobby-panel__header">
        <div>
          <p className="eyebrow">Room</p>
          <h3>{lobbyState.code}</h3>
          <p className="match-copy">Each match now runs 3 problems before the lobby resets for a fresh game.</p>
          {!hasEnoughPlayers ? <p className="match-copy">At least 1 player is needed before the host can start the match.</p> : null}
        </div>
        <button className="arcade-button arcade-button--primary arcade-button--small" disabled={!canStart} onClick={onStartRound} type="button">
          Start Match
        </button>
      </div>

      <div className="lobby-grid">
        <div className="subpanel">
          <p className="eyebrow">Players</p>
          <div className="player-list">
            {lobbyState.players.map((player) => (
              <div className="player-row" key={player.publicId}>
                <div>
                  <strong>{player.name}</strong>
                  <span>{player.isHost ? "host" : "player"}</span>
                </div>
                <b>{player.score}</b>
              </div>
            ))}
          </div>
        </div>

        <div className="subpanel">
          <p className="eyebrow">Votes</p>
          <div className="vote-group">
            <span>Language</span>
            <div className="vote-grid vote-grid--two">
              {languages.map((language) => (
                <button
                  className={`chip-button ${voteLanguage === language ? "chip-button--active" : ""}`}
                  key={language}
                  onClick={() => onVoteChange(language, voteDifficulty)}
                  type="button"
                >
                  {language} ({lobbyState.votes.language[language]})
                </button>
              ))}
            </div>
          </div>
          <div className="vote-group">
            <span>Difficulty</span>
            <div className="vote-grid vote-grid--difficulty">
              {difficulties.map((difficulty) => (
                <button
                  className={`chip-button ${voteDifficulty === difficulty ? "chip-button--active" : ""}`}
                  key={difficulty}
                  onClick={() => onVoteChange(voteLanguage, difficulty)}
                  type="button"
                >
                  {difficulty} ({lobbyState.votes.difficulty[difficulty]})
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function CountdownScreen({ countdown, currentRound, lobbyCode, totalRounds }) {
  return (
    <main className="stage-screen">
      <section className="stage-card stage-card--countdown">
        <p className="eyebrow">Lobby {lobbyCode}</p>
        <h2>Get ready to debug</h2>
        <p className="match-pill">Problem {currentRound} of {totalRounds}</p>
        <div className="countdown-bubble">{countdown}</div>
        <p className="stage-copy">Everyone receives the same bug at the same time, so the race stays fair.</p>
      </section>
    </main>
  );
}

function GameScreen({ currentRound, editedCode, onCodeChange, onSaveExplanation, onSubmitAnswer, roundTimer, submissionFeedback, snippet, totalRounds }) {
  return (
    <main className="stage-screen">
      <section className="stage-card">
        <div className="stage-card__header">
          <div>
            <p className="eyebrow">{snippet.language} / {snippet.difficulty}</p>
            <h2>{snippet.title}</h2>
            <p className="match-copy">Problem {currentRound} of {totalRounds}</p>
          </div>
          <div className="timer-pill">{formatSeconds(roundTimer)}</div>
        </div>

        <DebugFlowManager
          initialCode={editedCode}
          onSaveExplanation={onSaveExplanation}
          onSubmitSolution={async (nextCode) => {
            onCodeChange(nextCode);
            return await onSubmitAnswer(nextCode);
          }}
          problem={snippet}
          submissionFeedback={submissionFeedback}
        />
      </section>
    </main>
  );
}

function ResultsScreen({ currentPlayer, lobbyState, onReplayRound, snippet }) {
  const solvedPlayerIds = new Set(lobbyState.roundResults.map((result) => result.playerPublicId));
  const rankedResults = [
    ...lobbyState.roundResults,
    ...lobbyState.players
      .filter((player) => !solvedPlayerIds.has(player.publicId))
      .map((player) => ({
        playerPublicId: player.publicId,
        name: player.name,
        submission: "No submission recorded.",
        submitted: false,
        isCorrect: false,
        solveOrder: null,
        timeRemaining: 0,
        pointsEarned: 0
      }))
  ];

  return (
    <main className="stage-screen">
      <section className="stage-card">
        <div className="stage-card__header">
          <div>
            <p className="eyebrow">Round complete</p>
            <h2>{lobbyState.winner.name || "No solver this round"}</h2>
            <p className="match-copy">Problem {lobbyState.currentRound} of {lobbyState.totalRounds}</p>
          </div>
          <button
            className="arcade-button arcade-button--primary arcade-button--small"
            disabled={!currentPlayer?.isHost}
            onClick={onReplayRound}
            type="button"
          >
            {lobbyState.hasNextRound ? "Next Problem" : "Back to Lobby"}
          </button>
        </div>

        <div className="results-grid">
          <div className="subpanel">
            <p className="eyebrow">Fastest solve</p>
            <pre className="code-area">
              <code>{lobbyState.winner.submission || "No correct fix was submitted."}</code>
            </pre>
          </div>
          <div className="subpanel">
            <p className="eyebrow">Reference fix</p>
            <pre className="code-area">
              <code>{snippet.referenceFix || "Reference fix will appear here after the round ends."}</code>
            </pre>
          </div>
        </div>

        <div className="subpanel">
          <p className="eyebrow">Round ranking</p>
          <div className="player-list">
            {rankedResults.map((result, index) => (
              <div className="player-row" key={result.playerPublicId}>
                <div>
                  <strong>
                    {index + 1}. {result.name}
                  </strong>
                  <span>
                    {result.solveOrder
                      ? `solve #${result.solveOrder} • ${formatSeconds(result.timeRemaining)} left`
                      : result.submitted
                        ? "submitted • incorrect"
                        : "unsolved • 0 pts"}
                  </span>
                </div>
                <b>+{result.pointsEarned}</b>
              </div>
            ))}
          </div>
        </div>

        <div className="subpanel">
          <p className="eyebrow">Match scoreboard</p>
          <div className="player-list">
            {lobbyState.players.map((player, index) => (
              <div className="player-row" key={player.publicId}>
                <div>
                  <strong>
                    {index + 1}. {player.name}
                  </strong>
                  <span>{player.isHost ? "host" : "challenger"}</span>
                </div>
                <b>{player.score}</b>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

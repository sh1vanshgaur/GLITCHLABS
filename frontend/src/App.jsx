import { useEffect, useMemo, useState } from "react";
import { useLobbyGame } from "./hooks/useLobbyGame";
import { formatSeconds } from "./lib/utils";

const languages = ["Python", "Java", "C", "C++"];
const difficulties = ["Easy", "Medium", "Hard"];

const mascotPalette = ["#ff5858", "#ff9c2a", "#f5eb40", "#78e33a", "#38dbff", "#4f5fff", "#aa47ff", "#ff7ed2"];

const infoCards = [
  {
    icon: "?",
    title: "About",
    content: "GLITCHLABS is a multiplayer debugging game where everyone gets the same broken snippet and races to submit the correct fix."
  },
  {
    icon: "*",
    title: "Why GLITCHLABS?",
    content: "It turns bug fixing into a fast social challenge, helping players practice logic, speed, and clean debugging under pressure."
  },
  {
    icon: "!",
    title: "How to play",
    content: "Enter a name, join a room, vote for language and difficulty, then fix the buggy code before anyone else."
  }
];

function buildHints(snippet) {
  if (!snippet) {
    return [];
  }

  const accepted = Array.isArray(snippet.acceptedAnswers) ? snippet.acceptedAnswers : [];
  const primaryClue = accepted[0] || snippet.category?.toLowerCase() || "logic";
  const strongerClue = accepted[1] || snippet.explanation || "Check the exact token or condition that breaks execution.";

  return [
    `Hint 1: This looks like a ${snippet.category?.toLowerCase() || "code"} issue. Focus on the line where ${primaryClue} becomes relevant.`,
    `Hint 2: Look closely for this clue: ${strongerClue}.`
  ];
}

export default function App() {
  const {
    state,
    status,
    error,
    submissionFeedback,
    createLobby,
    joinLobby,
    vote,
    startRound,
    submitAnswer,
    replayRound
  } = useLobbyGame();

  const [playerName, setPlayerName] = useState("quantum");
  const [joinCode, setJoinCode] = useState("GLTCH");
  const [editedCode, setEditedCode] = useState("");
  const [voteLanguage, setVoteLanguage] = useState("Python");
  const [voteDifficulty, setVoteDifficulty] = useState("Easy");
  const [activeSnippetId, setActiveSnippetId] = useState(null);

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

  async function handleSubmitAnswer(event) {
    event.preventDefault();
    if (!editedCode.trim()) {
      return;
    }

    try {
      await submitAnswer(editedCode);
    } catch {
      // Hook already stores displayable errors.
    }
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
      <div className="page-wrap">
        <header className="hero-header">
          <div className="logo-wrap">
            <div className="logo-mark" aria-hidden="true">
              {"GLITCHLABS".split("").map((letter, index) => (
                <span key={`${letter}-${index}`} style={{ color: mascotPalette[index % mascotPalette.length] }}>
                  {letter}
                </span>
              ))}
              <span className="logo-pencil">!</span>
            </div>
            <div className="mascot-row" aria-hidden="true">
              {mascotPalette.map((color, index) => (
                <div className="mini-mascot" key={color}>
                  <div className="mini-mascot__head" style={{ backgroundColor: color }} />
                  <span>{index + 1}</span>
                </div>
              ))}
            </div>
          </div>
        </header>

        {isLandingLike ? (
          <main>
            <section className="landing-stage">
              <div className="play-card">
                <div className="play-card__top">
                  <input
                    className="arcade-input"
                    maxLength={20}
                    onChange={(event) => setPlayerName(event.target.value)}
                    placeholder="enter name"
                    value={playerName}
                  />
                  <select
                    className="arcade-select"
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

                <div className="mascot-stage">
                  <FaceStage stage={state.stage} status={status} />
                  <div className="status-badge">{status}</div>
                </div>

                <button className="arcade-button arcade-button--primary" onClick={handleCreateLobby} type="button">
                  Play!
                </button>
                <button className="arcade-button arcade-button--secondary" onClick={handleJoinLobby} type="button">
                  Create Private Room
                </button>

                <div className="lobby-tools">
                  <input
                    className="arcade-input arcade-input--code"
                    maxLength={5}
                    onChange={(event) => setJoinCode(event.target.value.toUpperCase())}
                    placeholder="ROOM"
                    value={joinCode}
                  />
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

                {state.stage === "lobby" ? (
                  <LobbyPanel
                    lobbyState={state}
                    onStartRound={handleStartRound}
                    onVoteChange={handleVote}
                    voteDifficulty={voteDifficulty}
                    voteLanguage={voteLanguage}
                  />
                ) : null}
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
            onSubmitAnswer={handleSubmitAnswer}
            currentRound={state.currentRound}
            roundTimer={state.roundRemaining}
            submissionFeedback={submissionFeedback}
            snippet={currentSnippet}
            totalRounds={state.totalRounds}
          />
        ) : null}

        {state.stage === "results" && currentSnippet ? (
          <ResultsScreen lobbyState={state} onReplayRound={handleReplayRound} snippet={currentSnippet} />
        ) : null}
      </div>
    </div>
  );
}

function FaceStage({ stage, status }) {
  const face = stage === "landing" ? "^_^" : stage === "lobby" ? "-_-" : stage === "countdown" ? "0_0" : status === "Error" ? "x_x" : ">_<";

  return (
    <div className="face-stage">
      <span className="face-arrow">&lt;</span>
      <div className="face-bubble">{face}</div>
      <span className="face-arrow">&gt;</span>
    </div>
  );
}

function LobbyPanel({ lobbyState, onStartRound, onVoteChange, voteLanguage, voteDifficulty }) {
  return (
    <div className="lobby-panel">
      <div className="lobby-panel__header">
        <div>
          <p className="eyebrow">Room</p>
          <h3>{lobbyState.code}</h3>
          <p className="match-copy">Each match now runs 3 problems before the lobby resets for a fresh game.</p>
        </div>
        <button className="arcade-button arcade-button--primary arcade-button--small" onClick={onStartRound} type="button">
          Start Match
        </button>
      </div>

      <div className="lobby-grid">
        <div className="subpanel">
          <p className="eyebrow">Players</p>
          <div className="player-list">
            {lobbyState.players.map((player) => (
              <div className="player-row" key={player.id}>
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
            <div className="difficulty-row difficulty-row--wrap">
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
            <div className="difficulty-row difficulty-row--wrap">
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

function GameScreen({ currentRound, editedCode, onCodeChange, onSubmitAnswer, roundTimer, submissionFeedback, snippet, totalRounds }) {
  const hints = buildHints(snippet);
  const visibleHintCount = roundTimer <= 30 ? 2 : roundTimer <= 60 ? 1 : 0;

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

        <div className="code-grid">
          <CodePanel title="Buggy Code" value={snippet.code} readOnly />
          <CodePanel title="Your Fix" onChange={onCodeChange} value={editedCode} />
        </div>

        <div className="stage-meta">
          <span>{snippet.category}</span>
          <span>Submit the full corrected code</span>
        </div>

        <div className="hint-panel">
          <div className="hint-panel__header">
            <p className="eyebrow">Hints</p>
            <span>{visibleHintCount}/2 unlocked</span>
          </div>
          <div className="hint-list">
            {hints.map((hint, index) => {
              const isUnlocked = index < visibleHintCount;

              return (
                <div className={`hint-item ${isUnlocked ? "hint-item--active" : ""}`} key={hint}>
                  {isUnlocked ? hint : `Hint ${index + 1} unlocks after ${index === 0 ? "60" : "30"} seconds.`}
                </div>
              );
            })}
          </div>
        </div>

        <form className="submit-row" onSubmit={onSubmitAnswer}>
          <button className="arcade-button arcade-button--primary" type="submit">
            Submit Fix
          </button>
          <button className="arcade-button arcade-button--secondary" onClick={() => onCodeChange(snippet.code)} type="button">
            Reset
          </button>
        </form>

        {submissionFeedback ? (
          <p className={`feedback-strip ${submissionFeedback.status === "correct" ? "feedback-strip--success" : ""}`}>
            {submissionFeedback.message}
          </p>
        ) : (
          <p className="feedback-strip">Read the buggy code on the left and write your corrected version on the right.</p>
        )}
      </section>
    </main>
  );
}

function CodePanel({ onChange, readOnly = false, title, value }) {
  return (
    <div className="code-panel">
      <div className="code-panel__header">{title}</div>
      {readOnly ? (
        <pre className="code-area">
          <code>{value}</code>
        </pre>
      ) : (
        <textarea className="code-area code-area--editable" onChange={(event) => onChange(event.target.value)} spellCheck={false} value={value} />
      )}
    </div>
  );
}

function ResultsScreen({ lobbyState, onReplayRound, snippet }) {
  return (
    <main className="stage-screen">
      <section className="stage-card">
        <div className="stage-card__header">
          <div>
            <p className="eyebrow">Round complete</p>
            <h2>{lobbyState.winner.name || "No winner this round"}</h2>
            <p className="match-copy">Problem {lobbyState.currentRound} of {lobbyState.totalRounds}</p>
          </div>
          <button className="arcade-button arcade-button--primary arcade-button--small" onClick={onReplayRound} type="button">
            {lobbyState.hasNextRound ? "Next Problem" : "Back to Lobby"}
          </button>
        </div>

        <div className="results-grid">
          <div className="subpanel">
            <p className="eyebrow">Winning submission</p>
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
          <p className="eyebrow">Scoreboard</p>
          <div className="player-list">
            {lobbyState.players.map((player, index) => (
              <div className="player-row" key={player.id}>
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

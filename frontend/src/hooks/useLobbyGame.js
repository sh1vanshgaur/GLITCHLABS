import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

const initialState = {
  playerId: null,
  code: null,
  stage: "landing",
  selectedLanguage: "Python",
  selectedDifficulty: "Easy",
  countdownRemaining: 5,
  roundRemaining: 90,
  currentRound: 0,
  totalRounds: 0,
  hasNextRound: false,
  roundResults: [],
  winner: { id: null, name: null, answer: null },
  players: [],
  votes: {
    language: { Python: 0, Java: 0, C: 0, "C++": 0 },
    difficulty: { Easy: 0, Medium: 0, Hard: 0 }
  },
  snippet: null
};

export function useLobbyGame() {
  const [state, setState] = useState(initialState);
  const [status, setStatus] = useState("Idle");
  const [error, setError] = useState("");
  const [submissionFeedback, setSubmissionFeedback] = useState(null);

  useEffect(() => {
    if (!state.code) {
      return undefined;
    }

    const socket = new WebSocket(`ws://127.0.0.1:8000/ws/lobbies/${state.code}`);

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "state") {
        setState((current) => ({
          ...current,
          ...message.payload,
          playerId: current.playerId ?? message.payload.playerId ?? current.playerId
        }));
        setSubmissionFeedback((current) =>
          message.payload.stage !== "active" ? null : current
        );
      }
    };

    socket.onerror = () => {
      setError("WebSocket connection failed. Make sure the backend is running.");
    };

    const heartbeat = window.setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send("ping");
      }
    }, 15000);

    return () => {
      window.clearInterval(heartbeat);
      socket.close();
    };
  }, [state.code]);

  async function createLobby(playerName) {
    return performRequest("Creating lobby...", "/api/lobbies", {
      method: "POST",
      body: JSON.stringify({ player_name: playerName })
    });
  }

  async function joinLobby(playerName, lobbyCode) {
    return performRequest("Joining lobby...", "/api/lobbies/join", {
      method: "POST",
      body: JSON.stringify({
        player_name: playerName,
        lobby_code: lobbyCode
      })
    });
  }

  async function vote(language, difficulty) {
    if (!state.code || !state.playerId) {
      return;
    }

    return performRequest("Saving vote...", `/api/lobbies/${state.code}/vote`, {
      method: "POST",
      body: JSON.stringify({
        player_id: state.playerId,
        language,
        difficulty
      })
    });
  }

  async function startRound() {
    if (!state.code || !state.playerId) {
      return;
    }

    return performRequest("Starting round...", `/api/lobbies/${state.code}/start`, {
      method: "POST",
      body: JSON.stringify({ player_id: state.playerId })
    }, { clearSubmissionFeedback: true });
  }

  async function submitAnswer(codeSubmission) {
    if (!state.code || !state.playerId) {
      return;
    }

    return performRequest("Checking answer...", `/api/lobbies/${state.code}/submit`, {
      method: "POST",
      body: JSON.stringify({
        player_id: state.playerId,
        code_submission: codeSubmission
      })
    }, { trackSubmissionFeedback: true });
  }

  async function replayRound() {
    if (!state.code || !state.playerId) {
      return;
    }

    return performRequest("Resetting lobby...", `/api/lobbies/${state.code}/replay`, {
      method: "POST",
      body: JSON.stringify({ player_id: state.playerId })
    }, { clearSubmissionFeedback: true });
  }

  async function performRequest(nextStatus, path, options, behavior = {}) {
    setStatus(nextStatus);
    setError("");
    if (behavior.clearSubmissionFeedback) {
      setSubmissionFeedback(null);
    }

    try {
      const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
          "Content-Type": "application/json"
        }
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Request failed.");
      }

      setState((current) => ({
        ...current,
        ...payload,
        playerId: payload.playerId ?? current.playerId,
        stage: payload.stage ?? current.stage
      }));
      if (behavior.trackSubmissionFeedback) {
        setSubmissionFeedback(payload.submissionFeedback ?? null);
      }
      setStatus("Connected");
      return payload;
    } catch (requestError) {
      setStatus("Error");
      setError(requestError.message);
      throw requestError;
    }
  }

  return {
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
  };
}

import { useEffect, useMemo, useState } from "react";
import { API_BASE, WS_BASE } from "../lib/apiConfig";

const initialState = {
  playerPublicId: null,
  sessionToken: "",
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
  winner: { name: null, submission: null },
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

  const currentPlayer = useMemo(
    () => state.players.find((player) => player.publicId === state.playerPublicId) ?? null,
    [state.playerPublicId, state.players]
  );

  useEffect(() => {
    if (!state.code || !state.sessionToken) {
      return undefined;
    }

    const socket = new WebSocket(`${WS_BASE}/ws/lobbies/${state.code}?token=${encodeURIComponent(state.sessionToken)}`);

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "state") {
        setState((current) => ({
          ...current,
          ...message.payload,
          playerPublicId: current.playerPublicId ?? message.payload.playerPublicId ?? null,
          sessionToken: current.sessionToken || message.payload.sessionToken || ""
        }));
        setSubmissionFeedback((currentFeedback) => (message.payload.stage !== "active" ? null : currentFeedback));
        setStatus("Connected");
      }
    };

    socket.onerror = () => {
      setStatus("Error");
      setError("WebSocket connection failed. Make sure the backend is running and your session is valid.");
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
  }, [state.code, state.sessionToken]);

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
    if (!state.code || !state.sessionToken) {
      return null;
    }

    return performRequest("Saving vote...", `/api/lobbies/${state.code}/vote`, {
      method: "POST",
      body: JSON.stringify({ language, difficulty })
    });
  }

  async function startRound() {
    if (!state.code || !state.sessionToken) {
      return null;
    }

    return performRequest(
      "Starting round...",
      `/api/lobbies/${state.code}/start`,
      { method: "POST" },
      { clearSubmissionFeedback: true }
    );
  }

  async function submitAnswer(codeSubmission) {
    if (!state.code || !state.sessionToken) {
      return null;
    }

    return performRequest(
      "Checking answer...",
      `/api/lobbies/${state.code}/submit`,
      {
        method: "POST",
        body: JSON.stringify({ code_submission: codeSubmission })
      },
      { trackSubmissionFeedback: true }
    );
  }

  async function submitExplanation(explanation) {
    if (!state.code || !state.sessionToken) {
      return null;
    }

    return performRequest("Saving explanation...", `/api/lobbies/${state.code}/explain`, {
      method: "POST",
      body: JSON.stringify({ explanation })
    }, { mergeState: false });
  }

  async function replayRound() {
    if (!state.code || !state.sessionToken) {
      return null;
    }

    return performRequest(
      "Resetting lobby...",
      `/api/lobbies/${state.code}/replay`,
      { method: "POST" },
      { clearSubmissionFeedback: true }
    );
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
          "Content-Type": "application/json",
          ...(state.sessionToken ? { "X-Session-Token": state.sessionToken } : {}),
          ...(options?.headers ?? {})
        }
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Request failed.");
      }

      if (behavior.mergeState !== false) {
        setState((current) => ({
          ...current,
          ...payload,
          playerPublicId: payload.playerPublicId ?? current.playerPublicId,
          sessionToken: payload.sessionToken ?? current.sessionToken
        }));
      }
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
    currentPlayer,
    createLobby,
    joinLobby,
    vote,
    startRound,
    submitAnswer,
    submitExplanation,
    replayRound
  };
}

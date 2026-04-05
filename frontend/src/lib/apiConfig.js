function trimTrailingSlash(value) {
  return value.endsWith("/") ? value.slice(0, -1) : value;
}

function defaultApiBase() {
  if (typeof window === "undefined") {
    return "http://127.0.0.1:8000";
  }

  const { protocol, hostname } = window.location;
  const backendProtocol = protocol === "https:" ? "https:" : "http:";
  return `${backendProtocol}//${hostname}:8000`;
}

function defaultWsBase(apiBase) {
  if (apiBase.startsWith("https://")) {
    return `wss://${apiBase.slice("https://".length)}`;
  }
  if (apiBase.startsWith("http://")) {
    return `ws://${apiBase.slice("http://".length)}`;
  }
  return apiBase;
}

export const API_BASE = trimTrailingSlash(import.meta.env.VITE_API_BASE_URL || defaultApiBase());
export const WS_BASE = trimTrailingSlash(import.meta.env.VITE_WS_BASE_URL || defaultWsBase(API_BASE));

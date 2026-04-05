import { API_BASE } from "./apiConfig";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    },
    ...options
  });

  const payload = await response.json();

  if (!response.ok) {
    throw new Error(payload.detail || "Request failed.");
  }

  return payload;
}

export async function fetchProblem(problemId) {
  return await request(`/problem/${problemId}`);
}

export async function submitHypothesis(problemId, hypothesis) {
  return await request("/submit-hypothesis", {
    method: "POST",
    body: JSON.stringify({
      problem_id: problemId,
      selected_hypothesis: hypothesis
    })
  });
}

export async function runTrace(problemId) {
  return await request("/run-trace", {
    method: "POST",
    body: JSON.stringify({ problem_id: problemId })
  });
}

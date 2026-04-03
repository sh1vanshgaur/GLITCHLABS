import { getDebugProblem } from "./debugData";

const API_BASE = "http://127.0.0.1:8000";

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
  try {
    return await request(`/problem/${problemId}`);
  } catch {
    return getDebugProblem(problemId);
  }
}

export async function submitHypothesis(problemId, hypothesis) {
  try {
    return await request("/submit-hypothesis", {
      method: "POST",
      body: JSON.stringify({
        problem_id: problemId,
        selected_hypothesis: hypothesis
      })
    });
  } catch {
    const problem = getDebugProblem(problemId);
    const correct = problem.bug_type === hypothesis;

    return {
      correct,
      actual_bug_type: problem.bug_type,
      explanation: correct
        ? "Your diagnosis matches the real failure mode."
        : `This bug is really a ${problem.bug_type.replaceAll("_", " ")}. ${problem.explanation}`
    };
  }
}

export async function runTrace(problemId) {
  try {
    return await request("/run-trace", {
      method: "POST",
      body: JSON.stringify({ problem_id: problemId })
    });
  } catch {
    const problem = getDebugProblem(problemId);
    return { execution_steps: problem.trace_steps };
  }
}

export async function submitSolution(problemId, codeSubmission) {
  try {
    return await request("/submit-solution", {
      method: "POST",
      body: JSON.stringify({
        problem_id: problemId,
        code_submission: codeSubmission
      })
    });
  } catch {
    const problem = getDebugProblem(problemId);
    const normalize = (value) => value.replace(/\s+/g, "").trim().toLowerCase();
    const correct = normalize(problem.correct_code) === normalize(codeSubmission);

    return {
      correct,
      explanation: problem.explanation
    };
  }
}

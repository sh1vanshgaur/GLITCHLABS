import { useEffect, useMemo, useState } from "react";
import ExplanationCard from "./ExplanationCard";
import ExecutionControls from "./ExecutionControls";
import HypothesisModal from "./HypothesisModal";
import TracePanel from "./TracePanel";
import { fetchProblem, runTrace, submitHypothesis as submitHypothesisRequest, submitSolution as submitSolutionRequest } from "../lib/debugApi";
import { getHypothesisLabel } from "../lib/debugData";

const PHASES = ["hypothesis", "trace", "edit", "result"];

function normalizeProblem(problem) {
  if (!problem) {
    return null;
  }

  return {
    ...problem,
    buggy_code: problem.buggy_code ?? problem.code ?? "",
    correct_code: problem.correct_code ?? problem.referenceFix ?? "",
    bug_type: problem.bug_type ?? problem.bugType ?? "condition_issue",
    explanation: problem.explanation ?? "Trace the execution to find the mismatch between expected and actual behavior.",
    trace_steps: problem.trace_steps ?? problem.traceSteps ?? [],
    test_cases: problem.test_cases ?? problem.testCases ?? []
  };
}

export default function DebugFlowManager({
  initialCode = "",
  onSubmitSolution,
  problem,
  roundTimer,
  submissionFeedback
}) {
  const [currentPhase, setCurrentPhase] = useState("hypothesis");
  const [selectedHypothesis, setSelectedHypothesis] = useState("");
  const [hypothesisFeedback, setHypothesisFeedback] = useState(null);
  const [executionSteps, setExecutionSteps] = useState([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [editableCode, setEditableCode] = useState(initialCode);
  const [explanationInput, setExplanationInput] = useState("");
  const [localSubmissionFeedback, setLocalSubmissionFeedback] = useState(null);
  const [resolvedProblem, setResolvedProblem] = useState(normalizeProblem(problem));
  const [loadingTrace, setLoadingTrace] = useState(false);
  const [lockingHypothesis, setLockingHypothesis] = useState(false);
  const [submittingSolution, setSubmittingSolution] = useState(false);
  const problemId = problem?.id ?? null;

  useEffect(() => {
    let cancelled = false;

    async function hydrateProblem() {
      if (!problemId) {
        return;
      }

      const nextProblem = normalizeProblem(await fetchProblem(problemId));
      if (!cancelled) {
        setResolvedProblem(nextProblem);
      }
    }

    setResolvedProblem(normalizeProblem(problem));
    setCurrentPhase("hypothesis");
    setSelectedHypothesis("");
    setHypothesisFeedback(null);
    setExecutionSteps(normalizeProblem(problem)?.trace_steps ?? []);
    setCurrentStepIndex(0);
    setEditableCode(problem?.buggy_code ?? problem?.code ?? initialCode ?? "");
    setExplanationInput("");
    setLocalSubmissionFeedback(null);
    hydrateProblem();

    return () => {
      cancelled = true;
    };
  }, [problemId]);

  const activeProblem = resolvedProblem;
  const activeSubmissionFeedback = localSubmissionFeedback ?? submissionFeedback;
  const currentStep = executionSteps[currentStepIndex] ?? null;
  const currentTestCase = activeProblem?.test_cases?.[0] ?? null;
  const phaseIndex = PHASES.indexOf(currentPhase);
  const hasCompletedTrace = executionSteps.length > 0 && currentStepIndex >= executionSteps.length - 1;
  const problemPrompt = activeProblem
    ? `Fix the buggy ${activeProblem.language} code so the current output matches the expected output, then explain what caused the bug.`
    : "Fix the code so the output matches the expected behavior.";

  const lineDecoratedCode = useMemo(() => {
    const lines = (activeProblem?.buggy_code ?? "").split("\n");

    return lines.map((line, index) => ({
      lineNumber: index + 1,
      content: line,
      active: currentPhase === "trace" && currentStep?.line === index + 1
    }));
  }, [activeProblem?.buggy_code, currentPhase, currentStep?.line]);

  async function handleSubmitHypothesis() {
    if (!activeProblem?.id || !selectedHypothesis) {
      return;
    }

    setLockingHypothesis(true);
    try {
      const feedback = await submitHypothesisRequest(activeProblem.id, selectedHypothesis);
      setHypothesisFeedback(feedback);
      setLoadingTrace(true);
      const tracePayload = await runTrace(activeProblem.id);
      const steps = tracePayload.execution_steps ?? [];
      setExecutionSteps(steps);
      setCurrentStepIndex(0);
      setCurrentPhase("trace");
    } finally {
      setLockingHypothesis(false);
      setLoadingTrace(false);
    }
  }

  async function handleSubmitSolution(event) {
    if (event) {
      event.preventDefault();
    }

    if (!activeProblem?.id) {
      return;
    }

    setSubmittingSolution(true);
    setLocalSubmissionFeedback({
      status: "pending",
      message: "Checking your fix..."
    });

    try {
      if (onSubmitSolution) {
        const response = await onSubmitSolution(event, editableCode);
        const nextStatus = response?.submissionFeedback?.status ?? response?.status ?? submissionFeedback?.status;
        const nextMessage = response?.submissionFeedback?.message;

        if (nextStatus) {
          const parentFeedback = {
            status: nextStatus,
            message:
              nextMessage ??
              (nextStatus === "correct"
                ? "Fix accepted. Move to the explanation step."
                : "The output still does not match. Review the trace and try again.")
          };

          setLocalSubmissionFeedback(parentFeedback);
          if (nextStatus === "correct") {
            setCurrentPhase("result");
          }
          return response;
        }
      }

      const feedback = await submitSolutionRequest(activeProblem.id, editableCode);
      const nextFeedback = {
        status: feedback.correct ? "correct" : "incorrect",
        message: feedback.correct
          ? "Fix accepted. Move to the explanation step."
          : "The output still does not match. Review the trace and try again."
      };
      setLocalSubmissionFeedback(nextFeedback);

      if (feedback.correct) {
        setCurrentPhase("result");
      }

      return nextFeedback;
    } finally {
      setSubmittingSolution(false);
    }
  }

  return (
    <div className="debug-flow">
      <section className="problem-description-card">
        <div>
          <p className="eyebrow">Problem</p>
          <h3>What You Need To Do</h3>
          <p className="problem-description-copy">{problemPrompt}</p>
        </div>
        <div className="problem-description-meta">
          <div className="problem-description-meta__item">
            <span>Current focus</span>
            <strong>{selectedHypothesis ? getHypothesisLabel(selectedHypothesis) : "Choose a hypothesis"}</strong>
          </div>
          <div className="problem-description-meta__item">
            <span>Next action</span>
            <strong>
              {currentPhase === "hypothesis"
                ? "Classify the bug"
                : currentPhase === "trace"
                  ? "Trace the execution"
                  : currentPhase === "edit"
                    ? "Submit your fix"
                    : "Explain the bug"}
            </strong>
          </div>
        </div>
      </section>

      <section className="problem-brief">
        <div className="problem-brief__card problem-brief__card--error">
          <p className="eyebrow">Current Output</p>
          <pre className="code-area code-area--compact"><code>{currentTestCase?.actual_output ?? "Unavailable"}</code></pre>
        </div>
        <div className="problem-brief__card problem-brief__card--expected">
          <p className="eyebrow">Expected Output</p>
          <pre className="code-area code-area--compact"><code>{currentTestCase?.expected_output ?? "Unavailable"}</code></pre>
        </div>
      </section>

      <section className="step-flow-card">
        <div className="step-flow-card__header">
          <div>
            <p className="eyebrow">Step Flow</p>
            <h3>Hypothesis to result</h3>
          </div>
          <p className="helper-copy">Follow the sequence to understand the bug before fixing it.</p>
        </div>
        <div className="flow-progress" aria-label="Debug flow progress">
          {PHASES.map((phase, index) => (
            <div className={`flow-step ${index === phaseIndex ? "flow-step--current" : ""} ${index < phaseIndex ? "flow-step--done" : ""}`} key={phase}>
              <span>{index + 1}</span>
              <strong>{phase}</strong>
            </div>
          ))}
        </div>
      </section>

      {hypothesisFeedback ? (
        <p className={`feedback-strip ${hypothesisFeedback.correct ? "feedback-strip--success" : "feedback-strip--error"}`}>
          {hypothesisFeedback.correct ? "Hypothesis check: correct. " : "Hypothesis check: incorrect. "}
          {hypothesisFeedback.explanation}
        </p>
      ) : null}

      {currentPhase === "hypothesis" ? (
        <HypothesisModal
          feedback={hypothesisFeedback}
          onSelect={setSelectedHypothesis}
          onSubmit={handleSubmitHypothesis}
          selectedHypothesis={selectedHypothesis}
          submitting={lockingHypothesis}
        />
      ) : null}

      {(currentPhase === "trace" || currentPhase === "edit" || currentPhase === "result") && activeProblem ? (
        <section className="interaction-stage">
          <div className="interaction-stage__header">
            <div>
              <p className="eyebrow">Action Area</p>
              <h3>
                {currentPhase === "trace"
                  ? "Inspect execution"
                  : currentPhase === "edit"
                    ? "Apply your fix"
                    : "Review your result"}
              </h3>
            </div>
            <p className="helper-copy">
              {currentPhase === "trace"
                ? "Read the code on the left and use the execution panel to understand where it goes wrong."
                : currentPhase === "edit"
                  ? "Update the buggy code and submit once the output should match."
                  : "Check whether your reasoning matches the real bug."}
            </p>
          </div>

          <section className="trace-workspace">
          <div className="code-panel trace-code-panel">
            <div className="code-panel__header">
              {currentPhase === "trace" ? "Read-only trace view" : "Edit mode"}
            </div>
            {currentPhase === "trace" ? (
              <div className="trace-code">
                {lineDecoratedCode.map((line) => (
                  <div className={`trace-code__line ${line.active ? "trace-code__line--active" : ""}`} key={line.lineNumber}>
                    <span>{String(line.lineNumber).padStart(2, "0")}</span>
                    <code>{line.content || " "}</code>
                  </div>
                ))}
              </div>
            ) : (
              <textarea
                className="code-area code-area--editable"
                onChange={(event) => setEditableCode(event.target.value)}
                spellCheck={false}
                value={editableCode}
              />
            )}
          </div>

          {currentPhase === "trace" ? (
            <div className="trace-side">
              <TracePanel currentStep={currentStep} currentStepIndex={currentStepIndex} steps={executionSteps} />
              <ExecutionControls
                canStepBack={currentStepIndex > 0}
                canStepForward={currentStepIndex < executionSteps.length - 1}
                onReset={() => setCurrentStepIndex(0)}
                onStepBack={() => setCurrentStepIndex((value) => Math.max(value - 1, 0))}
                onStepForward={() => setCurrentStepIndex((value) => Math.min(value + 1, executionSteps.length - 1))}
              />
              <button
                className="arcade-button arcade-button--primary arcade-button--compact"
                disabled={loadingTrace || executionSteps.length === 0 || !hasCompletedTrace}
                onClick={() => setCurrentPhase("edit")}
                type="button"
              >
                {hasCompletedTrace ? "Unlock Edit Mode" : "Reach Final Trace Step"}
              </button>
            </div>
          ) : null}
          </section>
        </section>
      ) : null}

      {currentPhase === "edit" && activeProblem ? (
        <section className="debug-submit">
          <p className={`feedback-strip ${activeSubmissionFeedback?.status === "correct" ? "feedback-strip--success" : activeSubmissionFeedback?.status === "incorrect" ? "feedback-strip--error" : ""}`}>
            {activeSubmissionFeedback?.message ?? "The editor is unlocked now. Submit the full corrected code after using the trace to justify your fix."}
          </p>
          <div className="submit-row">
            <button
              className="arcade-button arcade-button--primary arcade-button--compact"
              disabled={submittingSolution}
              onClick={handleSubmitSolution}
              type="button"
            >
              {submittingSolution ? "Checking..." : "Submit Fix"}
            </button>
            <button
              className="arcade-button arcade-button--secondary arcade-button--compact"
              disabled={submittingSolution}
              onClick={() => setCurrentPhase("trace")}
              type="button"
            >
              Back To Trace
            </button>
          </div>
        </section>
      ) : null}

      {currentPhase === "result" && activeProblem ? (
        <div className="result-stack">
          <p className={`feedback-strip ${activeSubmissionFeedback?.status === "correct" ? "feedback-strip--success" : "feedback-strip--error"}`}>
            {activeSubmissionFeedback?.message ?? "Submission reviewed. Capture your reasoning below."}
          </p>
          <ExplanationCard
            explanation={activeProblem.explanation}
            onChange={setExplanationInput}
            solutionFeedback={activeSubmissionFeedback}
            value={explanationInput}
          />
        </div>
      ) : null}
    </div>
  );
}

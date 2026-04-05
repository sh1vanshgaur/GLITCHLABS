import { useEffect, useMemo, useState } from "react";
import ExplanationCard from "./ExplanationCard";
import ExecutionControls from "./ExecutionControls";
import HypothesisModal from "./HypothesisModal";
import TracePanel from "./TracePanel";
import { fetchProblem, runTrace, submitHypothesis as submitHypothesisRequest } from "../lib/debugApi";
import { getHypothesisLabel } from "../lib/debugData";

const PHASES = ["hypothesis", "trace", "edit", "result"];

function buildBehaviorInsight(problemStatement, testCase) {
  if (!testCase) {
    return "Compare the observed behavior with the expected behavior and identify which requirement from the problem statement is being violated.";
  }

  const observed = testCase.actual_output || "the observed result";
  const expected = testCase.expected_output || "the expected result";
  const context = testCase.input ? `For ${testCase.input}, ` : "";
  const expectation = problemStatement
    ? `This violates the expectation in the problem statement: ${problemStatement}`
    : "This violates the intended behavior described above.";

  return `${context}the code currently produces ${observed}, but it should produce ${expected}. ${expectation}`;
}

function normalizeProblem(problem) {
  if (!problem) {
    return null;
  }

  return {
    ...problem,
    buggy_code: problem.buggy_code ?? problem.code ?? "",
    problem_statement: problem.problem_statement ?? "",
    explanation: problem.explanation ?? null,
    trace_steps: problem.trace_steps ?? problem.traceSteps ?? [],
    test_cases: problem.test_cases ?? problem.testCases ?? []
  };
}

export default function DebugFlowManager({
  initialCode = "",
  onSaveExplanation,
  onSubmitSolution,
  problem,
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
  const [explanationStatus, setExplanationStatus] = useState(null);
  const [resolvedProblem, setResolvedProblem] = useState(normalizeProblem(problem));
  const [loadingTrace, setLoadingTrace] = useState(false);
  const [lockingHypothesis, setLockingHypothesis] = useState(false);
  const [submittingSolution, setSubmittingSolution] = useState(false);
  const [hypothesisOutcome, setHypothesisOutcome] = useState("unreached");
  const [editOutcome, setEditOutcome] = useState("unreached");
  const problemId = problem?.id ?? null;

  useEffect(() => {
    let cancelled = false;

    async function hydrateProblem() {
      if (!problemId) {
        return;
      }

      const nextProblem = normalizeProblem(await fetchProblem(problemId));
      if (!cancelled) {
        setResolvedProblem((current) => ({
          ...(current ?? {}),
          ...nextProblem,
          trace_steps: current?.trace_steps?.length ? current.trace_steps : nextProblem.trace_steps
        }));
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
    setExplanationStatus(null);
    setHypothesisOutcome("unreached");
    setEditOutcome("unreached");
    hydrateProblem().catch(() => {
      if (!cancelled) {
        setResolvedProblem(normalizeProblem(problem));
      }
    });

    return () => {
      cancelled = true;
    };
  }, [initialCode, problemId]);

  const activeProblem = resolvedProblem;
  const activeSubmissionFeedback = localSubmissionFeedback ?? submissionFeedback;
  const currentStep = executionSteps[currentStepIndex] ?? null;
  const sampleCases = activeProblem?.test_cases?.slice(0, 2) ?? [];
  const currentTestCase = sampleCases[0] ?? null;
  const behaviorInsight = buildBehaviorInsight(activeProblem?.problem_statement, currentTestCase);
  const phaseIndex = PHASES.indexOf(currentPhase);
  const hasCompletedTrace = executionSteps.length > 0 && currentStepIndex >= executionSteps.length - 1;
  const problemPrompt = activeProblem
    ? "Understand what the code is supposed to do, identify the bug, fix it, and explain the root cause."
    : "Understand the intended behavior, identify the bug, fix it, and explain the root cause.";

  const lineDecoratedCode = useMemo(() => {
    const lines = (activeProblem?.buggy_code ?? "").split("\n");

    return lines.map((line, index) => ({
      lineNumber: index + 1,
      content: line,
      active: currentPhase === "trace" && currentStep?.line === index + 1
    }));
  }, [activeProblem?.buggy_code, currentPhase, currentStep?.line]);

  function getStepVisualState(phase, index) {
    if (phase === "hypothesis") {
      if (currentPhase === "hypothesis") {
        return lockingHypothesis ? "pending" : "current";
      }
      if (hypothesisOutcome === "success") {
        return "completed-success";
      }
      if (hypothesisOutcome === "failed") {
        return "completed-failed";
      }
      return "completed-neutral";
    }

    if (phase === "trace") {
      if (currentPhase === "trace") {
        return "current";
      }
      if (index < phaseIndex) {
        return "completed-neutral";
      }
      return "upcoming";
    }

    if (phase === "edit") {
      if (currentPhase === "edit") {
        return submittingSolution ? "pending" : "current";
      }
      if (editOutcome === "success") {
        return "completed-success";
      }
      if (editOutcome === "failed") {
        return "completed-failed";
      }
      if (index < phaseIndex) {
        return "completed-neutral";
      }
      return "upcoming";
    }

    if (phase === "result") {
      return currentPhase === "result" ? "current" : index < phaseIndex ? "completed-neutral" : "upcoming";
    }

    return "upcoming";
  }

  function getStepStatusLabel(stepState) {
    switch (stepState) {
      case "completed-success":
        return "success";
      case "completed-failed":
        return "failed";
      case "completed-neutral":
        return "completed";
      case "pending":
        return "pending";
      case "current":
        return "current";
      default:
        return "upcoming";
    }
  }

  async function handleSubmitHypothesis() {
    if (!activeProblem?.id || !selectedHypothesis) {
      return;
    }

    setLockingHypothesis(true);
    try {
      const feedback = await submitHypothesisRequest(activeProblem.id, selectedHypothesis);
      setHypothesisFeedback(feedback);
      setHypothesisOutcome(feedback.correct ? "success" : "failed");
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

  async function handleSubmitSolution() {
    if (!onSubmitSolution) {
      return;
    }

    setSubmittingSolution(true);
    setLocalSubmissionFeedback({
      status: "pending",
      message: "Checking your fix..."
    });

    try {
      const response = await onSubmitSolution(editableCode);
      const nextStatus = response?.submissionFeedback?.status;
      const nextMessage = response?.submissionFeedback?.message;
      const recordedCorrectness = response?.submissionFeedback?.correct;

      if (!nextStatus) {
        throw new Error("The server did not return submission feedback.");
      }

      const parentFeedback = {
        status: nextStatus,
        correct: recordedCorrectness,
        message:
          nextMessage ??
          (recordedCorrectness
            ? "Correct submission recorded. Move to the result step."
            : "Submission recorded. Wait for the result step.")
      };

      setLocalSubmissionFeedback(parentFeedback);
      setEditOutcome(recordedCorrectness ? "success" : "failed");
      setCurrentPhase("result");
      return response;
    } finally {
      setSubmittingSolution(false);
    }
  }

  async function handleSaveExplanation() {
    if (!onSaveExplanation) {
      return;
    }

    setExplanationStatus({
      tone: "neutral",
      message: "Saving explanation..."
    });

    try {
      const response = await onSaveExplanation(explanationInput);
      setExplanationStatus({
        tone: "success",
        message: response?.message ?? "Explanation saved."
      });
    } catch (error) {
      setExplanationStatus({
        tone: "error",
        message: error.message
      });
    }
  }

  return (
    <div className="debug-flow">
      <section className="problem-description-card">
        <div>
          <p className="eyebrow">Problem</p>
          <h3>What You Need To Do</h3>
          <p className="problem-description-copy">{problemPrompt}</p>
          {activeProblem?.problem_statement ? (
            <div className="problem-statement-block">
              <p className="eyebrow">Problem Statement</p>
              <p className="problem-statement-text">{activeProblem.problem_statement}</p>
              {sampleCases.length ? (
                <div className="problem-sample-grid">
                  {sampleCases.map((testCase, index) => (
                    <div className="problem-sample-card" key={`${testCase.input}-${index}`}>
                      <p className="eyebrow">Sample {index + 1}</p>
                      <p><strong>Input/Context:</strong> {testCase.input || "No explicit input provided."}</p>
                      <p><strong>Expected:</strong> {testCase.expected_output}</p>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
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
          <p className="eyebrow">Observed Behavior</p>
          <pre className="code-area code-area--compact"><code>{currentTestCase?.actual_output ?? "Unavailable"}</code></pre>
        </div>
        <div className="problem-brief__card problem-brief__card--expected">
          <p className="eyebrow">Expected Behavior</p>
          <pre className="code-area code-area--compact"><code>{currentTestCase?.expected_output ?? "Unavailable"}</code></pre>
        </div>
      </section>

      <section className="behavior-insight-card">
        <p className="eyebrow">Behavior Insight</p>
        <h3>What's Wrong</h3>
        <p className="behavior-insight-copy">{behaviorInsight}</p>
      </section>

      <section className="round-layout">
        <aside className="progress-sidebar" aria-label="Round progress">
          <div className="progress-sidebar__header">
            <p className="eyebrow">Round Progress</p>
            <h3>Hypothesis to result</h3>
            <p className="helper-copy">Stay oriented as you move through each debugging phase.</p>
          </div>
          <div
            className="progress-rail"
            style={{ "--progress-fill": `${Math.max(0, phaseIndex) / Math.max(PHASES.length - 1, 1) * 100}%` }}
          >
            {PHASES.map((phase, index) => {
              const state = getStepVisualState(phase, index);

              return (
                <div className={`progress-step progress-step--${state}`} key={phase}>
                  <div className="progress-step__marker" aria-hidden="true">
                    <span>{index + 1}</span>
                  </div>
                  <div className="progress-step__content">
                    <p className="progress-step__status">{getStepStatusLabel(state)}</p>
                    <strong>{phase}</strong>
                  </div>
                </div>
              );
            })}
          </div>
        </aside>

        <div className="round-main">
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
              </div>

              {currentPhase === "trace" ? (
                <div className="mode-callout mode-callout--trace">
                  <p className="eyebrow">What To Do In Trace Mode</p>
                  <h4>Step through the code first, then unlock editing.</h4>
                  <p>
                    Start with the highlighted line on the left, read the execution details on the right, and keep stepping
                    forward until you can clearly explain what behavior goes wrong.
                  </p>
                </div>
              ) : null}

              {currentPhase === "edit" ? (
                <div className="mode-callout">
                  <p className="eyebrow">What To Do In Edit Mode</p>
                  <h4>Fix the code only after you understand the bug.</h4>
                  <p>Update the buggy code so the behavior matches the problem statement and expected behavior.</p>
                </div>
              ) : null}

              {currentPhase === "result" ? (
                <div className="mode-callout">
                  <p className="eyebrow">What To Do In Result Mode</p>
                  <h4>Explain the root cause in your own words.</h4>
                  <p>Summarize what the bug changed in the program's behavior before the round moves on.</p>
                </div>
              ) : null}

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
                explanationStatus={explanationStatus}
                onChange={setExplanationInput}
                onSave={handleSaveExplanation}
                saveDisabled={!explanationInput.trim()}
                solutionFeedback={activeSubmissionFeedback}
                value={explanationInput}
              />
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
}

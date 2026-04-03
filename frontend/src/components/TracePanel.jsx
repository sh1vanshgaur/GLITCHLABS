export default function TracePanel({ currentStep, currentStepIndex, steps }) {
  return (
    <aside className="trace-panel">
      <div className="trace-panel__header">
        <div>
          <p className="eyebrow">Execution Panel</p>
          <h3>Trace Mode</h3>
        </div>
        <div className="trace-counter">
          Step {Math.min(currentStepIndex + 1, steps.length)} / {steps.length}
        </div>
      </div>

      <div className="trace-focus">
        <div className={`trace-line ${currentStep?.suspicious ? "trace-line--suspicious" : ""}`}>
          Current line: {currentStep?.line ?? "-"}
        </div>
        <p className="trace-note">{currentStep?.note ?? "Press step forward to inspect the program state."}</p>
      </div>

      <div className="trace-vars">
        <p className="eyebrow">Variables</p>
        <div className="trace-vars__list">
          {currentStep?.variables ? (
            Object.entries(currentStep.variables).map(([name, value]) => (
              <div className="trace-var" key={name}>
                <span>{name}</span>
                <strong>{String(value)}</strong>
              </div>
            ))
          ) : (
            <p className="feedback-strip">No variables captured yet. Start stepping through the code.</p>
          )}
        </div>
      </div>
    </aside>
  );
}

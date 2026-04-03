import { HYPOTHESIS_OPTIONS } from "../lib/debugData";

export default function HypothesisModal({
  feedback,
  onSelect,
  onSubmit,
  selectedHypothesis,
  submitting = false
}) {
  return (
    <section className="hypothesis-modal">
      <div className="hypothesis-modal__header">
        <div>
          <p className="eyebrow">Step 1</p>
          <h3>Choose your bug hypothesis</h3>
          <p className="helper-copy">
            Editing stays locked until you commit to a diagnosis. Pick the bug family you think caused the wrong output.
          </p>
        </div>
        <div className="phase-badge">Thinking</div>
      </div>

      <div className="hypothesis-grid">
        {HYPOTHESIS_OPTIONS.map((option) => {
          const active = selectedHypothesis === option.value;

          return (
            <button
              className={`hypothesis-option ${active ? "hypothesis-option--active" : ""}`}
              key={option.value}
              onClick={() => onSelect(option.value)}
              type="button"
            >
              <strong>{option.label}</strong>
              <span>{option.description}</span>
            </button>
          );
        })}
      </div>

      <div className="hypothesis-modal__footer">
        <button
          className="arcade-button arcade-button--primary arcade-button--compact"
          disabled={!selectedHypothesis || submitting}
          onClick={onSubmit}
          type="button"
        >
          {submitting ? "Analyzing..." : "Lock Hypothesis"}
        </button>

        {feedback ? (
          <p className={`feedback-strip ${feedback.correct ? "feedback-strip--success" : "feedback-strip--error"}`}>
            {feedback.correct ? "Correct hypothesis. " : "Incorrect hypothesis. "}
            {feedback.explanation}
          </p>
        ) : (
          <p className="feedback-strip">You must choose one path before the trace terminal unlocks.</p>
        )}
      </div>
    </section>
  );
}

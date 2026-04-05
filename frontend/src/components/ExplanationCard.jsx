export default function ExplanationCard({
  explanation,
  explanationStatus,
  onChange,
  onSave,
  saveDisabled,
  solutionFeedback,
  value
}) {
  const hasCorrectSubmission = solutionFeedback?.correct === true;

  return (
    <section className="explanation-card">
      <div className="stage-card__header">
        <div>
          <p className="eyebrow">Step 4</p>
          <h3>Explain the bug</h3>
          <p className="helper-copy">
            {hasCorrectSubmission
              ? "Write what was wrong, then save your explanation before reading the final reasoning."
              : "Your submission has been recorded. Stay here and wait for the round results."}
          </p>
        </div>
        <div className={`phase-badge ${hasCorrectSubmission ? "phase-badge--success" : "phase-badge--warn"}`}>
          {hasCorrectSubmission ? "Fix Accepted" : "Submission Recorded"}
        </div>
      </div>

      {hasCorrectSubmission ? (
        <>
          <textarea
            className="code-area code-area--editable explanation-input"
            onChange={(event) => onChange(event.target.value)}
            placeholder="What was wrong with the code?"
            spellCheck={false}
            value={value}
          />

          <div className="submit-row">
            <button
              className="arcade-button arcade-button--primary arcade-button--compact"
              disabled={saveDisabled}
              onClick={onSave}
              type="button"
            >
              Save Explanation
            </button>
          </div>
        </>
      ) : (
        <div className="feedback-strip">
          Incorrect submissions are still part of the round. The final result screen will show how your fix compared with the reference answer.
        </div>
      )}

      {explanationStatus ? (
        <div className={`feedback-strip ${explanationStatus.tone === "error" ? "feedback-strip--error" : explanationStatus.tone === "success" ? "feedback-strip--success" : ""}`}>
          {explanationStatus.message}
        </div>
      ) : null}

      {explanation ? (
        <div className="feedback-strip feedback-strip--success">
          Correct reasoning: {explanation}
        </div>
      ) : null}
    </section>
  );
}

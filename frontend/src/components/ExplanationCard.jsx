export default function ExplanationCard({
  explanation,
  onChange,
  solutionFeedback,
  value
}) {
  return (
    <section className="explanation-card">
      <div className="stage-card__header">
        <div>
          <p className="eyebrow">Step 4</p>
          <h3>Explain the bug</h3>
          <p className="helper-copy">Write what was wrong before you read the final reasoning.</p>
        </div>
        <div className={`phase-badge ${solutionFeedback?.correct ? "phase-badge--success" : "phase-badge--warn"}`}>
          {solutionFeedback?.correct ? "Fix Accepted" : "Still Learning"}
        </div>
      </div>

      <textarea
        className="code-area code-area--editable explanation-input"
        onChange={(event) => onChange(event.target.value)}
        placeholder="What was wrong with the code?"
        spellCheck={false}
        value={value}
      />

      <div className="feedback-strip feedback-strip--success">
        Correct reasoning: {explanation}
      </div>
    </section>
  );
}

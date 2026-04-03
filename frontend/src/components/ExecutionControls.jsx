export default function ExecutionControls({
  canStepBack,
  canStepForward,
  onReset,
  onStepBack,
  onStepForward
}) {
  return (
    <div className="execution-controls">
      <button
        className="arcade-button arcade-button--secondary arcade-button--compact"
        disabled={!canStepBack}
        onClick={onStepBack}
        type="button"
      >
        Step Back
      </button>
      <button
        className="arcade-button arcade-button--primary arcade-button--compact"
        disabled={!canStepForward}
        onClick={onStepForward}
        type="button"
      >
        Step Forward
      </button>
      <button className="arcade-button arcade-button--ghost arcade-button--compact" onClick={onReset} type="button">
        Reset
      </button>
    </div>
  );
}

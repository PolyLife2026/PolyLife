export default function ProgressBar({ score, label }) {
  const pct = Math.min(100, Math.max(0, Number(score) || 0));

  return (
    <div className="progress-bar-wrap">
      {label && <div className="progress-bar-label">{label}</div>}
      <div className="progress-bar-track">
        <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="progress-bar-value">{pct.toFixed(1)}%</span>
    </div>
  );
}

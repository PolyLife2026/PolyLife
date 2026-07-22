const STEPS = [
  { key: 'challenge', label: 'چالش / مسابقه', desc: 'Challenge / Competition' },
  { key: 'join', label: 'پیوستن', desc: 'Participant' },
  { key: 'activity', label: 'فعالیت / نتیجه', desc: 'Activity / Score' },
  { key: 'score', label: 'امتیاز', desc: 'Score / Rank' },
  { key: 'leaderboard', label: 'جدول', desc: 'Leaderboard' },
  { key: 'reward', label: 'جایزه', desc: 'Badge / Reward' },
];

export default function SystemFlowDiagram() {
  return (
    <section className="flow-diagram card">
      <h2>جریان اطلاعات سیستم</h2>
      <p className="form-hint flow-diagram__hint">
        Challenge → Participant → Activity → Score / Rank → Leaderboard → Badge / Reward
      </p>
      <div className="flow-steps">
        {STEPS.map((step, i) => (
          <div key={step.key} className="flow-step-wrap">
            <div className="flow-step">
              <span className="flow-step__num">{i + 1}</span>
              <strong>{step.label}</strong>
              <small>{step.desc}</small>
            </div>
            {i < STEPS.length - 1 && <span className="flow-arrow">←</span>}
          </div>
        ))}
      </div>
    </section>
  );
}

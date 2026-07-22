const STEPS = [
  { key: 'challenge', label: 'چالش', desc: 'رویداد ورزشی' },
  { key: 'join', label: 'پیوستن', desc: 'Participant_Challenge' },
  { key: 'activity', label: 'فعالیت', desc: 'ثبت روزانه' },
  { key: 'score', label: 'امتیاز', desc: 'Score / Rank' },
  { key: 'leaderboard', label: 'جدول', desc: 'Leaderboard' },
  { key: 'reward', label: 'جایزه', desc: 'Badge / Reward' },
];

export default function FlowDiagram() {
  return (
    <section className="flow-diagram card">
      <h2>جریان سیستم چالش</h2>
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

import { BADGE_INFO } from '../../utils/constants';

function badgeForRank(rank) {
  if (rank === 1) return BADGE_INFO.top1;
  if (rank <= 3) return BADGE_INFO.top3;
  if (rank <= 10) return BADGE_INFO.top10;
  return null;
}

export default function WinnersPanel({ leaderboard, challengeEnded }) {
  if (!challengeEnded || !leaderboard?.length) return null;

  const topThree = leaderboard.slice(0, 3);

  return (
    <section className="winners-panel card">
      <h3>🏆 برندگان و جوایز</h3>
      <p className="form-hint">
        چالش به پایان رسید. نشان‌ها و پاداش‌ها به‌صورت خودکار به برندگان اختصاص یافت.
      </p>
      <div className="winners-grid">
        {topThree.map((entry) => {
          const badge = badgeForRank(entry.rank);
          return (
            <div key={entry.user_id} className={`winner-card winner-card--rank-${entry.rank}`}>
              <div className="winner-rank">{entry.rank}</div>
              <div className="winner-emoji">{badge?.emoji ?? '🏅'}</div>
              <div className="winner-name">کاربر #{entry.user_id}</div>
              <div className="winner-score">{Number(entry.score).toFixed(1)}%</div>
              {badge && <div className="winner-badge">{badge.label}</div>}
            </div>
          );
        })}
      </div>
      <div className="badge-legend">
        {Object.values(BADGE_INFO).map((b) => (
          <span key={b.label} className="badge-legend-item">
            {b.emoji} {b.label} — {b.description}
          </span>
        ))}
      </div>
    </section>
  );
}

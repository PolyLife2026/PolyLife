import { BADGE_INFO } from '../../utils/constants';

function badgeForRank(rank) {
  if (rank === 1) return BADGE_INFO.top1;
  if (rank <= 3) return BADGE_INFO.top3;
  if (rank <= 10) return BADGE_INFO.top10;
  return null;
}

export default function CompetitionWinnersPanel({ rankings }) {
  if (!rankings?.length) return null;

  const topThree = [...rankings]
    .sort((a, b) => (a.rank ?? 999) - (b.rank ?? 999))
    .slice(0, 3);

  return (
    <section className="winners-panel card competition-winners">
      <h3>🏆 رتبه‌بندی نهایی</h3>
      <p className="form-hint">
        مسابقه به پایان رسید. نفرات برتر مشخص شدند.
      </p>
      <div className="winners-grid">
        {topThree.map((entry) => {
          const badge = badgeForRank(entry.rank);
          return (
            <div key={entry.user_id} className={`winner-card winner-card--rank-${entry.rank}`}>
              <div className="winner-rank">{entry.rank}</div>
              <div className="winner-emoji">{badge?.emoji ?? '🏅'}</div>
              <div className="winner-name">کاربر #{entry.user_id}</div>
              <div className="winner-score">{Number(entry.total_score).toFixed(1)} امتیاز</div>
              {badge && <div className="winner-badge">{badge.label}</div>}
            </div>
          );
        })}
      </div>
    </section>
  );
}

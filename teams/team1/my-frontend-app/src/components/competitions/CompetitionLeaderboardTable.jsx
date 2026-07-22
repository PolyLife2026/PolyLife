import { useAuth } from '../../context/AuthContext';

export default function CompetitionLeaderboardTable({ entries, loading }) {
  const { userId } = useAuth();

  if (loading) {
    return <div className="loading-state">در حال بارگذاری جدول امتیازات...</div>;
  }

  if (!entries?.length) {
    return (
      <div className="empty-state">
        هنوز امتیازی ثبت نشده. پس از ثبت‌نام منتظر ثبت نتایج باشید.
      </div>
    );
  }

  const sorted = [...entries].sort((a, b) => {
    if (a.rank != null && b.rank != null) return a.rank - b.rank;
    return Number(b.total_score) - Number(a.total_score);
  });

  return (
    <div className="leaderboard-wrap">
      <table className="leaderboard-table">
        <thead>
          <tr>
            <th>رتبه</th>
            <th>کاربر</th>
            <th>امتیاز</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((entry, index) => {
            const rank = entry.rank ?? index + 1;
            return (
              <tr
                key={`${entry.user_id}-${rank}`}
                className={Number(entry.user_id) === Number(userId) ? 'leaderboard-row--me' : ''}
              >
                <td>
                  <span className={`rank-badge rank-badge--${rank <= 3 ? rank : 'other'}`}>
                    {rank}
                  </span>
                </td>
                <td>
                  کاربر #{entry.user_id}
                  {Number(entry.user_id) === Number(userId) && <span className="me-tag">شما</span>}
                </td>
                <td>{Number(entry.total_score).toFixed(1)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

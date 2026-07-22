import { useAuth } from '../../context/AuthContext';

export default function LeaderboardTable({ entries, loading }) {
  const { userId } = useAuth();

  if (loading) {
    return <div className="loading-state">در حال بارگذاری جدول امتیازات...</div>;
  }

  if (!entries?.length) {
    return (
      <div className="empty-state">
        هنوز امتیازی ثبت نشده. اولین نفر باشید!
      </div>
    );
  }

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
          {entries.map((entry) => (
            <tr
              key={`${entry.user_id}-${entry.rank}`}
              className={Number(entry.user_id) === Number(userId) ? 'leaderboard-row--me' : ''}
            >
              <td>
                <span className={`rank-badge rank-badge--${entry.rank <= 3 ? entry.rank : 'other'}`}>
                  {entry.rank}
                </span>
              </td>
              <td>
                کاربر #{entry.user_id}
                {Number(entry.user_id) === Number(userId) && <span className="me-tag">شما</span>}
              </td>
              <td>{Number(entry.score).toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

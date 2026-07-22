import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  fetchChallenge,
  fetchLeaderboard,
  fetchMyRank,
  joinChallenge,
  deleteChallenge,
} from '../services/challenges';
import ActivityForm from '../components/challenges/ActivityForm';
import LeaderboardTable from '../components/challenges/LeaderboardTable';
import ProgressBar from '../components/challenges/ProgressBar';
import StatusBadge from '../components/challenges/StatusBadge';
import WinnersPanel from '../components/challenges/WinnersPanel';
import { useAuth } from '../context/AuthContext';
import {
  getActivityLabel,
  getDifficultyLabel,
  getGoalUnitLabel,
} from '../utils/constants';
import { formatDateTime, parseApiError } from '../utils/formatters';

export default function ChallengeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { userId, isCoach } = useAuth();

  const [challenge, setChallenge] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [myRank, setMyRank] = useState(null);
  const [loading, setLoading] = useState(true);
  const [joinLoading, setJoinLoading] = useState(false);
  const [error, setError] = useState('');
  const [joinError, setJoinError] = useState('');
  const [lbLoading, setLbLoading] = useState(false);

  const joined = Boolean(challenge?.is_joined);

  const loadLeaderboard = useCallback(async () => {
    setLbLoading(true);
    try {
      const data = await fetchLeaderboard(id);
      setLeaderboard(data);
    } catch {
      setLeaderboard([]);
    } finally {
      setLbLoading(false);
    }
  }, [id]);

  const loadMyRank = useCallback(async () => {
    try {
      const data = await fetchMyRank(id);
      setMyRank(data);
    } catch {
      setMyRank(null);
    }
  }, [id]);

  const loadAll = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const detail = await fetchChallenge(id);
      setChallenge(detail);
      await Promise.all([loadLeaderboard(), loadMyRank()]);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }, [id, userId, loadLeaderboard, loadMyRank]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  useEffect(() => {
    if (challenge?.status !== 'started') return undefined;
    const interval = setInterval(() => {
      loadLeaderboard();
      loadMyRank();
    }, 8000);
    return () => clearInterval(interval);
  }, [challenge?.status, loadLeaderboard, loadMyRank]);

  async function handleJoin() {
    setJoinError('');
    setJoinLoading(true);
    try {
      await joinChallenge(id);
      setChallenge((prev) => ({ ...prev, is_joined: true }));
    } catch (err) {
      const msg = parseApiError(err);
      if (msg.includes('already joined')) {
        setChallenge((prev) => ({ ...prev, is_joined: true }));
      } else {
        setJoinError(msg);
      }
    } finally {
      setJoinLoading(false);
    }
  }

  async function handleDelete() {
    if (!window.confirm('آیا از حذف این چالش مطمئن هستید؟')) return;
    try {
      await deleteChallenge(id);
      navigate('/challenges');
    } catch (err) {
      setError(parseApiError(err));
    }
  }

  function handleActivitySuccess() {
    loadLeaderboard();
    loadMyRank();
  }

  if (loading) return <div className="loading-state page">در حال بارگذاری...</div>;
  if (error && !challenge) return <div className="alert alert--error page">{error}</div>;
  if (!challenge) return null;

  const canJoin = !joined && ['created', 'started'].includes(challenge.status);
  const canLogActivity = joined && challenge.status === 'started';
  const isCreator = String(challenge.created_by) === String(userId);
  const canEdit = isCoach && isCreator && challenge.status === 'created';

  return (
    <div className="page challenge-detail">
      <Link to="/challenges" className="back-link">→ بازگشت به لیست</Link>

      <header className="detail-header card">
        <div className="detail-header__top">
          <h1>{challenge.title}</h1>
          <StatusBadge status={challenge.status} />
        </div>
        {challenge.description && <p className="detail-desc">{challenge.description}</p>}

        <dl className="detail-meta">
          <div><dt>نوع فعالیت</dt><dd>{getActivityLabel(challenge.activity_type)}</dd></div>
          <div><dt>دشواری</dt><dd>{getDifficultyLabel(challenge.difficulty)}</dd></div>
          <div><dt>هدف</dt><dd>{challenge.value_goal} {getGoalUnitLabel(challenge.goal_unit)}</dd></div>
          <div><dt>شروع</dt><dd>{formatDateTime(challenge.date_start)}</dd></div>
          <div><dt>پایان</dt><dd>{formatDateTime(challenge.date_end)}</dd></div>
        </dl>

        <div className="detail-actions">
          {canJoin && (
            <button type="button" className="btn btn--primary" disabled={joinLoading} onClick={handleJoin}>
              {joinLoading ? 'در حال پیوستن...' : 'پیوستن به چالش'}
            </button>
          )}
          {joined && <span className="joined-badge">✓ شما در این چالش شرکت کرده‌اید</span>}
          {canEdit && (
            <>
              <Link to={`/challenges/${id}/edit`} className="btn btn--secondary">ویرایش</Link>
              <button type="button" className="btn btn--danger" onClick={handleDelete}>حذف</button>
            </>
          )}
        </div>
        {joinError && <div className="alert alert--error">{joinError}</div>}
      </header>

      {myRank && (
        <section className="card my-rank-section">
          <h3>رتبه و پیشرفت شما</h3>
          <div className="my-rank-stats">
            <span className="my-rank-num">رتبه {myRank.rank}</span>
            <span>امتیاز: {Number(myRank.score).toFixed(1)}%</span>
          </div>
          <ProgressBar score={myRank.score} />
        </section>
      )}

      <div className="detail-grid">
        <section className="card">
          <div className="section-header">
            <h3>جدول امتیازات</h3>
            {challenge.status === 'started' && (
              <span className="live-badge">● زنده</span>
            )}
          </div>
          <LeaderboardTable entries={leaderboard} loading={lbLoading} />
        </section>

        <ActivityForm
          challengeId={Number(id)}
          goalUnit={challenge.goal_unit}
          disabled={!canLogActivity}
          onSuccess={handleActivitySuccess}
        />
      </div>

      <WinnersPanel leaderboard={leaderboard} challengeEnded={challenge.status === 'ended'} />
    </div>
  );
}

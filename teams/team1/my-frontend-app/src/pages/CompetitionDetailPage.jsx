import { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import CompetitionLeaderboardTable from '../components/competitions/CompetitionLeaderboardTable';
import CompetitionStatusBadge from '../components/competitions/CompetitionStatusBadge';
import CompetitionWinnersPanel from '../components/competitions/CompetitionWinnersPanel';
import ResultEntryForm from '../components/competitions/ResultEntryForm';
import { useAuth } from '../context/AuthContext';
import {
  fetchCompetition,
  fetchCompetitionFinalRankings,
  fetchCompetitionLeaderboard,
  joinCompetition,
  startCompetition,
} from '../services/competitions';
import { getCompetitionTypeLabel } from '../utils/constants';
import { formatDateTime, parseApiError } from '../utils/formatters';

export default function CompetitionDetailPage() {
  const { id } = useParams();
  const { userId, isCoach } = useAuth();

  const [competition, setCompetition] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [finalRankings, setFinalRankings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lbLoading, setLbLoading] = useState(false);
  const [joinLoading, setJoinLoading] = useState(false);
  const [startLoading, setStartLoading] = useState(false);
  const [error, setError] = useState('');
  const [joinError, setJoinError] = useState('');
  const [startError, setStartError] = useState('');

  const loadLeaderboard = useCallback(async () => {
    setLbLoading(true);
    try {
      const data = await fetchCompetitionLeaderboard(id);
      setLeaderboard(data.results ?? data);
    } catch {
      setLeaderboard([]);
    } finally {
      setLbLoading(false);
    }
  }, [id]);

  const loadFinalRankings = useCallback(async () => {
    try {
      const data = await fetchCompetitionFinalRankings(id);
      setFinalRankings(data.results ?? data);
    } catch {
      setFinalRankings([]);
    }
  }, [id]);

  const loadAll = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const detail = await fetchCompetition(id);
      setCompetition(detail);
      if (detail.status === 'finished') {
        await Promise.all([loadFinalRankings(), loadLeaderboard()]);
      } else {
        await loadLeaderboard();
      }
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }, [id, userId, loadLeaderboard, loadFinalRankings]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  useEffect(() => {
    if (competition?.status !== 'active') return undefined;
    const interval = setInterval(loadLeaderboard, 8000);
    return () => clearInterval(interval);
  }, [competition?.status, loadLeaderboard]);

  async function handleJoin() {
    setJoinError('');
    setJoinLoading(true);
    try {
      await joinCompetition(id);
      setCompetition((prev) => ({ ...prev, is_joined: true }));
    } catch (err) {
      const msg = parseApiError(err);
      if (msg.includes('Already joined')) {
        setCompetition((prev) => ({ ...prev, is_joined: true }));
      } else {
        setJoinError(msg);
      }
    } finally {
      setJoinLoading(false);
    }
  }

  async function handleStart() {
    setStartError('');
    setStartLoading(true);
    try {
      const updated = await startCompetition(id);
      setCompetition((prev) => ({ ...prev, status: updated.status }));
    } catch (err) {
      setStartError(parseApiError(err));
    } finally {
      setStartLoading(false);
    }
  }

  function handleResultSuccess() {
    loadLeaderboard();
  }

  if (loading) return <div className="loading-state page">در حال بارگذاری...</div>;
  if (error && !competition) return <div className="alert alert--error page">{error}</div>;
  if (!competition) return null;

  const canJoin = !competition.is_joined && competition.status === 'pending';
  const canStart = isCoach && competition.status === 'pending';
  const isActive = competition.status === 'active';
  const isFinished = competition.status === 'finished';
  const displayRankings = isFinished && finalRankings.length ? finalRankings : leaderboard;

  return (
    <div className="page competition-detail">
      <Link to="/competitions" className="back-link">→ بازگشت به لیست</Link>

      <header className="detail-header card competition-detail-header">
        <div className="detail-header__top">
          <h1>{competition.title}</h1>
          <CompetitionStatusBadge status={competition.status} />
        </div>
        {competition.description && <p className="detail-desc">{competition.description}</p>}
        {competition.rules && (
          <div className="competition-rules">
            <strong>قوانین:</strong> {competition.rules}
          </div>
        )}

        <dl className="detail-meta">
          <div><dt>نوع مسابقه</dt><dd>{getCompetitionTypeLabel(competition.competition_type)}</dd></div>
          <div><dt>شروع</dt><dd>{formatDateTime(competition.date_start)}</dd></div>
          <div><dt>پایان</dt><dd>{formatDateTime(competition.date_end)}</dd></div>
        </dl>

        <div className="detail-actions">
          {canJoin && (
            <button type="button" className="btn btn--primary" disabled={joinLoading} onClick={handleJoin}>
              {joinLoading ? 'در حال پیوستن...' : 'پیوستن به مسابقه'}
            </button>
          )}
          {canStart && (
            <button type="button" className="btn btn--secondary" disabled={startLoading} onClick={handleStart}>
              {startLoading ? 'در حال شروع...' : 'شروع مسابقه'}
            </button>
          )}
          {competition.is_joined && (
            <span className="joined-badge">✓ شما در این مسابقه ثبت‌نام کرده‌اید</span>
          )}
        </div>
        {joinError && <div className="alert alert--error">{joinError}</div>}
        {startError && <div className="alert alert--error">{startError}</div>}
      </header>

      <div className="detail-grid">
        <section className="card">
          <div className="section-header">
            <h3>جدول امتیازات</h3>
            {isActive && <span className="live-badge">● زنده</span>}
          </div>
          <CompetitionLeaderboardTable entries={displayRankings} loading={lbLoading} />
        </section>

        {isCoach && (
          <ResultEntryForm
            competitionId={Number(id)}
            disabled={!isActive}
            onSuccess={handleResultSuccess}
          />
        )}
      </div>

      {isFinished && <CompetitionWinnersPanel rankings={finalRankings.length ? finalRankings : leaderboard} />}
    </div>
  );
}
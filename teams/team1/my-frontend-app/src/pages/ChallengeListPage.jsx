import { useCallback, useEffect, useState } from 'react';
import { fetchChallenges } from '../services/challenges';
import ChallengeCard from '../components/challenges/ChallengeCard';
import ChallengeFilters from '../components/challenges/ChallengeFilters';
import SystemFlowDiagram from '../components/shared/SystemFlowDiagram';
import BrandDivider from '../components/layout/BrandDivider';
import { parseApiError } from '../utils/formatters';

export default function ChallengeListPage() {
  const [challenges, setChallenges] = useState([]);
  const [filters, setFilters] = useState({ activity_type: '', difficulty: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (filters.activity_type) params.activity_type = filters.activity_type;
      if (filters.difficulty) params.difficulty = filters.difficulty;
      const data = await fetchChallenges(params);
      setChallenges(data.results ?? data);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="page">
      <section className="page-hero">
        <BrandDivider />
        <h1 className="page-title">چالش‌های ورزشی</h1>
        <BrandDivider />
        <p className="page-subtitle">
          چالش‌ها را بررسی کنید، ثبت‌نام کنید و فعالیت‌های روزانه خود را ثبت نمایید.
        </p>
      </section>

      <SystemFlowDiagram />

      <ChallengeFilters filters={filters} onChange={setFilters} />

      {error && <div className="alert alert--error">{error}</div>}

      {loading ? (
        <div className="loading-state">در حال بارگذاری چالش‌ها...</div>
      ) : challenges.length === 0 ? (
        <div className="empty-state">چالشی یافت نشد.</div>
      ) : (
        <div className="challenge-grid">
          {challenges.map((c) => (
            <ChallengeCard key={c.challenge_id} challenge={c} />
          ))}
        </div>
      )}
    </div>
  );
}

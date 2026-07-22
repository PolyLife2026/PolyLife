import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import CompetitionCard from '../components/competitions/CompetitionCard';
import BrandDivider from '../components/layout/BrandDivider';
import { fetchCompetitions } from '../services/competitions';
import { useAuth } from '../context/AuthContext';
import { parseApiError } from '../utils/formatters';

export default function CompetitionListPage() {
  const { isCoach } = useAuth();
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchCompetitions();
      setCompetitions(data.results ?? data);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="page">
      <section className="page-hero">
        <BrandDivider />
        <h1 className="page-title">مسابقات</h1>
        <BrandDivider />
        <p className="page-subtitle">
          مسابقات رقابتی را بررسی کنید و در رویدادهای فعال ثبت‌نام نمایید.
        </p>
        {isCoach && (
          <Link to="/competitions/new" className="btn btn--primary">+ ایجاد مسابقه</Link>
        )}
      </section>

      {error && <div className="alert alert--error">{error}</div>}

      {loading ? (
        <div className="loading-state">در حال بارگذاری مسابقات...</div>
      ) : competitions.length === 0 ? (
        <div className="empty-state">مسابقه‌ای یافت نشد.</div>
      ) : (
        <div className="challenge-grid">
          {competitions.map((c) => (
            <CompetitionCard key={c.competition_id} competition={c} />
          ))}
        </div>
      )}
    </div>
  );
}

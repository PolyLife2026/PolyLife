import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import CompetitionForm from '../components/competitions/CompetitionForm';
import { createCompetition } from '../services/competitions';
import { useAuth } from '../context/AuthContext';

export default function CreateCompetitionPage() {
  const navigate = useNavigate();
  const { isCoach } = useAuth();
  const [loading, setLoading] = useState(false);

  if (!isCoach) {
    return (
      <div className="page">
        <div className="alert alert--error">
          فقط مربیان می‌توانند مسابقه ایجاد کنند. نقش خود را در نوار بالا تغییر دهید.
        </div>
        <Link to="/competitions" className="back-link">→ بازگشت</Link>
      </div>
    );
  }

  async function handleSubmit(payload) {
    setLoading(true);
    try {
      const created = await createCompetition(payload);
      navigate(`/competitions/${created.competition_id}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <Link to="/competitions" className="back-link">→ بازگشت به لیست</Link>
      <h1 className="page-title">ایجاد مسابقه جدید</h1>
      <p className="page-subtitle">مربیان می‌توانند مسابقات رقابتی جدید تعریف کنند.</p>
      <CompetitionForm onSubmit={handleSubmit} loading={loading} submitLabel="ایجاد مسابقه" />
    </div>
  );
}

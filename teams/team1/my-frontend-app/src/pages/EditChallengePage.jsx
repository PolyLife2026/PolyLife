import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import ChallengeForm from '../components/challenges/ChallengeForm';
import { fetchChallenge, updateChallenge } from '../services/challenges';
import { useAuth } from '../context/AuthContext';
import { parseApiError } from '../utils/formatters';

export default function EditChallengePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isCoach, userId } = useAuth();
  const [challenge, setChallenge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchChallenge(id)
      .then(setChallenge)
      .catch((err) => setError(parseApiError(err)))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="loading-state page">در حال بارگذاری...</div>;

  if (!isCoach || String(challenge?.created_by) !== String(userId)) {
    return (
      <div className="page">
        <div className="alert alert--error">شما اجازه ویرایش این چالش را ندارید.</div>
        <Link to={`/challenges/${id}`} className="back-link">→ بازگشت</Link>
      </div>
    );
  }

  async function handleSubmit(payload) {
    setSaving(true);
    try {
      await updateChallenge(id, payload);
      navigate(`/challenges/${id}`);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page">
      <Link to={`/challenges/${id}`} className="back-link">→ بازگشت</Link>
      <h1 className="page-title">ویرایش چالش</h1>
      {error && <div className="alert alert--error">{error}</div>}
      <ChallengeForm
        initial={challenge}
        onSubmit={handleSubmit}
        loading={saving}
        submitLabel="ذخیره تغییرات"
      />
    </div>
  );
}

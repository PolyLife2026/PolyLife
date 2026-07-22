import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import ChallengeForm from '../components/challenges/ChallengeForm';
import { createChallenge } from '../services/challenges';
import { useAuth } from '../context/AuthContext';

export default function CreateChallengePage() {
  const navigate = useNavigate();
  const { isCoach } = useAuth();
  const [loading, setLoading] = useState(false);

  if (!isCoach) {
    return (
      <div className="page">
        <div className="alert alert--error">
          فقط مربیان می‌توانند چالش ایجاد کنند. نقش خود را در نوار بالا تغییر دهید.
        </div>
        <Link to="/challenges" className="back-link">→ بازگشت</Link>
      </div>
    );
  }

  async function handleSubmit(payload) {
    setLoading(true);
    try {
      const created = await createChallenge(payload);
      navigate(`/challenges/${created.challenge_id}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <Link to="/challenges" className="back-link">→ بازگشت به لیست</Link>
      <h1 className="page-title">ایجاد چالش جدید</h1>
      <p className="page-subtitle">مربیان می‌توانند چالش‌های ورزشی جدید تعریف کنند.</p>
      <ChallengeForm onSubmit={handleSubmit} loading={loading} submitLabel="ایجاد چالش" />
    </div>
  );
}

import { useState } from 'react';
import { recordCompetitionResult } from '../../services/competitions';
import { parseApiError } from '../../utils/formatters';

export default function ResultEntryForm({ competitionId, disabled, onSuccess }) {
  const [userId, setUserId] = useState('');
  const [score, setScore] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      await recordCompetitionResult(competitionId, {
        user_id: Number(userId),
        score: Number(score),
      });
      setSuccess('امتیاز ثبت شد و رتبه‌بندی به‌روزرسانی شد.');
      setUserId('');
      setScore('');
      onSuccess?.();
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="activity-form card result-entry-form" onSubmit={handleSubmit}>
      <h3>ثبت نتیجه شرکت‌کننده (مربی)</h3>
      <p className="form-hint">
        امتیاز هر شرکت‌کننده را ثبت کنید. رتبه‌بندی بلافاصله به‌روز می‌شود.
      </p>

      {disabled && (
        <div className="alert alert--warning">
          ثبت نتیجه فقط در مسابقات فعال امکان‌پذیر است.
        </div>
      )}

      {error && <div className="alert alert--error">{error}</div>}
      {success && <div className="alert alert--success">{success}</div>}

      <div className="form-grid">
        <label>
          شناسه کاربر
          <input
            type="number"
            min="1"
            required
            value={userId}
            disabled={disabled || loading}
            onChange={(e) => setUserId(e.target.value)}
          />
        </label>
        <label>
          امتیاز
          <input
            type="number"
            step="0.01"
            min="0"
            required
            value={score}
            disabled={disabled || loading}
            onChange={(e) => setScore(e.target.value)}
          />
        </label>
      </div>

      <button type="submit" className="btn btn--primary" disabled={disabled || loading}>
        {loading ? 'در حال ثبت...' : 'ثبت امتیاز'}
      </button>
    </form>
  );
}

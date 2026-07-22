import { useState } from 'react';
import { createActivity } from '../../services/activities';
import { todayISO, parseApiError } from '../../utils/formatters';
import { getGoalUnitLabel } from '../../utils/constants';

export default function ActivityForm({ challengeId, goalUnit, disabled, onSuccess }) {
  const [value, setValue] = useState('');
  const [activityDate, setActivityDate] = useState(todayISO());
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      await createActivity({
        challenge: challengeId,
        value,
        activity_date: activityDate,
        note: note || undefined,
      });
      setSuccess('فعالیت با موفقیت ثبت شد! امتیاز و رتبه به‌روزرسانی شد.');
      setValue('');
      setNote('');
      onSuccess?.();
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="activity-form card" onSubmit={handleSubmit}>
      <h3>ثبت فعالیت روزانه</h3>
      <p className="form-hint">
        فعالیت را در همان روز انجام فعالیت ثبت کنید. پس از ثبت، امتیاز و رتبه به‌صورت خودکار به‌روز می‌شود.
      </p>

      {disabled && (
        <div className="alert alert--warning">
          این چالش فعال نیست یا به پایان رسیده — ثبت فعالیت غیرفعال است.
        </div>
      )}

      {error && <div className="alert alert--error">{error}</div>}
      {success && <div className="alert alert--success">{success}</div>}

      <div className="form-grid">
        <label>
          مقدار ({getGoalUnitLabel(goalUnit)})
          <input
            type="number"
            step="0.01"
            min="0.01"
            required
            value={value}
            disabled={disabled || loading}
            onChange={(e) => setValue(e.target.value)}
            placeholder="مثلاً ۵"
          />
        </label>
        <label>
          تاریخ فعالیت
          <input
            type="date"
            required
            value={activityDate}
            disabled={disabled || loading}
            onChange={(e) => setActivityDate(e.target.value)}
          />
        </label>
        <label className="form-grid__full">
          یادداشت (اختیاری)
          <input
            type="text"
            maxLength={255}
            value={note}
            disabled={disabled || loading}
            onChange={(e) => setNote(e.target.value)}
            placeholder="مثلاً: دویدن صبحگاهی"
          />
        </label>
      </div>

      <button type="submit" className="btn btn--primary" disabled={disabled || loading}>
        {loading ? 'در حال ثبت...' : 'ثبت فعالیت'}
      </button>
    </form>
  );
}

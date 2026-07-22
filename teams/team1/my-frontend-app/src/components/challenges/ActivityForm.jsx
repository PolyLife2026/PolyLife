import { useState } from 'react';
import { createActivity, updateActivity } from '../../services/activities';
import { todayISO, parseApiError } from '../../utils/formatters';
import { getGoalUnitLabel } from '../../utils/constants';

export default function ActivityForm({ challengeId, goalUnit, disabled, onSuccess }) {
  const [value, setValue] = useState('');
  const [activityDate, setActivityDate] = useState(todayISO());
  const [note, setNote] = useState('');
  const [todayActivityId, setTodayActivityId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const isEditingToday = todayActivityId && activityDate === todayISO();

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      const payload = {
        challenge: challengeId,
        value,
        activity_date: activityDate,
        note: note || undefined,
      };

      if (isEditingToday) {
        await updateActivity(todayActivityId, payload);
        setSuccess('فعالیت امروز ویرایش شد! امتیاز و رتبه به‌روزرسانی شد.');
      } else {
        const created = await createActivity(payload);
        if (activityDate === todayISO() && created?.activity_id) {
          setTodayActivityId(created.activity_id);
        }
        setSuccess('فعالیت با موفقیت ثبت شد! امتیاز و رتبه به‌روزرسانی شد.');
      }
      onSuccess?.();
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }

  function handleDateChange(nextDate) {
    setActivityDate(nextDate);
    if (nextDate !== todayISO()) {
      setTodayActivityId(null);
    }
  }

  return (
    <form className="activity-form card" onSubmit={handleSubmit}>
      <h3>{isEditingToday ? 'ویرایش فعالیت امروز' : 'ثبت فعالیت روزانه'}</h3>
      <p className="form-hint">
        فعالیت را در همان روز انجام فعالیت ثبت یا ویرایش کنید. پس از هر تغییر، امتیاز و رتبه به‌صورت خودکار به‌روز می‌شود.
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
            disabled={disabled || loading || isEditingToday}
            onChange={(e) => handleDateChange(e.target.value)}
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
        {loading
          ? 'در حال ذخیره...'
          : isEditingToday
            ? 'ذخیره ویرایش'
            : 'ثبت فعالیت'}
      </button>
    </form>
  );
}

import { useState } from 'react';
import {
  ACTIVITY_TYPES,
  DIFFICULTIES,
  GOAL_UNITS,
} from '../../utils/constants';
import { toInputDateTime } from '../../utils/formatters';

const EMPTY = {
  title: '',
  description: '',
  activity_type: 'running',
  difficulty: 'medium',
  value_goal: '',
  goal_unit: 'km',
  date_start: '',
  date_end: '',
};

export default function ChallengeForm({ initial, onSubmit, loading, submitLabel = 'ذخیره' }) {
  const [form, setForm] = useState(() => ({
    ...EMPTY,
    ...initial,
    value_goal: initial?.value_goal ?? '',
    date_start: initial?.date_start ? toInputDateTime(initial.date_start) : '',
    date_end: initial?.date_end ? toInputDateTime(initial.date_end) : '',
  }));
  const [error, setError] = useState('');

  function updateField(key, val) {
    setForm((prev) => ({ ...prev, [key]: val }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    try {
      await onSubmit({
        title: form.title,
        description: form.description || null,
        activity_type: form.activity_type,
        difficulty: form.difficulty,
        value_goal: form.value_goal,
        goal_unit: form.goal_unit,
        date_start: new Date(form.date_start).toISOString(),
        date_end: new Date(form.date_end).toISOString(),
      });
    } catch (err) {
      const data = err?.response?.data;
      if (typeof data === 'object') {
        setError(Object.values(data).flat().join(' | '));
      } else {
        setError(err?.message ?? 'خطا در ذخیره');
      }
    }
  }

  return (
    <form className="challenge-form card" onSubmit={handleSubmit}>
      {error && <div className="alert alert--error">{error}</div>}

      <div className="form-grid">
        <label className="form-grid__full">
          عنوان چالش
          <input
            required
            maxLength={100}
            value={form.title}
            onChange={(e) => updateField('title', e.target.value)}
          />
        </label>
        <label className="form-grid__full">
          توضیحات
          <textarea
            rows={3}
            value={form.description}
            onChange={(e) => updateField('description', e.target.value)}
          />
        </label>
        <label>
          نوع فعالیت
          <select value={form.activity_type} onChange={(e) => updateField('activity_type', e.target.value)}>
            {ACTIVITY_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </label>
        <label>
          سطح دشواری
          <select value={form.difficulty} onChange={(e) => updateField('difficulty', e.target.value)}>
            {DIFFICULTIES.map((d) => (
              <option key={d.value} value={d.value}>{d.label}</option>
            ))}
          </select>
        </label>
        <label>
          هدف
          <input
            type="number"
            step="0.01"
            min="0.01"
            required
            value={form.value_goal}
            onChange={(e) => updateField('value_goal', e.target.value)}
          />
        </label>
        <label>
          واحد هدف
          <select value={form.goal_unit} onChange={(e) => updateField('goal_unit', e.target.value)}>
            {GOAL_UNITS.map((u) => (
              <option key={u.value} value={u.value}>{u.label}</option>
            ))}
          </select>
        </label>
        <label>
          تاریخ شروع
          <input
            type="datetime-local"
            required
            value={form.date_start}
            onChange={(e) => updateField('date_start', e.target.value)}
          />
        </label>
        <label>
          تاریخ پایان
          <input
            type="datetime-local"
            required
            value={form.date_end}
            onChange={(e) => updateField('date_end', e.target.value)}
          />
        </label>
      </div>

      <button type="submit" className="btn btn--primary" disabled={loading}>
        {loading ? 'در حال ذخیره...' : submitLabel}
      </button>
    </form>
  );
}

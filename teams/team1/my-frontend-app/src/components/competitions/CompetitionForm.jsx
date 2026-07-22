import { useState } from 'react';
import { COMPETITION_TYPES } from '../../utils/constants';
import { toInputDateTime } from '../../utils/formatters';

const EMPTY = {
  title: '',
  description: '',
  rules: '',
  competition_type: 'weight_loss',
  date_start: '',
  date_end: '',
};

export default function CompetitionForm({ initial, onSubmit, loading, submitLabel = 'ذخیره' }) {
  const [form, setForm] = useState(() => ({
    ...EMPTY,
    ...initial,
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
        rules: form.rules || null,
        competition_type: form.competition_type,
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
    <form className="challenge-form card competition-form" onSubmit={handleSubmit}>
      {error && <div className="alert alert--error">{error}</div>}

      <div className="form-grid">
        <label className="form-grid__full">
          عنوان مسابقه
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
        <label className="form-grid__full">
          قوانین
          <textarea
            rows={3}
            value={form.rules}
            onChange={(e) => updateField('rules', e.target.value)}
            placeholder="قوانین و معیارهای امتیازدهی"
          />
        </label>
        <label>
          نوع مسابقه
          <select value={form.competition_type} onChange={(e) => updateField('competition_type', e.target.value)}>
            {COMPETITION_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
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

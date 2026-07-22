import { ACTIVITY_TYPES, DIFFICULTIES } from '../../utils/constants';

export default function ChallengeFilters({ filters, onChange }) {
  return (
    <div className="filters-bar">
      <label>
        نوع فعالیت
        <select
          value={filters.activity_type}
          onChange={(e) => onChange({ ...filters, activity_type: e.target.value })}
        >
          <option value="">همه</option>
          {ACTIVITY_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </label>
      <label>
        سطح دشواری
        <select
          value={filters.difficulty}
          onChange={(e) => onChange({ ...filters, difficulty: e.target.value })}
        >
          <option value="">همه</option>
          {DIFFICULTIES.map((d) => (
            <option key={d.value} value={d.value}>{d.label}</option>
          ))}
        </select>
      </label>
    </div>
  );
}

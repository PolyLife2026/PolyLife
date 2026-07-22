import { formatDateTime } from '../../utils/formatters';

export default function ParticipantsList({ participants }) {
  if (!participants?.length) {
    return (
      <div className="participants-list">
        <h3>شرکت‌کنندگان</h3>
        <p className="form-hint">هنوز کسی در این چالش ثبت‌نام نکرده است.</p>
      </div>
    );
  }

  return (
    <div className="participants-list">
      <h3>شرکت‌کنندگان ({participants.length})</h3>
      <ul className="participants-list__items">
        {participants.map((p) => (
          <li key={p.user_id} className="participants-list__item">
            <span className="participants-list__user">کاربر #{p.user_id}</span>
            <span className="participants-list__date">{formatDateTime(p.joined_at)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

import { getStatusLabel } from '../../utils/constants';

const STATUS_CLASS = {
  created: 'status--created',
  started: 'status--started',
  ended: 'status--ended',
  cancelled: 'status--cancelled',
};

export default function StatusBadge({ status }) {
  return (
    <span className={`status-badge ${STATUS_CLASS[status] ?? ''}`}>
      {getStatusLabel(status)}
    </span>
  );
}

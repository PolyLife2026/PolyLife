import { getCompetitionStatusLabel } from '../../utils/constants';

export default function CompetitionStatusBadge({ status }) {
  return (
    <span className={`status-badge status--competition-${status}`}>
      {getCompetitionStatusLabel(status)}
    </span>
  );
}

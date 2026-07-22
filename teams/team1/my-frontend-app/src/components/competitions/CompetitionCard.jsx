import { Link } from 'react-router-dom';
import CompetitionStatusBadge from './CompetitionStatusBadge';
import { getCompetitionTypeLabel } from '../../utils/constants';
import { formatDate } from '../../utils/formatters';

export default function CompetitionCard({ competition }) {
  return (
    <article className="challenge-card competition-card">
      <div className="challenge-card__header">
        <h3>{competition.title}</h3>
        <CompetitionStatusBadge status={competition.status} />
      </div>
      <p className="competition-card__type">{getCompetitionTypeLabel(competition.competition_type)}</p>
      <div className="challenge-card__dates">
        <span>{formatDate(competition.date_start)}</span>
        <span className="date-sep">←</span>
        <span>{formatDate(competition.date_end)}</span>
      </div>
      <Link to={`/competitions/${competition.competition_id}`} className="btn btn--primary btn--block">
        مشاهده مسابقه
      </Link>
    </article>
  );
}

import { Link } from 'react-router-dom';
import StatusBadge from './StatusBadge';
import { formatDate } from '../../utils/formatters';

export default function ChallengeCard({ challenge }) {
  return (
    <article className="challenge-card">
      <div className="challenge-card__header">
        <h3>{challenge.title}</h3>
        <StatusBadge status={challenge.status} />
      </div>
      <div className="challenge-card__dates">
        <span>{formatDate(challenge.date_start)}</span>
        <span className="date-sep">←</span>
        <span>{formatDate(challenge.date_end)}</span>
      </div>
      <Link to={`/challenges/${challenge.challenge_id}`} className="btn btn--primary btn--block">
        مشاهده جزئیات
      </Link>
    </article>
  );
}

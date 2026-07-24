import { USER_JOURNEY_STEPS } from '../../utils/constants';

export default function UserJourney() {
  return (
    <section className="user-journey card">
      <h2>مسیر کاربر در برنامه</h2>
      <ol className="user-journey__list">
        {USER_JOURNEY_STEPS.map((step, index) => (
          <li key={step.title} className="user-journey__item">
            <span className="user-journey__num">{index + 1}</span>
            <div>
              <strong>{step.title}</strong>
              <p>{step.desc}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}

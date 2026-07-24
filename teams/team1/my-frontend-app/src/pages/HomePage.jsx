import { Link } from 'react-router-dom';
import BrandDivider from '../components/layout/BrandDivider';
import SystemFlowDiagram from '../components/shared/SystemFlowDiagram';
import UserJourney from '../components/shared/UserJourney';
import { useAuth } from '../context/AuthContext';

export default function HomePage() {
  const { isCoach } = useAuth();

  return (
    <div className="page home-page">
      <section className="page-hero home-hero">
        <BrandDivider />
        <h1 className="page-title">PolyLife</h1>
        <BrandDivider />
        <p className="page-subtitle">
          سیستم چالش‌های ورزشی و مسابقات رقابتی — پیوستن، ثبت فعالیت، رتبه‌بندی لحظه‌ای و دریافت جوایز
        </p>
      </section>

      <section className="home-sections">
        <article className="home-section-card home-section-card--challenge">
          <h2>چالش‌های ورزشی</h2>
          <p>
            رویدادهایی که کاربران در آن‌ها شرکت کرده و فعالیت‌های روزانه خود را ثبت می‌کنند.
          </p>
          <div className="home-section-actions">
            <Link to="/challenges" className="btn btn--primary">مشاهده چالش‌ها</Link>
            {isCoach && (
              <Link to="/challenges/new" className="btn btn--secondary">ایجاد چالش</Link>
            )}
          </div>
        </article>

        <article className="home-section-card home-section-card--competition">
          <h2>مسابقات</h2>
          <p>
            رویدادهای رقابتی (کاهش وزن، بیشترین فعالیت، ثبت رکورد) که توسط مربیان تعریف می‌شوند.
          </p>
          <div className="home-section-actions">
            <Link to="/competitions" className="btn btn--primary">مشاهده مسابقات</Link>
            {isCoach && (
              <Link to="/competitions/new" className="btn btn--secondary">ایجاد مسابقه</Link>
            )}
          </div>
        </article>
      </section>

      <SystemFlowDiagram />
      <UserJourney />
    </div>
  );
}

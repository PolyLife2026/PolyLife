import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import BrandDivider from './BrandDivider';

export default function Header() {
  const { userId, role, isCoach, setUserId, setRole } = useAuth();

  return (
    <header className="site-header">
      <div className="header-top">
        <Link to="/" className="logo-link">
          <BrandDivider compact />
          <span className="logo-text">PolyLife</span>
          <BrandDivider compact />
        </Link>
        <nav className="main-nav">
          <Link to="/">خانه</Link>
          <Link to="/challenges">چالش‌ها</Link>
          <Link to="/competitions">مسابقات</Link>
          {isCoach && (
            <>
              <Link to="/challenges/new">ایجاد چالش</Link>
              <Link to="/competitions/new">ایجاد مسابقه</Link>
            </>
          )}
        </nav>
      </div>

      <div className="dev-auth-bar">
        <span className="dev-label">حالت توسعه:</span>
        <label>
          شناسه کاربر
          <input
            type="number"
            min="1"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />
        </label>
        <label>
          نقش
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="participant">شرکت‌کننده</option>
            <option value="coach">مربی</option>
          </select>
        </label>
      </div>
    </header>
  );
}

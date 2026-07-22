import { Outlet } from 'react-router-dom';
import Header from './Header';

export default function Layout() {
  return (
    <div className="app-shell">
      <Header />
      <main className="main-content">
        <Outlet />
      </main>
      <footer className="site-footer">
        <p>PolyLife — چالش‌های ورزشی و مسابقات رقابتی</p>
      </footer>
    </div>
  );
}

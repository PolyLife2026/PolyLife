import { FlameIcon } from '../components/Icons'

export default function Results({ profile, onEdit, onStart }) {
  return (
    <div className="screen-simple">
      <div style={{ textAlign: 'center' }}>
        <h1>نتایج و اهداف روزانه</h1>
        <p className="muted">بر اساس اطلاعاتی که وارد کردی محاسبه شد</p>
      </div>

      <div
        className="card"
        style={{
          textAlign: 'center',
          padding: '26px 16px',
          background: 'var(--teal-dark)',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 6,
            color: 'var(--cyan-light)',
          }}
        >
          <FlameIcon size={18} />
          <span style={{ fontSize: 13, fontWeight: 600 }}>کالری مجاز روزانه</span>
        </div>
        <div style={{ fontSize: 42, fontWeight: 800, color: 'var(--white)', margin: '6px 0 0' }}>
          {profile.target_calories ?? '—'}
        </div>
      </div>

      <div className="stat-row">
        <div className="stat-box">
          <div className="stat-value">{profile.bmi ?? '—'}</div>
          <div className="stat-label">BMI</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{profile.bmr ?? '—'}</div>
          <div className="stat-label">BMR</div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <button onClick={onStart}>شروع ثبت وعده‌ها</button>
        <button className="ghost" onClick={onEdit}>
          ویرایش اطلاعات
        </button>
      </div>
    </div>
  )
}

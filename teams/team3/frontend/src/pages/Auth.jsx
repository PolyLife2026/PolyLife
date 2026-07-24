import { useState } from 'react'
import { auth } from '../api'
import { FlameIcon } from '../components/Icons'

export default function Auth({ onLoggedIn }) {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (mode === 'register') {
        await auth.register(username, password)
      }
      await auth.login(username, password)
      onLoggedIn()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="screen-simple">
      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            width: 64, height: 64, borderRadius: 20, margin: '0 auto 14px',
            background: 'linear-gradient(135deg, var(--teal-dark), var(--teal-darker))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'var(--white)',
          }}
        >
          <FlameIcon size={30} />
        </div>
        <h1>PolyLife</h1>
        <p className="muted">کالری‌شمار و مدیریت وعده‌های غذایی</p>
      </div>

      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <h2 style={{ textAlign: 'center' }}>{mode === 'login' ? 'ورود' : 'ثبت‌نام'}</h2>
        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div>
            <label>نام کاربری</label>
            <input
              placeholder="نام کاربری"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div>
            <label>رمز عبور</label>
            <input
              placeholder="رمز عبور"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="error">{error}</div>}
          <button type="submit" disabled={loading}>
            {loading ? 'در حال ارسال...' : mode === 'login' ? 'ورود' : 'ثبت‌نام'}
          </button>
        </form>
        <button
          className="ghost"
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
        >
          {mode === 'login' ? 'حساب نداری؟ ثبت‌نام کن' : 'قبلاً ثبت‌نام کردی؟ وارد شو'}
        </button>
      </div>
    </div>
  )
}

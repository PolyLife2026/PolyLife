import { useState } from 'react'
import { apiFetch } from '../api'

export default function HealthForm({ goal, onDone }) {
  const [height, setHeight] = useState('')
  const [weight, setWeight] = useState('')
  const [age, setAge] = useState('')
  const [gender, setGender] = useState('male')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const result = await apiFetch('/health-profile/', {
        method: 'POST',
        body: JSON.stringify({
          height: Number(height),
          weight: Number(weight),
          age: Number(age),
          gender,
          goal,
        }),
      })
      onDone(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="screen-simple">
      <div style={{ textAlign: "center" }}>
        <h1>اطلاعات سلامت</h1>
        <p className="muted">این‌ها فقط برای محاسبه‌ی دقیق کالری مجازت لازمه</p>
      </div>
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div>
            <label>قد (سانتی‌متر)</label>
            <input
              placeholder="مثلاً ۱۷۵"
              type="number"
              value={height}
              onChange={(e) => setHeight(e.target.value)}
              required
            />
          </div>
          <div>
            <label>وزن (کیلوگرم)</label>
            <input
              placeholder="مثلاً ۷۰"
              type="number"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              required
            />
          </div>
          <div>
            <label>سن</label>
            <input
              placeholder="مثلاً ۲۵"
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              required
            />
          </div>
          <div>
            <label>جنسیت</label>
            <select value={gender} onChange={(e) => setGender(e.target.value)}>
              <option value="male">مرد</option>
              <option value="female">زن</option>
            </select>
          </div>
          {error && <div className="error">{error}</div>}
          <button type="submit" disabled={loading}>
            {loading ? 'در حال محاسبه...' : 'ثبت'}
          </button>
        </form>
      </div>
    </div>
  )
}

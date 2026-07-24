import { useState } from 'react'

const GOALS = [
  { value: 'lose', label: 'کاهش وزن' },
  { value: 'gain', label: 'افزایش وزن' },
  { value: 'maintain', label: 'تثبیت وزن' },
]

export default function GoalSelect({ onNext }) {
  const [selected, setSelected] = useState(null)

  return (
    <div className="screen-simple">
      <div style={{ textAlign: "center" }}>
        <h1>هدف شما چیه؟</h1>
        <p className="muted">بر اساس این، برنامه‌ی کالری روزانه‌ات رو می‌چینیم</p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {GOALS.map((g) => (
          <button
            key={g.value}
            className={`goal-btn ${selected === g.value ? 'selected' : ''}`}
            onClick={() => setSelected(g.value)}
          >
            {g.label}
          </button>
        ))}
      </div>
      <button disabled={!selected} onClick={() => onNext(selected)}>
        شروع
      </button>
    </div>
  )
}

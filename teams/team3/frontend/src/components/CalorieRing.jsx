export default function CalorieRing({ consumed = 0, target = 2000, size = 180 }) {
  const percent = target > 0 ? Math.min((consumed / target) * 100, 100) : 0
  const overTarget = target > 0 && consumed > target

  const stroke = 16
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const dash = (percent / 100) * circumference

  const ringColor = overTarget ? '#E4572E' : 'var(--teal-dark)'

  return (
    <div style={{ position: 'relative', width: size, height: size, margin: '0 auto' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--gray)"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={ringColor}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${circumference - dash}`}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: 'stroke-dasharray 0.4s ease' }}
        />
      </svg>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <span style={{ fontSize: 26, fontWeight: 700, color: 'var(--teal-dark)' }}>
          {Math.round(consumed)}
        </span>
        <span style={{ fontSize: 12, color: '#7a7a7a' }}>از {Math.round(target)} کالری</span>
        {overTarget && (
          <span style={{ fontSize: 11, color: '#E4572E', fontWeight: 600, marginTop: 2 }}>
            بیش از حد مجاز
          </span>
        )}
      </div>
    </div>
  )
}

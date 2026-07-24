import { useEffect, useMemo, useState } from 'react'
import { apiFetch } from '../api'

const MEAL_TYPES = [
  { value: 'breakfast', label: 'صبحانه' },
  { value: 'lunch', label: 'ناهار' },
  { value: 'dinner', label: 'شام' },
  { value: 'snack', label: 'میان‌وعده' },
]

// Must match FoodItem.CATEGORY_CHOICES in team3/team3/models.py exactly.
const CATEGORIES = [
  { value: '', label: 'همه' },
  { value: 'iranian', label: 'ایرانی' },
  { value: 'western', label: 'فرنگی' },
  { value: 'fruit', label: 'میوه' },
  { value: 'dairy', label: 'لبنیات' },
  { value: 'drink', label: 'نوشیدنی' },
  { value: 'snack', label: 'تنقلات' },
  { value: 'other', label: 'سایر' },
]

function today() {
  return new Date().toISOString().slice(0, 10)
}

function StarIcon({ filled }) {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill={filled ? 'var(--gold)' : 'none'}
      stroke={filled ? 'var(--gold)' : 'var(--teal-dark)'}
      strokeWidth="1.6"
    >
      <path d="M12 2.5 15.09 9l7.16.63-5.4 4.72L18.5 21.4 12 17.6 5.5 21.4l1.65-6.05-5.4-4.72L8.91 9z" strokeLinejoin="round" />
    </svg>
  )
}

function PlusIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
      <path d="M12 5v14M5 12h14" />
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m-9 0 1 12a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1l1-12" />
    </svg>
  )
}

/** Circular calorie-progress gauge, drawn with a plain SVG arc (no chart library needed). */
function CalorieRing({ consumed, target }) {
  const size = 176
  const stroke = 16
  const r = (size - stroke) / 2
  const circumference = 2 * Math.PI * r
  const ratio = target > 0 ? Math.min(consumed / target, 1) : 0
  const over = target > 0 && consumed > target
  const offset = circumference * (1 - ratio)

  return (
    <div className="ring-wrap">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--gray)" strokeWidth={stroke} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={over ? '#c0392b' : 'var(--teal-dark)'}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: 'stroke-dashoffset 0.4s ease' }}
        />
      </svg>
      <div className="ring-center">
        <strong>{consumed}</strong>
        <span>از {target} کالری</span>
      </div>
    </div>
  )
}

/**
 * Each food always has a real 'گرم' FoodUnit row (grams_per_unit = 1) plus
 * optional human units (بشقاب/لیوان/عدد/...). We just let the user pick
 * whichever FoodUnit they want from that list — no special-casing needed.
 */
function FoodRow({ food, isFavorite, onToggleFavorite, onAdd }) {
  const [unitId, setUnitId] = useState(food.units[0]?.id || '')
  const [qty, setQty] = useState(1)

  return (
    <div className="food-row">
      <button
        className="icon-btn star"
        onClick={() => onToggleFavorite(food)}
        title="افزودن به علاقه‌مندی‌ها"
        type="button"
      >
        <StarIcon filled={isFavorite} />
      </button>

      <div className="food-row-main">
        <div className="food-row-name">{food.name}</div>
        <div className="food-row-sub">
          {food.calories} کالری / ۱۰۰ گرم · {food.category_label}
        </div>
      </div>

      <input
        type="number"
        min="0"
        step="0.5"
        className="qty-input"
        value={qty}
        onChange={(e) => setQty(e.target.value)}
      />
      <select className="unit-select" value={unitId} onChange={(e) => setUnitId(e.target.value)}>
        {food.units.map((u) => (
          <option key={u.id} value={u.id}>
            {u.unit_name}
          </option>
        ))}
      </select>

      <button
        className="icon-btn add"
        onClick={() => onAdd(food, qty, unitId)}
        title="افزودن به وعده"
        type="button"
      >
        <PlusIcon />
      </button>
    </div>
  )
}

/** Tab 1: purely for finding and adding foods to today's log. */
function MealsTab({ isFavorite, toggleFavorite, onLogged }) {
  const [category, setCategory] = useState('')
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [mealType, setMealType] = useState('breakfast')
  const [error, setError] = useState('')
  const [confirmMsg, setConfirmMsg] = useState('')
  const [showManual, setShowManual] = useState(false)
  const [manualName, setManualName] = useState('')
  const [manualCalories, setManualCalories] = useState('')

  async function search(q, cat) {
    if (q.trim().length < 2 && !cat) {
      setResults([])
      return
    }
    try {
      const params = new URLSearchParams()
      if (q.trim().length >= 2) params.set('q', q.trim())
      if (cat) params.set('category', cat)
      const data = await apiFetch(`/food-items/search/?${params.toString()}`)
      setResults(data)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    search(query, category)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category])

  function flashConfirm(name) {
    setConfirmMsg(`«${name}» به وعده اضافه شد ✓`)
    setTimeout(() => setConfirmMsg(''), 2000)
  }

  async function addFood(food, qty, unitId) {
    setError('')
    const unit = food.units.find((u) => u.id === unitId)
    try {
      const body = { food_item_id: food.id, meal_type: mealType, log_date: today() }
      if (unit && unit.unit_name === 'گرم') {
        // 'گرم' is grams_per_unit=1, so quantity IS the gram amount directly.
        body.quantity_grams = Number(qty)
      } else {
        body.unit_id = unitId
        body.unit_quantity = Number(qty)
      }
      await apiFetch('/meal-logs/', { method: 'POST', body: JSON.stringify(body) })
      flashConfirm(food.name)
      onLogged()
    } catch (err) {
      setError(err.message)
    }
  }

  async function addManual() {
    setError('')
    if (!manualCalories) {
      setError('مقدار کالری را وارد کنید.')
      return
    }
    try {
      await apiFetch('/meal-logs/quick-add/', {
        method: 'POST',
        body: JSON.stringify({
          name: manualName,
          calories: Number(manualCalories),
          meal_type: mealType,
          log_date: today(),
        }),
      })
      flashConfirm(manualName || 'خوراکی دستی')
      setManualName('')
      setManualCalories('')
      setShowManual(false)
      onLogged()
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleToggleFavorite(food) {
    // optimistic UI update on the currently-shown results list
    setResults((prev) => prev.map((f) => (f.id === food.id ? { ...f, is_favorite: !f.is_favorite } : f)))
    await toggleFavorite(food)
  }

  return (
    <div className="tab-stack">
      <div className="meal-type-row">
        {MEAL_TYPES.map((m) => (
          <button
            key={m.value}
            className={`chip ${mealType === m.value ? 'chip-active' : ''}`}
            onClick={() => setMealType(m.value)}
            type="button"
          >
            {m.label}
          </button>
        ))}
      </div>

      <div className="search-box">
        <input
          placeholder="جستجوی غذا... (مثلا قرمه سبزی)"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            search(e.target.value, category)
          }}
        />
      </div>

      <div className="category-row">
        {CATEGORIES.map((c) => (
          <button
            key={c.value}
            className={`chip chip-outline ${category === c.value ? 'chip-active' : ''}`}
            onClick={() => setCategory(c.value)}
            type="button"
          >
            {c.label}
          </button>
        ))}
      </div>

      {confirmMsg && <div className="confirm-toast">{confirmMsg}</div>}
      {error && <div className="error">{error}</div>}

      {results.length > 0 ? (
        <div className="card food-list">
          {results.map((f) => (
            <FoodRow
              key={f.id}
              food={f}
              isFavorite={isFavorite(f.id, f.is_favorite)}
              onToggleFavorite={handleToggleFavorite}
              onAdd={addFood}
            />
          ))}
        </div>
      ) : (
        <p className="muted">
          یک دسته را از بالا انتخاب کنید (مثلا «ایرانی») یا نام غذا را جستجو کنید تا نتایج و ستاره‌ی علاقه‌مندی نمایش داده شود.
        </p>
      )}

      <button type="button" className="link-btn" onClick={() => setShowManual((s) => !s)}>
        {showManual ? 'بستن ثبت دستی' : '+ غذای من در لیست نیست، ثبت دستی'}
      </button>

      {showManual && (
        <div className="card manual-add">
          <input
            placeholder="نام غذا (اختیاری)"
            value={manualName}
            onChange={(e) => setManualName(e.target.value)}
          />
          <div className="manual-row">
            <input
              type="number"
              placeholder="کالری کل"
              value={manualCalories}
              onChange={(e) => setManualCalories(e.target.value)}
            />
            <button type="button" onClick={addManual}>
              ثبت
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

/** Tab 2: the ring chart AND the itemized list of everything logged today. */
function ChartTab({ refreshKey }) {
  const [daily, setDaily] = useState(null)
  const [mealLog, setMealLog] = useState(null)
  const [error, setError] = useState('')

  async function load() {
    try {
      const [dailyData, mealLogData] = await Promise.all([
        apiFetch(`/dashboard/daily/?date=${today()}`),
        apiFetch(`/meal-logs/?date=${today()}`),
      ])
      setDaily(dailyData)
      setMealLog(mealLogData)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey])

  async function removeItem(itemId) {
    try {
      await apiFetch(`/meal-logs/items/${itemId}/`, { method: 'DELETE' })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  if (error) return <div className="error">{error}</div>
  if (!daily) return <p className="muted">در حال بارگذاری...</p>

  return (
    <div className="tab-stack">
      <div className="card ring-card">
        <CalorieRing consumed={daily.total_calories} target={daily.target_calories} />
        <div className="ring-stats">
          <div>
            <span className="stat-label">کالری مجاز</span>
            <strong>{daily.target_calories}</strong>
          </div>
          <div>
            <span className="stat-label">مصرف‌شده</span>
            <strong>{daily.total_calories}</strong>
          </div>
          <div>
            <span className="stat-label">باقی‌مانده</span>
            <strong className={daily.remaining_calories < 0 ? 'neg' : ''}>{daily.remaining_calories}</strong>
          </div>
        </div>
      </div>

      {daily.over_target && <div className="warning">⚠ شما از حد مجاز کالری روزانه عبور کرده‌اید.</div>}

      <h2>وعده‌های امروز</h2>
      {mealLog && mealLog.items && mealLog.items.length > 0 ? (
        <div className="card food-list">
          {mealLog.items.map((item) => (
            <div className="food-row logged-row" key={item.id}>
              <div className="food-row-main">
                <div className="food-row-name">
                  {item.note || (item.food_item.name === 'Quick Add (manual calorie entry)' ? 'خوراکی دستی' : item.food_item.name)}
                </div>
                <div className="food-row-sub">
                  {item.unit_quantity} {item.unit_name} · {item.consumed_calories} کالری
                </div>
              </div>
              <button className="icon-btn danger" onClick={() => removeItem(item.id)} type="button">
                <TrashIcon />
              </button>
            </div>
          ))}
          <p className="total-line">مجموع: {mealLog.total_calories} کالری</p>
        </div>
      ) : (
        <p className="muted">هنوز چیزی ثبت نشده.</p>
      )}
    </div>
  )
}

function FavoritesTab({ favorites, loading, onRemove }) {
  return (
    <div className="tab-stack">
      {loading && <p className="muted">در حال بارگذاری...</p>}
      {!loading && favorites.length === 0 && (
        <p className="muted">
          لیست علاقه‌مندی‌ها خالی است. برای اضافه کردن، توی تب «انتخاب غذا» روی ستاره‌ی کنار هر غذا بزنید.
        </p>
      )}
      {favorites.length > 0 && (
        <div className="card food-list">
          {favorites.map((f) => (
            <div className="food-row logged-row" key={f.id}>
              <StarIcon filled />
              <div className="food-row-main">
                <div className="food-row-name">{f.food_item.name}</div>
                <div className="food-row-sub">{f.food_item.calories} کالری / ۱۰۰ گرم</div>
              </div>
              <button className="icon-btn danger" onClick={() => onRemove(f.id)} type="button">
                <TrashIcon />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function Dashboard() {
  const [tab, setTab] = useState('meals')
  const [favorites, setFavorites] = useState([])
  const [favLoading, setFavLoading] = useState(true)
  const [refreshKey, setRefreshKey] = useState(0)
  // Tracks foods whose favorite state we've flipped locally via /favorites/toggle/,
  // used as an override on top of whatever the search API said `is_favorite` was.
  const [localOverrides, setLocalOverrides] = useState({})

  async function loadFavorites() {
    setFavLoading(true)
    try {
      const data = await apiFetch('/favorites/')
      setFavorites(data)
    } catch (e) {
      // favorites are non-critical — fail silently and keep the rest of the UI usable
    } finally {
      setFavLoading(false)
    }
  }

  useEffect(() => {
    loadFavorites()
  }, [])

  const favoriteFoodIds = useMemo(() => new Set(favorites.map((f) => f.food_item.id)), [favorites])

  function isFavorite(foodId, serverIsFavorite) {
    if (foodId in localOverrides) return localOverrides[foodId]
    if (typeof serverIsFavorite === 'boolean') return serverIsFavorite
    return favoriteFoodIds.has(foodId)
  }

  async function toggleFavorite(food) {
    try {
      const result = await apiFetch('/favorites/toggle/', {
        method: 'POST',
        body: JSON.stringify({ food_item_id: food.id }),
      })
      setLocalOverrides((prev) => ({ ...prev, [food.id]: result.is_favorite }))
      await loadFavorites()
    } catch (e) {
      // revert optimistic UI if the request actually failed
      setLocalOverrides((prev) => ({ ...prev, [food.id]: !prev[food.id] }))
    }
  }

  async function removeFavoriteById(favoriteId) {
    try {
      await apiFetch(`/favorites/${favoriteId}/`, { method: 'DELETE' })
      await loadFavorites()
    } catch (e) {
      // ignore
    }
  }

  return (
    <div className="screen dashboard-screen">
      <h2>مدیریت وعده‌های روزانه</h2>

      {tab === 'meals' && (
        <MealsTab
          isFavorite={isFavorite}
          toggleFavorite={toggleFavorite}
          onLogged={() => setRefreshKey((k) => k + 1)}
        />
      )}
      {tab === 'chart' && <ChartTab refreshKey={refreshKey} />}
      {tab === 'favorites' && (
        <FavoritesTab favorites={favorites} loading={favLoading} onRemove={removeFavoriteById} />
      )}

      <div className="tabs">
        <button className={tab === 'favorites' ? 'active' : ''} onClick={() => setTab('favorites')}>
          غذاهای مورد علاقه
        </button>
        <button
          className={tab === 'chart' ? 'active' : ''}
          onClick={() => {
            setRefreshKey((k) => k + 1)
            setTab('chart')
          }}
        >
          نمودار کالری روزانه
        </button>
        <button className={tab === 'meals' ? 'active' : ''} onClick={() => setTab('meals')}>
          انتخاب غذا
        </button>
      </div>
    </div>
  )
}

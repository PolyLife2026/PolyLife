export const ACTIVITY_TYPES = [
  { value: 'running', label: 'دویدن' },
  { value: 'swimming', label: 'شنا' },
  { value: 'cycling', label: 'دوچرخه‌سواری' },
  { value: 'walking', label: 'پیاده‌روی' },
];

export const DIFFICULTIES = [
  { value: 'easy', label: 'آسان' },
  { value: 'medium', label: 'متوسط' },
  { value: 'hard', label: 'سخت' },
];

export const GOAL_UNITS = [
  { value: 'km', label: 'کیلومتر' },
  { value: 'minute', label: 'دقیقه' },
  { value: 'step', label: 'قدم' },
  { value: 'calorie', label: 'کالری' },
  { value: 'kg', label: 'کیلوگرم' },
];

export const STATUS_LABELS = {
  created: 'ایجاد شده',
  started: 'در حال برگزاری',
  ended: 'پایان‌یافته',
  cancelled: 'لغو شده',
};

export const BADGE_INFO = {
  top1: { label: 'نشان طلایی', emoji: '🥇', description: 'رتبه اول' },
  top3: { label: 'نشان نقره‌ای', emoji: '🥈', description: '۳ نفر اول' },
  top10: { label: 'نشان برنزی', emoji: '🏅', description: '۱۰ نفر اول' },
};

export function getActivityLabel(value) {
  return ACTIVITY_TYPES.find((t) => t.value === value)?.label ?? value;
}

export function getDifficultyLabel(value) {
  return DIFFICULTIES.find((d) => d.value === value)?.label ?? value;
}

export function getGoalUnitLabel(value) {
  return GOAL_UNITS.find((u) => u.value === value)?.label ?? value;
}

export function getStatusLabel(value) {
  return STATUS_LABELS[value] ?? value;
}

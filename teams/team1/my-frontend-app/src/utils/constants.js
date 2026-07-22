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
  active: 'در حال برگزاری',
  ended: 'پایان‌یافته',
  cancelled: 'لغو شده',
};

export const COMPETITION_TYPES = [
  { value: 'weight_loss', label: 'کاهش وزن' },
  { value: 'activity_based', label: 'بر اساس فعالیت' },
  { value: 'record_based', label: 'ثبت رکورد' },
];

export const COMPETITION_STATUS_LABELS = {
  pending: 'در انتظار شروع',
  active: 'در حال برگزاری',
  finished: 'پایان‌یافته',
};

export const USER_JOURNEY_STEPS = [
  {
    title: 'پیوستن به چالش یا مسابقه',
    desc: 'کاربر رویدادهای موجود را بررسی کرده و در یک چالش یا مسابقه فعال ثبت‌نام می‌کند.',
  },
  {
    title: 'ثبت فعالیت روزانه',
    desc: 'در طول چالش، فعالیت‌های ورزشی در همان روز انجام فعالیت ثبت یا ویرایش می‌شوند.',
  },
  {
    title: 'به‌روزرسانی لحظه‌ای امتیاز',
    desc: 'پس از هر فعالیت، امتیاز و رتبه به‌صورت خودکار محاسبه و در جدول امتیازات نمایش داده می‌شود.',
  },
  {
    title: 'پایان خودکار و تخصیص جوایز',
    desc: 'با پایان رویداد، ثبت فعالیت قفل شده و نشان‌ها و پاداش‌ها به برندگان اختصاص می‌یابد.',
  },
];

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

export function getCompetitionTypeLabel(value) {
  return COMPETITION_TYPES.find((t) => t.value === value)?.label ?? value;
}

export function getCompetitionStatusLabel(value) {
  return COMPETITION_STATUS_LABELS[value] ?? value;
}

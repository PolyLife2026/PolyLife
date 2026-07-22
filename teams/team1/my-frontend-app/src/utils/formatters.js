export function formatDate(isoString) {
  if (!isoString) return '—';
  return new Intl.DateTimeFormat('fa-IR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(isoString));
}

export function formatDateTime(isoString) {
  if (!isoString) return '—';
  return new Intl.DateTimeFormat('fa-IR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(isoString));
}

export function toInputDateTime(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function todayISO() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export function parseApiError(error) {
  const data = error?.response?.data;
  if (!data) return 'خطای ارتباط با سرور';
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  if (data.error) return data.error;
  const messages = Object.entries(data).flatMap(([key, val]) => {
    if (Array.isArray(val)) return val.map((m) => `${key}: ${m}`);
    return [`${key}: ${val}`];
  });
  return messages.join(' | ') || 'خطای ناشناخته';
}

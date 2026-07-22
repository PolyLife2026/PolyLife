import axios from 'axios';

const api = axios.create({
  baseURL: '/team1/api',
  headers: { 'Content-Type': 'application/json' },
});

export function setAuthHeaders(userId, role) {
  api.defaults.headers.common['X-User-Id'] = String(userId);
  api.defaults.headers.common['X-User-Role'] = role;
}

export function clearAuthHeaders() {
  delete api.defaults.headers.common['X-User-Id'];
  delete api.defaults.headers.common['X-User-Role'];
}

export default api;

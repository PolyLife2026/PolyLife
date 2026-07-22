import api from './api';

export async function createActivity(payload) {
  const { data } = await api.post('/activities/', payload);
  return data;
}

export async function updateActivity(id, payload) {
  const { data } = await api.patch(`/activities/${id}/`, payload);
  return data;
}

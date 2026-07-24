import api from './api';

export async function fetchChallenges(params = {}) {
  const { data } = await api.get('/challenges/', { params });
  return data;
}

export async function fetchChallenge(id) {
  const { data } = await api.get(`/challenges/${id}/`);
  return data;
}

export async function createChallenge(payload) {
  const { data } = await api.post('/challenges/', payload);
  return data;
}

export async function updateChallenge(id, payload) {
  const { data } = await api.patch(`/challenges/${id}/`, payload);
  return data;
}

export async function deleteChallenge(id) {
  await api.delete(`/challenges/${id}/`);
}

export async function joinChallenge(id) {
  const { data } = await api.post(`/challenges/${id}/join/`);
  return data;
}

export async function fetchLeaderboard(id, page = 1) {
  const { data } = await api.get(`/challenges/${id}/leaderboard/`, {
    params: { page },
  });
  return data;
}

export async function fetchMyRank(id) {
  const { data } = await api.get(`/challenges/${id}/my-rank/`);
  return data;
}

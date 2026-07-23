import api from './api';

export async function fetchCompetitions() {
  const { data } = await api.get('/competitions/');
  return data;
}

export async function fetchCompetition(id) {
  const { data } = await api.get(`/competitions/${id}/`);
  return data;
}

export async function createCompetition(payload) {
  const { data } = await api.post('/competitions/', payload);
  return data;
}

export async function joinCompetition(id) {
  const { data } = await api.post(`/competitions/${id}/join/`);
  return data;
}

export async function startCompetition(id) {
  const { data } = await api.post(`/competitions/${id}/start/`);
  return data;
}

export async function fetchCompetitionLeaderboard(id, params = {}) {
  const { data } = await api.get(`/competitions/${id}/leaderboard/`, { params });
  return data;
}

export async function fetchCompetitionFinalRankings(id) {
  const { data } = await api.get(`/competitions/${id}/final-rankings/`);
  return data;
}

export async function recordCompetitionResult(id, payload) {
  const { data } = await api.post(`/competitions/${id}/results/`, payload);
  return data;
}
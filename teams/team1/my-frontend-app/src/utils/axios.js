import axios from 'axios';

const api = axios.create({
  baseURL: '/team1/api', // Relative path for Vite proxy
  headers: {
    'Content-Type': 'application/json',
    'X-User-Id': '1', // PolyLife header-based auth
    'X-User-Role': 'admin' 
  }
});

export default api;
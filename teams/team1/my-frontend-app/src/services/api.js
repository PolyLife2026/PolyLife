import axios from 'axios';

// Configure based on your Vite proxy or Django backend URL
const api = axios.create({
    baseURL: 'http://localhost:9101/team1/api',
    headers: {
        'Content-Type': 'application/json',
        // PolyLife custom header-based auth required for microservices
        // TODO: Replace static values with dynamic state/context later
        'X-User-Id': '1',
        'Role': 'ADMIN' 
    }
});

export default api;

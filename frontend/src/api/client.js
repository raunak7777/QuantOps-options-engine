import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
    baseURL: API_BASE,
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
});

export const priceOption = (params) => api.post('/price', params).then(r => r.data);
export const getGreeks = (params) => api.post('/greeks', params).then(r => r.data);
export const getSurface = (params) => api.post('/surface', params).then(r => r.data);
export const getMonteCarlo = (params) => api.post('/monte-carlo', params).then(r => r.data);
export const predictVol = (params) => api.post('/predict-vol', params).then(r => r.data);
export const getImpliedVol = (params) => api.post('/implied-vol', params).then(r => r.data);
export const healthCheck = () => api.get('/health').then(r => r.data);

export default api;

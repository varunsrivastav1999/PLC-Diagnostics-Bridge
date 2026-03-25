import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Response interceptor for consistent error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.code === 'ECONNABORTED') {
            error.message = 'Request timed out — check PLC network';
        } else if (!error.response) {
            error.message = 'Server unreachable';
        }
        return Promise.reject(error);
    }
);

export default {
    connect(data) {
        return api.post('/plc/connect', data);
    },
    disconnect(data) {
        return api.post('/plc/disconnect', data);
    },
    testConnection(data) {
        return api.post('/plc/test-connection', data);
    },
    readData(data) {
        return api.post('/plc/read', data);
    },
    writeData(data) {
        return api.post('/plc/write', data);
    },
    getStatus(params) {
        return api.get('/plc/status', { params });
    },
    getSupportedTypes() {
        return api.get('/plc/supported-types');
    },
};

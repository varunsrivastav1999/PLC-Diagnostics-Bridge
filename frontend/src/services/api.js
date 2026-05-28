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
    checkPortBusy(data) {
        return api.post('/plc/check-port', data);
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
    discoverPorts(ip, timeout = 1.0) {
        return api.get('/plc/discover-ports', { params: { ip, timeout } });
    },
    discoverSubnet(ip, timeout = 0.5) {
        return api.get('/plc/discover-subnet', { params: { ip, timeout }, timeout: 60000 });
    },
    getFanucSchema() {
        return api.get('/plc/fanuc/preset-schema');
    },
    getFanucColorSchema() {
        return api.get('/plc/fanuc/color-schema');
    },
    getFanucColors(data, type) {
        return api.post(`/plc/fanuc/colors/${type}`, data);
    },
    saveFanucColors(data, type) {
        return api.put(`/plc/fanuc/colors/${type}`, data);
    },
    getFanucExtendedSchema() {
        return api.get('/plc/fanuc/extended-schema');
    },
    getFanucExtended(data, type) {
        return api.post(`/plc/fanuc/extended/${type}`, data);
    },
    saveFanucExtended(data, type) {
        return api.put(`/plc/fanuc/extended/${type}`, data);
    },
    getLatency(plcType, ip, port) {
        return api.get('/plc/latency', { params: { plc_type: plcType, ip, port } });
    }
};

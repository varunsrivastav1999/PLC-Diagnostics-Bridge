import { defineStore } from 'pinia';
import api from '../services/api';

export const usePlcStore = defineStore('plc', {
    state: () => ({
        connectionConfig: {
            plc_type: 'siemens',
            ip: '192.168.0.10',
            port: 102,
            rack: 0,
            slot: 1,
            cpu_type: 'S7-1500',
        },
        isConnected: false,
        isConnecting: false,
        supportedTypes: [],
        pollingInterval: 1000,
        isPolling: false,
        activePollTimeout: null,
        portBusy: false,
        checkingPort: false,
        portStatus: 'unknown',
        portMessage: '',
        responseTime: null,
    }),

    getters: {
        connectionLabel: (state) => `${state.connectionConfig.plc_type} @ ${state.connectionConfig.ip}:${state.connectionConfig.port}`,
    },

    actions: {
        async fetchSupportedTypes() {
            try {
                const res = await api.getSupportedTypes();
                this.supportedTypes = res.data;
            } catch {
                // Silent — dropdown keeps local defaults
            }
        },

        async checkPortBusy() {
            this.checkingPort = true;
            try {
                const res = await api.checkPortBusy(this.connectionConfig);
                const data = res.data;

                // Normalize response for reliable busy/free state
                const status = (data.port_status || 'unknown').toLowerCase();
                const busy = typeof data.port_busy === 'boolean' ? data.port_busy : status === 'open';

                this.portBusy = busy;
                this.portStatus = status;
                this.portMessage = data.message || '';
                this.responseTime = data.response_time || null;
                return { ...data, port_busy: busy, port_status: status };
            } catch (err) {
                this.portBusy = false;
                this.portStatus = 'error';
                this.portMessage = err.message;
                this.responseTime = null;
                return { success: false, message: err.message };
            } finally {
                this.checkingPort = false;
            }
        },

        async connectPlc() {
            this.isConnecting = true;
            try {
                const res = await api.connect(this.connectionConfig);
                this.isConnected = res.data.connected;
                return res.data;
            } catch (err) {
                this.isConnected = false;
                return { success: false, message: err.message };
            } finally {
                this.isConnecting = false;
            }
        },

        async disconnectPlc() {
            try {
                const res = await api.disconnect(this.connectionConfig);
                this.isConnected = false;
                this.stopPolling();
                return res.data;
            } catch (err) {
                this.isConnected = false;
                this.stopPolling();
                return { success: false, message: err.message };
            }
        },

        startPolling(readCallback) {
            if (this.isPolling) return;
            this.isPolling = true;
            this._pollLoop(readCallback);
        },

        stopPolling() {
            this.isPolling = false;
            if (this.activePollTimeout) {
                clearTimeout(this.activePollTimeout);
                this.activePollTimeout = null;
            }
        },

        _pollLoop(readCallback) {
            if (!this.isPolling || !this.isConnected) {
                this.stopPolling();
                return;
            }
            readCallback().finally(() => {
                if (this.isPolling && this.isConnected) {
                    this.activePollTimeout = setTimeout(() => {
                        this._pollLoop(readCallback);
                    }, this.pollingInterval);
                }
            });
        },
    },
});

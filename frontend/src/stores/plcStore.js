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

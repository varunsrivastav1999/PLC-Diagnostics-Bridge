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
        autoDetectingPort: false,
        autoConnecting: false,
        autoLinkEnabled: true,
        autoLinkStatus: 'idle',
        autoLinkMessage: 'Ready: Auto-detects MC port & connects on completed IP',
        lastDetectedPort: null,
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
                if (this.autoLinkStatus === 'connected') {
                    this.autoLinkStatus = 'idle';
                    this.autoLinkMessage = 'Disconnected. Ready to auto-link on IP change.';
                }
                return res.data;
            } catch (err) {
                this.isConnected = false;
                this.stopPolling();
                return { success: false, message: err.message };
            }
        },

        resetAutoLink(message = 'Session refreshed. Ready for IP.') {
            this.autoDetectingPort = false;
            this.autoConnecting = false;
            this.autoLinkStatus = 'refreshing';
            this.autoLinkMessage = message;
        },

        async autoDiscoverAndConnect(targetIp) {
            const ip = targetIp || this.connectionConfig.ip;
            if (!ip) return { success: false, message: 'No target IP provided' };

            this.autoDetectingPort = true;
            this.autoLinkStatus = 'detecting';
            this.autoLinkMessage = `Probing MC Protocol ports on ${ip}...`;

            try {
                const res = await api.discoverPorts(ip);
                const data = res.data;
                let portToUse = 5000;

                if (data && data.success && data.recommended_port) {
                    portToUse = data.recommended_port;
                    this.connectionConfig.port = portToUse;
                    this.lastDetectedPort = portToUse;
                    const count = data.discovery?.mc_ports?.length || 1;
                    this.autoLinkMessage = `✓ Detected MC Port ${portToUse} (${count} active). Connecting...`;
                } else {
                    this.connectionConfig.port = portToUse;
                    this.lastDetectedPort = portToUse;
                    this.autoLinkMessage = `MC scan completed (using standard port ${portToUse}). Connecting...`;
                }

                // Proceed to connection process
                this.autoDetectingPort = false;
                this.autoConnecting = true;
                this.autoLinkStatus = 'connecting';

                const connResult = await this.connectPlc();
                if (connResult.success) {
                    this.autoLinkStatus = 'connected';
                    this.autoLinkMessage = `✓ Linked to Mitsubishi MC at ${ip}:${this.connectionConfig.port}`;
                    return { success: true, port: this.connectionConfig.port, message: this.autoLinkMessage };
                } else {
                    this.autoLinkStatus = 'failed';
                    this.autoLinkMessage = `Port ${this.connectionConfig.port} detected, but connection failed: ${connResult.message}`;
                    return { success: false, port: this.connectionConfig.port, message: this.autoLinkMessage };
                }
            } catch (err) {
                this.autoDetectingPort = false;
                this.autoConnecting = false;
                this.autoLinkStatus = 'failed';
                this.autoLinkMessage = `MC Discovery failed on ${ip}: ${err.message}`;
                return { success: false, message: err.message };
            } finally {
                this.autoDetectingPort = false;
                this.autoConnecting = false;
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

/**
 * AURIX — WebSocket Client
 * Real-time communication with the AURIX backend
 */

const AurixWS = {
    ws: null,
    reconnectAttempts: 0,
    maxReconnectAttempts: 10,
    reconnectDelay: 2000,
    isConnected: false,
    messageHandlers: [],

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                HUD.updateStatus('ONLINE', 'online');
                HUD.addLogEntry('System connected');
                console.log('[WS] Connected to AURIX');
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this._handleMessage(data);
                } catch (e) {
                    console.error('[WS] Parse error:', e);
                }
            };

            this.ws.onclose = () => {
                this.isConnected = false;
                HUD.updateStatus('DISCONNECTED', 'error');
                console.log('[WS] Disconnected');
                this._attemptReconnect();
            };

            this.ws.onerror = (error) => {
                console.error('[WS] Error:', error);
            };
        } catch (e) {
            console.error('[WS] Connection failed:', e);
            this._attemptReconnect();
        }
    },

    _attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * this.reconnectAttempts;
            HUD.updateStatus(`RECONNECTING (${this.reconnectAttempts})`, 'error');
            setTimeout(() => this.connect(), delay);
        }
    },

    send(type, data = {}) {
        if (!this.isConnected || !this.ws) {
            console.warn('[WS] Not connected');
            return false;
        }

        try {
            this.ws.send(JSON.stringify({ type, ...data }));
            return true;
        } catch (e) {
            console.error('[WS] Send error:', e);
            return false;
        }
    },

    sendChat(message) {
        return this.send('chat', { content: message });
    },

    requestStats() {
        return this.send('stats');
    },

    onMessage(handler) {
        this.messageHandlers.push(handler);
    },

    _handleMessage(data) {
        for (const handler of this.messageHandlers) {
            try {
                handler(data);
            } catch (e) {
                console.error('[WS] Handler error:', e);
            }
        }
    },

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    },
};

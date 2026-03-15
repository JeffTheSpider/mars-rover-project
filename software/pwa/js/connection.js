// Mars Rover PWA — WebSocket Connection Manager
// Handles connection lifecycle, reconnection with exponential backoff,
// and message routing between the UI and rover.

class RoverConnection {
    constructor() {
        this.ws = null;
        this.ip = null;
        this.port = 81;
        this.reconnectDelay = 1000;
        this.maxReconnectDelay = 10000;
        this.reconnectTimer = null;
        this.heartbeatTimer = null;
        this.connected = false;
        this.listeners = new Map();
    }

    // --- Event system ---
    on(event, callback) {
        if (!this.listeners.has(event)) this.listeners.set(event, []);
        this.listeners.get(event).push(callback);
    }

    emit(event, data) {
        const cbs = this.listeners.get(event);
        if (cbs) cbs.forEach(cb => cb(data));
    }

    // --- Connection lifecycle ---
    connect(ip) {
        this.ip = ip;
        this.disconnect();

        try {
            this.ws = new WebSocket(`ws://${ip}:${this.port}`);
        } catch (e) {
            this.emit('error', `Invalid address: ${ip}`);
            return;
        }

        this.ws.onopen = () => {
            this.connected = true;
            this.reconnectDelay = 1000;
            this.emit('connected', this.ip);
            this.startHeartbeat();
            // Save last successful IP
            try { localStorage.setItem('rover_ip', ip); } catch (_) {}
        };

        this.ws.onclose = () => {
            const wasConnected = this.connected;
            this.connected = false;
            this.stopHeartbeat();
            this.emit('disconnected', wasConnected ? 'lost' : 'failed');
            this.scheduleReconnect();
        };

        this.ws.onerror = () => {
            // onclose fires after onerror — handling there
        };

        this.ws.onmessage = (e) => {
            try {
                const data = JSON.parse(e.data);
                this.emit('message', data);
            } catch (_) {
                // Binary frame (e.g. MJPEG camera) — emit raw
                this.emit('binary', e.data);
            }
        };
    }

    disconnect() {
        this.stopHeartbeat();
        clearTimeout(this.reconnectTimer);
        if (this.ws) {
            this.ws.onclose = null;
            this.ws.onerror = null;
            this.ws.close();
            this.ws = null;
        }
        this.connected = false;
    }

    scheduleReconnect() {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = setTimeout(() => {
            if (this.ip) this.connect(this.ip);
        }, this.reconnectDelay);
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
    }

    // --- Heartbeat ---
    startHeartbeat() {
        this.stopHeartbeat();
        this.heartbeatTimer = setInterval(() => {
            this.send({ cmd: 'ping' });
        }, 5000);
    }

    stopHeartbeat() {
        clearInterval(this.heartbeatTimer);
        this.heartbeatTimer = null;
    }

    // --- Send commands ---
    send(obj) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(obj));
            return true;
        }
        return false;
    }

    sendDrive(cmd, speed, mode) {
        return this.send({ cmd, speed, mode });
    }

    sendStop() {
        return this.send({ cmd: 'stop' });
    }

    sendEstop() {
        return this.send({ cmd: 'estop' });
    }

    // --- Status ---
    get isConnected() {
        return this.connected && this.ws && this.ws.readyState === WebSocket.OPEN;
    }

    getLastIP() {
        try { return localStorage.getItem('rover_ip') || ''; } catch (_) { return ''; }
    }
}

// Export singleton
window.roverConnection = new RoverConnection();

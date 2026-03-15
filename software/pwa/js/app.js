// Mars Rover PWA — Main Application
// Orchestrates connection, controls, UI updates, and section toggling.

(function () {
    'use strict';

    const conn = window.roverConnection;
    let controls = null;
    let logEntries = [];
    const MAX_LOG_ENTRIES = 100;

    // ============================================================
    // Initialisation
    // ============================================================
    document.addEventListener('DOMContentLoaded', () => {
        registerServiceWorker();
        initConnectionDialog();
        initExpandableSections();
        initActionButtons();

        controls = new window.RoverControls(conn);
        controls.init();

        // Connection events
        conn.on('connected', onConnected);
        conn.on('disconnected', onDisconnected);
        conn.on('message', onMessage);
        conn.on('error', onError);

        // Auto-connect if we have a saved IP
        const lastIP = conn.getLastIP();
        if (lastIP) {
            document.getElementById('rover-ip').value = lastIP;
        }
    });

    // ============================================================
    // Service Worker
    // ============================================================
    function registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(reg => addLog('info', 'Service worker registered'))
                .catch(err => addLog('error', 'SW registration failed'));
        }
    }

    // ============================================================
    // Connection Dialog
    // ============================================================
    function initConnectionDialog() {
        const dialog = document.getElementById('connect-dialog');
        const input = document.getElementById('rover-ip');
        const btn = document.getElementById('connect-btn');
        const errorEl = document.getElementById('connect-error');

        btn.addEventListener('click', () => {
            const ip = input.value.trim();
            if (!ip) {
                errorEl.textContent = 'Enter the rover IP address';
                return;
            }
            errorEl.textContent = 'Connecting...';
            btn.disabled = true;
            conn.connect(ip);
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') btn.click();
        });
    }

    function showConnectDialog() {
        const dialog = document.getElementById('connect-dialog');
        const btn = document.getElementById('connect-btn');
        dialog.classList.remove('connect-dialog--hidden');
        btn.disabled = false;
    }

    function hideConnectDialog() {
        document.getElementById('connect-dialog').classList.add('connect-dialog--hidden');
    }

    // ============================================================
    // Connection Events
    // ============================================================
    function onConnected(ip) {
        hideConnectDialog();
        updateConnectionStatus(true);
        addLog('info', `Connected to ${ip}`);
    }

    function onDisconnected(reason) {
        updateConnectionStatus(false);
        if (reason === 'lost') {
            addLog('warn', 'Connection lost — reconnecting...');
        } else if (reason === 'failed') {
            const errorEl = document.getElementById('connect-error');
            if (errorEl) errorEl.textContent = 'Connection failed — retrying...';
        }
    }

    function onError(msg) {
        addLog('error', msg);
        const errorEl = document.getElementById('connect-error');
        if (errorEl) errorEl.textContent = msg;
    }

    function onMessage(data) {
        // Status update from rover
        if (data.batt !== undefined) updateBattery(data.batt, data.pct);
        if (data.ml !== undefined) updateSpeed(data.ml, data.mr);
        if (data.mode !== undefined) updateSteeringMode(data.mode);
        if (data.estop !== undefined) controls.setEstop(data.estop);
        if (data.uptime !== undefined) updateUptime(data.uptime);
        if (data.rssi !== undefined) updateRSSI(data.rssi);

        // Error from rover
        if (data.error) addLog('error', `Rover: ${data.error}`);
    }

    // ============================================================
    // UI Updates
    // ============================================================
    function updateConnectionStatus(connected) {
        const dot = document.getElementById('status-dot');
        if (dot) {
            dot.className = 'header__dot' + (connected ? ' header__dot--connected' : ' header__dot--error');
        }
    }

    function updateBattery(voltage, percent) {
        const el = document.getElementById('battery-value');
        if (el) {
            const pct = Math.round(percent || 0);
            el.textContent = `${pct}%`;

            // Battery icon colour
            const battEl = document.getElementById('battery-display');
            if (battEl) {
                if (pct > 50) battEl.style.color = 'var(--success)';
                else if (pct > 20) battEl.style.color = 'var(--warning)';
                else battEl.style.color = 'var(--danger)';
            }
        }

        // Status bar voltage
        const voltEl = document.getElementById('status-voltage');
        if (voltEl && voltage !== undefined) {
            voltEl.textContent = voltage.toFixed(1) + 'V';
        }
    }

    function updateSpeed(left, right) {
        const el = document.getElementById('status-speed');
        if (el) {
            el.textContent = `L:${left} R:${right}`;
        }
    }

    function updateSteeringMode(mode) {
        const names = ['Ackermann', 'Point Turn', 'Crab Walk'];
        const el = document.getElementById('status-mode');
        if (el) el.textContent = names[mode] || 'Unknown';
    }

    function updateUptime(seconds) {
        const el = document.getElementById('health-uptime');
        if (!el) return;
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        el.textContent = `${h}h ${m}m ${s}s`;
    }

    function updateRSSI(rssi) {
        const el = document.getElementById('health-wifi');
        if (el) {
            el.textContent = rssi + ' dBm';
            el.className = 'health-card__value';
            if (rssi > -50) el.classList.add('health-card__value--ok');
            else if (rssi > -70) el.classList.add('health-card__value--warn');
            else el.classList.add('health-card__value--danger');
        }
    }

    // ============================================================
    // Expandable Sections
    // ============================================================
    function initExpandableSections() {
        document.querySelectorAll('.section__header').forEach(header => {
            header.addEventListener('click', () => {
                header.parentElement.classList.toggle('section--open');
            });
        });
    }

    // ============================================================
    // Quick Action Buttons
    // ============================================================
    function initActionButtons() {
        const ledBtn = document.getElementById('action-lights');
        if (ledBtn) {
            let ledOn = false;
            ledBtn.addEventListener('click', () => {
                ledOn = !ledOn;
                conn.send({ cmd: 'led', state: ledOn ? 1 : 0 });
                ledBtn.style.color = ledOn ? 'var(--secondary)' : '';
            });
        }

        const hornBtn = document.getElementById('action-horn');
        if (hornBtn) {
            hornBtn.addEventListener('touchstart', (e) => {
                e.preventDefault();
                conn.send({ cmd: 'buzzer', state: 1 });
            }, { passive: false });
            hornBtn.addEventListener('touchend', (e) => {
                e.preventDefault();
                conn.send({ cmd: 'buzzer', state: 0 });
            }, { passive: false });
            // Mouse fallback
            hornBtn.addEventListener('mousedown', () => conn.send({ cmd: 'buzzer', state: 1 }));
            hornBtn.addEventListener('mouseup', () => conn.send({ cmd: 'buzzer', state: 0 }));
        }
    }

    // ============================================================
    // Logging
    // ============================================================
    function addLog(level, message) {
        const now = new Date();
        const ts = now.toLocaleTimeString('en-GB', { hour12: false });
        const entry = { time: ts, level, message };

        logEntries.push(entry);
        if (logEntries.length > MAX_LOG_ENTRIES) logEntries.shift();

        const viewer = document.getElementById('log-viewer');
        if (!viewer) return;

        const div = document.createElement('div');
        div.className = `log-entry--${level}`;
        div.textContent = `[${ts}] ${message}`;
        viewer.appendChild(div);

        // Auto-scroll
        viewer.scrollTop = viewer.scrollHeight;

        // Trim DOM
        while (viewer.children.length > MAX_LOG_ENTRIES) {
            viewer.removeChild(viewer.firstChild);
        }
    }

    // ============================================================
    // Settings UI
    // ============================================================
    window.updateSetting = function (setting, value) {
        conn.send({ cmd: 'cfg', key: setting, value: parseFloat(value) || 0 });

        // Update display value
        const display = document.getElementById(`setting-${setting}-value`);
        if (display) {
            if (setting === 'led_color') display.textContent = value;
            else display.textContent = value;
        }
    };
})();

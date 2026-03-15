// Mars Rover PWA — Touch Controls
// D-pad with touch-and-hold for continuous driving (release = stop)
// Touch events only — no click handlers (EA-16 spec)

class RoverControls {
    constructor(connection) {
        this.connection = connection;
        this.activeCmd = null;
        this.speed = 50;
        this.steeringMode = 0; // 0=Ackermann, 1=PointTurn, 2=CrabWalk
        this.debounceTimer = null;
        this.estopEngaged = false;

        this.cmdMap = {
            'fl':    'fl',
            'fwd':   'fwd',
            'fr':    'fr',
            'left':  'left',
            'stop':  'stop',
            'right': 'right',
            'bl':    'bl',
            'rev':   'rev',
            'br':    'br'
        };
    }

    init() {
        this.bindDpad();
        this.bindSpeedSlider();
        this.bindModeButtons();
        this.bindEstop();
    }

    // --- D-Pad ---
    bindDpad() {
        const buttons = document.querySelectorAll('.dpad__btn[data-cmd]');
        buttons.forEach(btn => {
            const cmd = btn.dataset.cmd;

            // Touch events for mobile
            btn.addEventListener('touchstart', (e) => {
                e.preventDefault();
                this.onPress(cmd, btn);
            }, { passive: false });

            btn.addEventListener('touchend', (e) => {
                e.preventDefault();
                this.onRelease(btn);
            }, { passive: false });

            btn.addEventListener('touchcancel', (e) => {
                e.preventDefault();
                this.onRelease(btn);
            }, { passive: false });

            // Mouse fallback for desktop testing
            btn.addEventListener('mousedown', (e) => {
                e.preventDefault();
                this.onPress(cmd, btn);
            });

            btn.addEventListener('mouseup', (e) => {
                e.preventDefault();
                this.onRelease(btn);
            });

            btn.addEventListener('mouseleave', () => {
                if (this.activeCmd) this.onRelease(btn);
            });
        });

        // Safety: stop on any touch end outside d-pad
        document.addEventListener('touchend', () => {
            if (this.activeCmd && this.activeCmd !== 'stop') {
                this.sendStop();
            }
        });
    }

    onPress(cmd, btn) {
        if (this.estopEngaged) return;

        // 50ms debounce
        if (this.debounceTimer) return;
        this.debounceTimer = setTimeout(() => {
            this.debounceTimer = null;
        }, 50);

        this.activeCmd = cmd;
        btn.classList.add('dpad__btn--active');

        if (cmd === 'stop') {
            this.sendStop();
        } else {
            this.connection.sendDrive(cmd, this.speed, this.steeringMode);
        }
    }

    onRelease(btn) {
        btn.classList.remove('dpad__btn--active');
        if (this.activeCmd && this.activeCmd !== 'stop') {
            this.sendStop();
        }
        this.activeCmd = null;
    }

    sendStop() {
        this.activeCmd = null;
        this.connection.sendStop();
    }

    // --- Speed Slider ---
    bindSpeedSlider() {
        const slider = document.getElementById('speed-slider');
        const value = document.getElementById('speed-value');
        if (!slider || !value) return;

        slider.addEventListener('input', () => {
            this.speed = parseInt(slider.value, 10);
            value.textContent = this.speed + '%';
        });

        // Load saved speed
        try {
            const saved = localStorage.getItem('rover_speed');
            if (saved) {
                this.speed = parseInt(saved, 10);
                slider.value = this.speed;
                value.textContent = this.speed + '%';
            }
        } catch (_) {}

        // Save on change
        slider.addEventListener('change', () => {
            try { localStorage.setItem('rover_speed', this.speed); } catch (_) {}
        });
    }

    // --- Steering Mode ---
    bindModeButtons() {
        const buttons = document.querySelectorAll('.mode-btn[data-mode]');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.steeringMode = parseInt(btn.dataset.mode, 10);
                buttons.forEach(b => b.classList.remove('mode-btn--active'));
                btn.classList.add('mode-btn--active');
                this.connection.send({ cmd: 'mode', mode: this.steeringMode });
                try { localStorage.setItem('rover_mode', this.steeringMode); } catch (_) {}
            });
        });

        // Restore saved mode
        try {
            const saved = localStorage.getItem('rover_mode');
            if (saved !== null) {
                this.steeringMode = parseInt(saved, 10);
                const active = document.querySelector(`.mode-btn[data-mode="${this.steeringMode}"]`);
                if (active) {
                    buttons.forEach(b => b.classList.remove('mode-btn--active'));
                    active.classList.add('mode-btn--active');
                }
            }
        } catch (_) {}
    }

    // --- E-Stop ---
    bindEstop() {
        const btn = document.getElementById('estop-btn');
        if (!btn) return;

        btn.addEventListener('click', () => {
            if (this.estopEngaged) {
                // Release E-stop
                this.estopEngaged = false;
                btn.classList.remove('estop-btn--engaged');
                btn.textContent = 'EMERGENCY STOP';
                this.connection.send({ cmd: 'resume' });
            } else {
                // Engage E-stop
                this.estopEngaged = true;
                btn.classList.add('estop-btn--engaged');
                btn.textContent = 'E-STOP ENGAGED — TAP TO RELEASE';
                this.connection.sendEstop();
            }
        });
    }

    // --- External state update ---
    setEstop(engaged) {
        this.estopEngaged = engaged;
        const btn = document.getElementById('estop-btn');
        if (!btn) return;
        if (engaged) {
            btn.classList.add('estop-btn--engaged');
            btn.textContent = 'E-STOP ENGAGED — TAP TO RELEASE';
        } else {
            btn.classList.remove('estop-btn--engaged');
            btn.textContent = 'EMERGENCY STOP';
        }
    }
}

window.RoverControls = RoverControls;

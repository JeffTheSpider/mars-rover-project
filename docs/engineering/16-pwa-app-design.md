# Engineering Analysis 16: Phone PWA Control App Design

**Document**: EA-16
**Date**: 2026-03-15
**Purpose**: Define the phone control app architecture, UI design, features, and communication protocol for controlling the rover from a mobile device.
**Depends on**: EA-12 (UART Protocol), EA-13 (ROS2), EA-15 (Safety)

---

## 1. Architecture Overview

### 1.1 Phase 1: Direct ESP32 Connection

```
Phone (PWA) ←→ WebSocket ←→ ESP32-S3 WiFi Web Server
                               (same network)
```

- Phone connects directly to ESP32's IP via local WiFi
- WebSocket for real-time control (low latency)
- HTTP for status API and web UI serving
- No internet required — works on local network only
- Proven pattern from Hub project (Clock/Lamp PWA)

### 1.2 Phase 2: Through Jetson

```
Phone (PWA) ←→ WebSocket ←→ Jetson (web_server_node)
                               ↕ ROS2 topics
                           ←→ Nav2, cameras, AI, etc.
                               ↕ UART
                           ←→ ESP32-S3 (motors)
```

- Phone connects to Jetson's web server (ROS2 node)
- All commands flow through ROS2 → UART → ESP32
- Camera streams available (MJPEG over WebSocket)
- 4G modem enables remote control over internet
- Same PWA UI, different backend

---

## 2. UI Design

### 2.1 Design Language

| Element | Value | Notes |
|---------|-------|-------|
| Theme | Catppuccin Mocha (dark) | Same as Hub project — Charlie's preference |
| Font | Plus Jakarta Sans (headings), system sans (body) | Same as Hub |
| Accent colour | Mars red (#f38ba8 / Catppuccin red) | Rover themed |
| Secondary | Sand (#f9e2af / Catppuccin yellow) | Mars terrain |
| Layout | Mobile-first, single page app | 360-412px width target |
| Interactions | Touch-optimised, large tap targets (48px+) | Gloves-compatible |

### 2.2 Screen Layout

```
┌──────────────────────────┐
│  MARS ROVER    🔋 78%    │  Header: name + battery
├──────────────────────────┤
│                          │
│   [Camera Feed]          │  Live camera (Phase 2)
│   640×480 MJPEG          │  or placeholder (Phase 1)
│                          │
├──────────────────────────┤
│  Status Bar              │
│  Speed: 2.3 | Steer: 15°│
│  Mode: Ackermann         │
├──────────────────────────┤
│                          │
│  ┌───┐ ┌───┐ ┌───┐     │
│  │ ↖ │ │ ↑ │ │ ↗ │     │  D-pad controls
│  └───┘ └───┘ └───┘     │
│  ┌───┐ ┌───┐ ┌───┐     │
│  │ ← │ │STP│ │ → │     │  Centre = E-STOP
│  └───┘ └───┘ └───┘     │
│  ┌───┐ ┌───┐ ┌───┐     │
│  │ ↙ │ │ ↓ │ │ ↘ │     │
│  └───┘ └───┘ └───┘     │
│                          │
├──────────────────────────┤
│  Speed: ═══════●════  50%│  Speed slider
├──────────────────────────┤
│ [Ackermann] [Turn] [Crab]│  Mode buttons
├──────────────────────────┤
│ [Lights] [Horn] [Camera] │  Quick actions
├──────────────────────────┤
│ ▸ Settings               │  Expandable sections
│ ▸ Navigation             │
│ ▸ System                 │
└──────────────────────────┘
```

### 2.3 D-Pad Control

Touch-and-hold for continuous driving (release = stop):

| Button | Phase 1 Action | Phase 2 Action |
|--------|---------------|----------------|
| ↑ Forward | `{"cmd":"fwd","speed":50}` | Publish `cmd_vel.linear.x = speed` |
| ↓ Reverse | `{"cmd":"rev","speed":50}` | Publish `cmd_vel.linear.x = -speed` |
| ← Left | `{"cmd":"left","speed":50}` | Publish `cmd_vel.angular.z = rate` |
| → Right | `{"cmd":"right","speed":50}` | Publish `cmd_vel.angular.z = -rate` |
| ↖ Fwd-Left | `{"cmd":"fl","speed":50}` | Combined linear + angular |
| ↗ Fwd-Right | `{"cmd":"fr","speed":50}` | Combined linear + angular |
| ↙ Rev-Left | `{"cmd":"bl","speed":50}` | Combined |
| ↘ Rev-Right | `{"cmd":"br","speed":50}` | Combined |
| STOP (centre) | `{"cmd":"stop"}` | Publish `cmd_vel = 0` |

**Touch handling**: Use `touchstart`/`touchend` events (not `click`). Send command on press, send stop on release. 50ms debounce to prevent double-sends.

### 2.4 Virtual Joystick (Alternative)

For Phase 2, replace the D-pad with a virtual analogue joystick:

```
┌────────────────────────┐
│                        │
│     ┌──────────┐       │
│     │    ●     │       │  Touch circle
│     │   /      │       │  Drag = direction + speed
│     │  ○       │       │  ○ = centre (neutral)
│     │          │       │  ● = touch position
│     └──────────┘       │
│                        │
└────────────────────────┘

Output:
  linear.x = distance × cos(angle)  (forward/back)
  angular.z = distance × sin(angle) (left/right)
  distance normalised 0-1 (1 = edge of circle)
```

Libraries: nipplejs (lightweight JS joystick, ~8 KB)

---

## 3. Sections & Features

### 3.1 Status Dashboard

Always visible at top of screen:

| Field | Source | Update Rate |
|-------|--------|-------------|
| Battery voltage | ESP32 ADC | 1 Hz |
| Battery percent | Calculated | 1 Hz |
| Speed (L/R) | Motor PWM values | 5 Hz |
| Steering angle | Current servo angles | 5 Hz |
| Steering mode | Current mode | On change |
| WiFi signal | RSSI | 5 Hz |
| GPS position | GPS module (Phase 2) | 1 Hz |
| Temperature | DS18B20 (Phase 2) | 1 Hz |
| Uptime | ESP32 millis | 5 Hz |

### 3.2 Settings Section (Expandable)

| Setting | Type | Default | Range |
|---------|------|---------|-------|
| Max speed | Slider | 50% | 10-100% |
| Steering sensitivity | Slider | Medium | Low/Med/High |
| Camera resolution | Dropdown | 640×480 | 320×240, 640×480, 1280×720 |
| LED colour | Colour picker | Red | Full RGB |
| LED mode | Buttons | Off | Off / Solid / Blink / Chase |
| Horn tone | Slider | 1000 Hz | 200-4000 Hz |
| Servo trim FL | ±Slider | 0 | -50 to +50 μs |
| Servo trim FR | ±Slider | 0 | -50 to +50 μs |
| Servo trim RL | ±Slider | 0 | -50 to +50 μs |
| Servo trim RR | ±Slider | 0 | -50 to +50 μs |

### 3.3 Navigation Section (Phase 2)

| Feature | Description |
|---------|-------------|
| Map view | 2D occupancy grid from SLAM (rendered as canvas) |
| GPS track | Breadcrumb trail on OpenStreetMap tile |
| Waypoint editor | Tap to add waypoints, drag to reorder |
| Patrol route | Saved waypoint lists, start/stop/pause |
| Return-to-home button | Trigger RTH behaviour tree |
| Geofence editor | Draw polygon on map |

### 3.4 Camera Section (Phase 2)

| Feature | Description |
|---------|-------------|
| Live view | MJPEG stream from selected camera |
| Camera selector | Tabs: Front / Rear / Left / Right / Mast / Depth / IR |
| Mast control | Pan + tilt sliders (0-360° pan, -45 to +90° tilt) |
| Zoom control | Slider for ELP 10× zoom |
| Snapshot | Save current frame to phone gallery |
| Recording | Start/stop video recording to rover SD card |
| YOLO overlay | Toggle: show detection bounding boxes on live feed |

### 3.5 System Section

| Feature | Description |
|---------|-------------|
| Health | CPU/GPU/RAM usage, temperature |
| Diagnostics | Sensor status (green/yellow/red per sensor) |
| Logs | Scrollable log viewer (last 100 messages) |
| OTA update | Upload new ESP32 firmware from phone |
| Backup/Restore | Save/load rover configuration |
| Reboot | Restart Jetson or ESP32 |
| Shutdown | Safe shutdown (parks motors, saves state) |

---

## 4. Communication

### 4.1 WebSocket Protocol

Phase 1 uses the same JSON-over-WebSocket as the firmware's `rover_webserver.h`:

```javascript
// Send command
ws.send(JSON.stringify({
    cmd: "fwd",     // Command name
    speed: 50,      // Speed percentage
    mode: 0         // 0=Ackermann, 1=PointTurn, 2=CrabWalk
}));

// Receive status
ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    // data = { batt: 7.4, pct: 78, ml: 50, mr: 50 }
};
```

### 4.2 Phase 2 Extended Protocol

Phase 2 adds more message types:

```javascript
// Camera stream (binary WebSocket frames)
// MJPEG frames sent as binary blobs

// Navigation commands
ws.send(JSON.stringify({
    type: "nav",
    action: "goto",
    lat: 52.9378,
    lon: -1.4947
}));

// Autonomous mode
ws.send(JSON.stringify({
    type: "autonomy",
    action: "start_patrol",
    route: "garden_loop"
}));
```

### 4.3 Connection Management

```javascript
class RoverConnection {
    constructor() {
        this.ws = null;
        this.reconnectDelay = 1000;
        this.maxReconnect = 10000;
    }

    connect(ip) {
        this.ws = new WebSocket(`ws://${ip}:81`);

        this.ws.onopen = () => {
            this.reconnectDelay = 1000;  // Reset backoff
            this.onConnected();
        };

        this.ws.onclose = () => {
            this.onDisconnected();
            // Exponential backoff reconnect
            setTimeout(() => this.connect(ip),
                       this.reconnectDelay);
            this.reconnectDelay = Math.min(
                this.reconnectDelay * 2, this.maxReconnect
            );
        };

        this.ws.onmessage = (e) => this.onMessage(e.data);
    }
}
```

---

## 5. Offline / PWA Features

### 5.1 Service Worker

Network-first strategy (same as Hub project, proven approach):

```javascript
// sw.js
const CACHE_VERSION = 'rover-v1';

self.addEventListener('fetch', (e) => {
    e.respondWith(
        fetch(e.request)
            .then(response => {
                // Cache successful responses
                const clone = response.clone();
                caches.open(CACHE_VERSION).then(c => c.put(e.request, clone));
                return response;
            })
            .catch(() => caches.match(e.request))
    );
});
```

### 5.2 PWA Manifest

```json
{
    "name": "Mars Rover Control",
    "short_name": "Rover",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#1e1e2e",
    "theme_color": "#f38ba8",
    "orientation": "portrait",
    "icons": [
        { "src": "/icons/rover-192.png", "sizes": "192x192" },
        { "src": "/icons/rover-512.png", "sizes": "512x512" }
    ]
}
```

### 5.3 Installable

The PWA is installable as a home screen app on:
- Android Chrome (prompt appears after 2 visits)
- iOS Safari (Add to Home Screen)
- Desktop Chrome/Edge

When installed, it launches in standalone mode (no browser chrome), looks and feels like a native app.

---

## 6. Responsive Layout

### 6.1 Breakpoints

| Width | Layout | Notes |
|-------|--------|-------|
| <400px | Single column, compact D-pad | Phone portrait |
| 400-768px | Single column, larger controls | Phone landscape / small tablet |
| >768px | Two columns: camera left + controls right | Tablet / desktop |

### 6.2 Landscape Mode

When phone is rotated to landscape:
- Camera feed takes left 60% of screen
- Controls stack on right 40%
- D-pad shrinks to fit
- Ideal for driving with live camera view

---

## 7. Phase 1 Implementation

The Phase 1 PWA is already embedded in `firmware/esp32/webserver.h` as a single HTML page. For Phase 2, it will be extracted to separate files served by the Jetson:

```
software/pwa/
├── index.html
├── manifest.json
├── sw.js
├── css/
│   └── styles.css         # Catppuccin Mocha theme
├── js/
│   ├── app.js             # Main application logic
│   ├── connection.js      # WebSocket management
│   ├── controls.js        # D-pad / joystick
│   ├── camera.js          # Camera stream handler
│   └── map.js             # Navigation map (Leaflet.js)
├── icons/
│   ├── rover-192.png
│   └── rover-512.png
└── lib/
    ├── nipplejs.min.js    # Virtual joystick (~8KB)
    └── leaflet.min.js     # Map library (~40KB)
```

---

*Document EA-16 v1.0 — 2026-03-15*

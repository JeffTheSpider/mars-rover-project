# Mars Rover Control PWA

Browser-based phone app for controlling the Mars Rover. Catppuccin Mocha dark theme matching the Hub project.

## Phase 1 Features
- D-pad touch controls (touch-and-hold = drive, release = stop)
- 3 steering modes: Ackermann, Point Turn, Crab Walk
- Speed slider (10-100%)
- E-stop button (always visible)
- Battery monitoring
- Servo trim adjustment
- LED and horn quick actions
- WebSocket connection with auto-reconnect
- Installable PWA (Add to Home Screen)
- Responsive: portrait, landscape, tablet/desktop

## Phase 2 Additions (planned)
- Live camera feeds (MJPEG via WebSocket)
- Virtual joystick (nipplejs library)
- SLAM map display
- GPS waypoint editor
- Geofence editor
- Camera selector (7 cameras)
- System health dashboard
- OTA firmware update
- Backup/restore settings

## Architecture
- **Phase 1**: PWA served by ESP32-S3 web server (port 80 HTTP, port 81 WebSocket)
- **Phase 2**: PWA served by Jetson via ROS2 web_server_node (port 8080 HTTP, port 8081 WebSocket)

## Files
```
pwa/
├── index.html          # Single page application
├── manifest.json       # PWA manifest (installable)
├── sw.js               # Service worker (network-first, v1)
├── css/
│   └── styles.css      # Catppuccin Mocha theme, responsive layout
├── js/
│   ├── app.js          # Main app logic, UI updates, section toggling
│   ├── connection.js   # WebSocket manager with exponential backoff
│   └── controls.js     # D-pad touch handling, steering modes, E-stop
├── icons/
│   ├── rover-192.png   # App icon (to be created)
│   └── rover-512.png   # App icon (to be created)
└── lib/
    ├── nipplejs.min.js # Virtual joystick (Phase 2, ~8KB)
    └── leaflet.min.js  # Map library (Phase 2, ~40KB)
```

## WebSocket Protocol
```json
// Send command (phone → rover)
{"cmd": "fwd", "speed": 50, "mode": 0}
{"cmd": "stop"}
{"cmd": "estop"}
{"cmd": "mode", "mode": 1}

// Receive status (rover → phone)
{"batt": 7.4, "pct": 78, "ml": 50, "mr": 50, "mode": 0, "estop": false}
```

## Design Language
- Theme: Catppuccin Mocha (dark)
- Accent: Mars Red (#f38ba8)
- Secondary: Sand (#f9e2af)
- Font: Plus Jakarta Sans (headings), system sans (body)
- Tap targets: 48px minimum
- Touch-optimised (touchstart/touchend, no click)

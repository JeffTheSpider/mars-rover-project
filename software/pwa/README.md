# Rover Control PWA

Browser-based phone app for controlling the Mars Rover.

## Features
- Live camera feeds with 360-degree view (swipe to rotate)
- Virtual joystick + throttle for manual driving
- GPS map with waypoint planning and geofence
- Robotic arm control (manual + gesture presets)
- Dashboard (battery, speed, temp, GPS, weather)
- Autonomous mode controls (destinations, patrol routes)
- Anti-theft settings and alerts
- Camera recordings viewer

## Tech Stack
- HTML/CSS/JS (Catppuccin Mocha theme, consistent with Hub PWA)
- WebSocket for real-time control
- WebRTC for camera streams
- Gamepad API for physical controller support
- Service Worker for offline capability

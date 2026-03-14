# Jetson Orin Nano Software

High-level brain for the Mars Rover. Runs ROS2 Humble on Ubuntu.

## Components
- **ROS2 nodes**: Navigation, SLAM, sensor fusion, camera management
- **AI pipeline**: YOLO v8 object detection, depth processing
- **Web server**: Express/Flask, WebSocket for phone control, WebRTC for camera streams
- **Camera manager**: 7 camera feeds, 360-degree stitching, zoom control
- **Arm controller**: Inverse kinematics, gesture library
- **Anti-theft**: Geofence, motion detect, GPS tracking, alarm

## Communication
UART to ESP32-S3 at 115200 baud, binary packet protocol.

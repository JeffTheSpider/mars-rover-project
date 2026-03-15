# ROS2 Software Architecture Research

**Date**: 2026-03-15
**Source**: Research agent — Nav2 docs, robot_localization, community rover projects

## Key Architectural Decisions

1. **Dual EKF** — local (odom→base_link, no GPS) + global (map→odom, with GPS). Prevents GPS jumps from causing jerky motor commands.
2. **SmacPlannerHybrid** (Hybrid-A*) — respects min turning radius and non-holonomic constraints. Essential for Ackermann.
3. **RegulatedPurePursuit controller** with `use_rotate_to_heading: false` — prevents impossible spin-in-place commands.
4. **No "spin" recovery behavior** — Ackermann rovers cannot spin in place. Only use `backup` and `wait`.
5. **MJPEG for USB cameras** — reduces bandwidth ~10x, making 4 simultaneous USB cameras feasible.
6. **Lifecycle-managed cameras** — only stream side/rear when needed to prevent USB saturation.
7. **TensorRT FP16** for YOLO — ~30-60 FPS on Orin Nano Super at 640x640 input.
8. **slam_toolbox online_async** — lightweight 2D SLAM, ~5% CPU. rtabmap optional for visual mapping.
9. **BT.CPP v4 ReactiveSequence** — safety monitor can pre-empt any running behaviour instantly.

## USB Camera Bandwidth Analysis

USB 3.0 practical: ~3.2 Gbps shared across single root hub.
7 cameras at 1080p30 raw = ~1.3 GB/s = way over budget.

**Solution — tiered approach:**
- Tier 1: OAK-D Lite on dedicated USB 3.0 port (~50 MB/s with on-device processing)
- Tier 2: 4x USB cameras at 640x480 MJPEG @ 15fps = ~12 MB/s total (fits USB 2.0 hub)
- Tier 3: Side/rear cameras lifecycle-managed, activated on demand

**udev rules for persistent camera names:**
```
SUBSYSTEM=="video4linux", ATTRS{idVendor}=="xxxx", KERNELS=="1-2.1", SYMLINK+="cam_front"
```

## Nav2 Critical Settings for Ackermann

```yaml
FollowPath:
  plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
  use_rotate_to_heading: false  # CRITICAL — Ackermann cannot rotate in place
  allow_reversing: true

GridBased:
  plugin: "nav2_smac_planner/SmacPlannerHybrid"
  minimum_turning_radius: 0.8  # meters
  motion_model_for_search: "DUBIN"  # forward-only Ackermann

behavior_server:
  behavior_plugins: ["backup", "wait"]
  # NO "spin" — Ackermann cannot spin in place
```

## Dual EKF Configuration

```yaml
ekf_local:  # odom frame, continuous, no GPS
  world_frame: odom
  odom0: /wheel_odom      # x, y, yaw, vx, vy, vyaw
  imu0: /imu/data         # orientation, angular vel, linear accel

ekf_global:  # map frame, with GPS
  world_frame: map
  odom0: /wheel_odom
  imu0: /imu/data
  odom1: /odometry/gps    # x, y position from navsat_transform

navsat_transform:
  magnetic_declination_radians: -0.0175  # ~-1 deg for UK
```

## TF Tree

```
map → odom → base_link
  ├── lidar_link, imu_link, gps_link (static)
  ├── oakd_link → optical frames
  ├── cam_{front,rear,left,right}_link (static)
  ├── ultrasonic_{fl,fr,l,r,rl,rr}_link (static)
  ├── mast_base → mast_pan → mast_tilt (dynamic)
  ├── arm_{left,right}_base → joints (dynamic)
  └── {fl,fr,ml,mr,rl,rr}_wheel_link (dynamic)
```

## YOLO TensorRT Pipeline

```bash
yolo export model=yolov8n.pt format=onnx imgsz=640
trtexec --onnx=yolov8n.onnx --saveEngine=yolov8n.engine --fp16
```

## Key ROS2 Packages (Humble)

Core: nav2_bringup, slam_toolbox, robot_localization
Sensors: rplidar_ros, depthai_ros_driver, v4l2_camera, nmea_navsat_driver
Perception: vision_msgs, cv_bridge, depth_image_proc, pcl_ros
Behaviour: behaviortree_cpp, nav2_behavior_tree
Viz: foxglove_bridge (web-based alternative to rviz)

## Behaviour Tree Structure

```
MainTree (ReactiveSequence)
├── SafetyCheck (always runs, pre-empts everything)
└── Fallback
    ├── ReturnToHome (if battery < 20%)
    └── Fallback
        ├── PatrolMission (waypoint following + scanning)
        ├── ExploreMission (frontier exploration)
        └── IdleAtDock
```

## Launch File Architecture

```
rover_bringup/launch/
  rover_bringup.launch.py    # Master — includes all with conditional flags
  sensors.launch.py          # LiDAR, IMU, GPS, ultrasonics, cameras
  localization.launch.py     # Dual EKF + navsat_transform
  navigation.launch.py       # Nav2 full stack
  slam.launch.py             # slam_toolbox
  perception.launch.py       # YOLO, obstacle fusion
  teleop.launch.py           # Manual control
  mission.launch.py          # BT engine + mission planner
```

Usage: `ros2 launch rover_bringup rover_bringup.launch.py use_mission:=true`

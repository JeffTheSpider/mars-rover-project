# Engineering Analysis 13: ROS2 Software Architecture

**Document**: EA-13
**Date**: 2026-03-15
**Purpose**: Define the complete ROS2 software architecture for the Jetson Orin Nano, including node design, topic structure, navigation stack configuration, AI pipeline, and launch file organisation.
**Depends on**: EA-04 (Compute), EA-09 (GPIO), EA-10 (Steering), EA-12 (UART Protocol), EA-18 (Binary UART)
**See also**: `docs/references/ros2-architecture-research.md` — detailed Nav2 config, dual EKF YAML, camera bandwidth analysis, TensorRT pipeline, launch file examples

---

## 1. Platform & Version

| Component | Version | Notes |
|-----------|---------|-------|
| OS | Ubuntu 22.04 LTS (JetPack 6.x) | NVIDIA's Jetson image |
| ROS2 | Humble Hawksbill (LTS) | End of life May 2027 |
| Python | 3.10 | Ubuntu 22.04 default |
| C++ | C++17 | For performance-critical nodes |
| Build system | colcon | Standard ROS2 build |
| Middleware | CycloneDDS | Default for Humble, good for single-robot |

---

## 2. Package Structure

```
~/rover_ws/src/
├── rover_bringup/          # Launch files, config YAML, URDF
│   ├── launch/
│   │   ├── rover.launch.py         # Full system launch
│   │   ├── teleop.launch.py        # Manual driving only
│   │   ├── nav.launch.py           # Navigation stack
│   │   ├── perception.launch.py    # Cameras + AI
│   │   └── hardware.launch.py      # UART + sensors only
│   ├── config/
│   │   ├── nav2_params.yaml        # Nav2 configuration
│   │   ├── ekf.yaml                # robot_localization EKF
│   │   ├── controller.yaml         # ros2_control config
│   │   └── camera_params.yaml      # Camera intrinsics
│   ├── urdf/
│   │   └── rover.urdf.xacro        # Robot model + TF frames
│   └── maps/                       # Saved SLAM maps
│
├── rover_hardware/          # Hardware interface
│   ├── src/
│   │   ├── uart_bridge_node.cpp    # UART ↔ ROS2 bridge
│   │   └── hardware_interface.cpp  # ros2_control hardware
│   └── include/
│
├── rover_perception/        # Cameras + AI
│   ├── src/
│   │   ├── yolo_node.py            # Object detection
│   │   ├── camera_manager.py       # Multi-camera handler
│   │   └── depth_processor.py      # OAK-D depth processing
│
├── rover_navigation/        # Navigation + planning
│   ├── src/
│   │   ├── ackermann_controller.py # Twist → wheel speeds + angles
│   │   ├── waypoint_follower.py    # GPS waypoint navigation
│   │   └── geofence_node.py        # Boundary enforcement
│
├── rover_autonomy/          # High-level behaviours
│   ├── src/
│   │   ├── behaviour_tree_node.py  # BT.CPP behaviours
│   │   └── mission_planner.py      # Mission sequencing
│   └── behaviour_trees/
│       ├── patrol.xml              # Patrol route BT
│       ├── explore.xml             # Random exploration BT
│       └── return_home.xml         # Return-to-home BT
│
├── rover_teleop/            # Phone app interface
│   ├── src/
│   │   ├── web_server_node.py      # WebSocket + REST API
│   │   └── joy_mapper.py           # Gamepad input
│   └── web/
│       └── pwa/                    # Phone PWA files
│
└── rover_msgs/              # Custom message definitions
    └── msg/
        ├── WheelSpeeds.msg         # 6 wheel speed values
        ├── SteeringAngles.msg      # 4 servo angles
        ├── RoverStatus.msg         # Battery, temp, state
        └── Detection.msg           # YOLO detection result
```

---

## 3. Node Architecture

### 3.1 Node Graph

```
                        ┌──────────────────┐
                        │  behaviour_tree   │
                        │  (autonomy)       │
                        └────────┬──────────┘
                                 │ /goal_pose
                                 ▼
┌──────────┐    ┌─────────────────────────────┐    ┌──────────┐
│ teleop   │───▶│        Nav2 Stack            │───▶│ ackermann│
│ web_srv  │    │ (planner + controller +      │    │controller│
└──────────┘    │  costmap + recovery)         │    └────┬─────┘
   /cmd_vel     └──────────┬──────────────────┘         │
                           │ /cmd_vel                    │ /wheel_speeds
                           ▼                             │ /steering_angles
                    ┌──────────────┐                     ▼
                    │ ackermann    │              ┌──────────────┐
                    │ controller   │──────────────│ uart_bridge  │
                    └──────────────┘              │ (ESP32 comms)│
                                                 └──────┬───────┘
                                                        │ UART
                                                        ▼
                                                 ┌──────────────┐
                                                 │   ESP32-S3   │
                                                 │ (motors,     │
                                                 │  servos,     │
                                                 │  sensors)    │
                                                 └──────────────┘

Sensor data flow:
ESP32 → uart_bridge → /encoders, /imu, /battery
RPLidar → /scan
OAK-D → /depth, /rgb
Cameras → /camera_N/image_raw
GPS → /gps/fix

Fusion:
/encoders + /imu + /gps → robot_localization EKF → /odom
/scan + /odom → slam_toolbox → /map + /tf (map→odom)
```

### 3.2 Node Descriptions

| Node | Language | Function | Frequency |
|------|----------|----------|-----------|
| **uart_bridge** | C++ | Translates between UART protocol (EA-12) and ROS2 topics | 50 Hz |
| **ackermann_controller** | Python | Converts Twist (/cmd_vel) to 6 wheel speeds + 4 steering angles using EA-10 Ackermann math | 50 Hz |
| **robot_localization** | C++ (pkg) | EKF sensor fusion: IMU + encoders + GPS → odometry | 50 Hz |
| **slam_toolbox** | C++ (pkg) | Online SLAM from LIDAR scans → map + localisation | 5 Hz |
| **nav2** | C++ (pkg) | Path planning, obstacle avoidance, behaviour recovery | 20 Hz |
| **yolo_node** | Python | YOLO v8 object detection on camera feeds via TensorRT | 10-30 Hz |
| **camera_manager** | Python | Manages 7 cameras: grab frames, publish, handle USB bandwidth | Per camera |
| **depth_processor** | Python | OAK-D depth map → pointcloud for 3D obstacle detection | 15 Hz |
| **geofence_node** | Python | GPS boundary check, override cmd_vel if outside fence | 1 Hz |
| **web_server_node** | Python | WebSocket server for phone PWA — teleop + status display | Event-driven |
| **waypoint_follower** | Python | Loads GPS waypoint lists, sends goals to Nav2 sequentially | Event-driven |
| **behaviour_tree** | C++ | BT.CPP runtime: patrol, explore, return-to-home behaviours | 10 Hz |

---

## 4. Topics & Messages

### 4.1 Core Topics

| Topic | Message Type | Publisher | Subscriber | Rate |
|-------|-------------|-----------|------------|------|
| `/cmd_vel` | `geometry_msgs/Twist` | teleop / Nav2 | ackermann_controller | 50 Hz |
| `/wheel_speeds` | `rover_msgs/WheelSpeeds` | ackermann_controller | uart_bridge | 50 Hz |
| `/steering_angles` | `rover_msgs/SteeringAngles` | ackermann_controller | uart_bridge | 50 Hz |
| `/encoders` | `sensor_msgs/JointState` | uart_bridge | robot_localization | 50 Hz |
| `/imu/data` | `sensor_msgs/Imu` | uart_bridge | robot_localization | 50 Hz |
| `/gps/fix` | `sensor_msgs/NavSatFix` | gps_driver | robot_localization, geofence | 5 Hz |
| `/scan` | `sensor_msgs/LaserScan` | rplidar_node | slam_toolbox, Nav2 | 5.5 Hz |
| `/odom` | `nav_msgs/Odometry` | robot_localization | Nav2, slam_toolbox | 50 Hz |
| `/map` | `nav_msgs/OccupancyGrid` | slam_toolbox | Nav2 | 1 Hz |
| `/battery` | `sensor_msgs/BatteryState` | uart_bridge | web_server, behaviour | 1 Hz |
| `/rover/status` | `rover_msgs/RoverStatus` | uart_bridge | web_server | 1 Hz |
| `/estop` | `std_msgs/Bool` | web_server, geofence | uart_bridge | Event |

### 4.2 Camera Topics

| Topic | Message Type | Source | Rate | Resolution |
|-------|-------------|--------|------|------------|
| `/camera/front/image_raw` | `sensor_msgs/Image` | Arducam #1 | 15 Hz | 640×480 |
| `/camera/rear/image_raw` | `sensor_msgs/Image` | Arducam #2 | 15 Hz | 640×480 |
| `/camera/left/image_raw` | `sensor_msgs/Image` | Arducam #3 | 10 Hz | 640×480 |
| `/camera/right/image_raw` | `sensor_msgs/Image` | Arducam #4 | 10 Hz | 640×480 |
| `/camera/mast/image_raw` | `sensor_msgs/Image` | ELP 10× zoom | 15 Hz | 1920×1080 |
| `/depth/image_raw` | `sensor_msgs/Image` | OAK-D Lite depth | 15 Hz | 640×480 |
| `/depth/rgb/image_raw` | `sensor_msgs/Image` | OAK-D Lite RGB | 15 Hz | 640×480 |
| `/camera/ir/image_raw` | `sensor_msgs/Image` | Pi NoIR | 10 Hz | 640×480 |
| `/detections` | `rover_msgs/Detection[]` | yolo_node | 10 Hz | — |

**USB Bandwidth Management** (critical):
- 7 cameras at 1080p30 raw = ~1.3 GB/s — far exceeds USB 3.0 practical bandwidth (~3.2 Gbps)
- **Tier 1**: OAK-D Lite on dedicated USB 3.0 port (~50 MB/s with on-device ISP/H.264)
- **Tier 2**: 4× USB cameras at 640×480 MJPEG @ 15fps = ~12 MB/s total (fits USB 2.0 hub)
- **Tier 3**: Side/rear cameras are **lifecycle-managed** — only stream when needed (turns, parking)
- Front camera always on (navigation + YOLO input)
- Use `v4l2_camera` with `pixel_format: mjpeg` (not raw YUYV)
- Assign persistent `/dev/video*` names via udev rules based on USB port path, not plug order

### 4.3 Custom Messages

```
# WheelSpeeds.msg
float32[6] speeds  # -100.0 to +100.0, percentage
# [0]=FL, [1]=ML, [2]=RL, [3]=RR, [4]=MR, [5]=FR

# SteeringAngles.msg
float32[4] angles  # degrees, -35.0 to +35.0
# [0]=FL, [1]=FR, [2]=RL, [3]=RR

# RoverStatus.msg
uint8 state        # 0=boot, 1=ready, 2=armed, 3=driving, 4=estop, 5=error
float32 battery_v
uint8 battery_pct
float32 temperature
uint32 uptime_s
string error_msg

# Detection.msg
string class_name
float32 confidence
int32[4] bbox      # x, y, width, height in pixels
float32 distance   # estimated distance in metres (if depth available)
```

---

## 5. TF2 Transform Tree

```
map
 └── odom                        (published by robot_localization EKF)
      └── base_link              (centre of rover, ground level)
           ├── base_footprint    (ground projection)
           ├── imu_link          (BNO055 location)
           ├── gps_link          (GPS antenna location)
           ├── lidar_link        (RPLidar A1, top deck)
           ├── chassis           (body frame)
           │    ├── left_rocker
           │    │    ├── wheel_fl
           │    │    └── left_bogie
           │    │         ├── wheel_ml
           │    │         └── wheel_rl
           │    └── right_rocker
           │         ├── wheel_fr
           │         └── right_bogie
           │              ├── wheel_mr
           │              └── wheel_rr
           ├── camera_front      (Arducam #1)
           ├── camera_rear       (Arducam #2)
           ├── camera_left       (Arducam #3)
           ├── camera_right      (Arducam #4)
           ├── mast_base
           │    └── mast_head    (pan-tilt, variable TF)
           │         ├── camera_mast (ELP zoom)
           │         └── camera_ir   (Pi NoIR)
           ├── depth_camera      (OAK-D Lite)
           ├── arm_left_base
           │    └── arm_left_ee  (end effector)
           └── arm_right_base
                └── arm_right_ee
```

Static transforms are published by `robot_state_publisher` from the URDF. Dynamic transforms (mast pan/tilt, arm joints) are published by their respective control nodes.

---

## 6. Navigation Stack (Nav2)

### 6.1 Configuration

```yaml
# nav2_params.yaml (key parameters)

bt_navigator:
  plugin_lib_names:
    - nav2_compute_path_to_pose_action_bt_node
    - nav2_follow_path_action_bt_node
    - nav2_back_up_action_bt_node
    # NO nav2_spin — Ackermann rovers cannot spin in place
    - nav2_wait_action_bt_node

controller_server:
  controller_frequency: 20.0
  controller_plugins: ["FollowPath"]
  FollowPath:
    # RegulatedPurePursuit — smooth path following, respects Ackermann constraints
    # DWB assumes differential drive and will generate impossible spin commands
    plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
    desired_linear_vel: 0.83   # 3 km/h in m/s (autonomous limit)
    lookahead_dist: 0.6
    min_lookahead_dist: 0.3
    max_lookahead_dist: 0.9
    lookahead_time: 1.5
    rotate_to_heading_angular_vel: 0.5
    max_angular_accel: 1.0
    allow_reversing: true
    use_rotate_to_heading: false  # CRITICAL — Ackermann cannot rotate in place

planner_server:
  planner_plugins: ["GridBased"]
  GridBased:
    plugin: "nav2_smac_planner/SmacPlannerHybrid"
    minimum_turning_radius: 0.993  # Ackermann constraint (EA-10)
    motion_model_for_search: "DUBIN"  # Forward-only Ackermann (use REEDS_SHEPP if reversing needed)

global_costmap:
  robot_radius: 0.45         # Half of 900mm body
  resolution: 0.05           # 5cm grid
  plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
  obstacle_layer:
    observation_sources: scan depth
    scan:
      topic: /scan
      sensor_model: sensor_msgs/LaserScan
    depth:
      topic: /depth/points
      sensor_model: sensor_msgs/PointCloud2

local_costmap:
  robot_radius: 0.45
  resolution: 0.05
  width: 5.0                 # 5m × 5m local costmap
  height: 5.0
  rolling_window: true
```

### 6.2 SLAM Configuration

Using `slam_toolbox` for online SLAM:

```yaml
# slam_toolbox params
slam_toolbox:
  mode: mapping              # or localization (with saved map)
  resolution: 0.05           # 5cm map resolution
  max_laser_range: 12.0      # RPLidar A1 max range
  minimum_travel_distance: 0.3
  minimum_travel_heading: 0.3
  map_update_interval: 2.0   # Update map every 2 seconds
  transform_publish_period: 0.05  # 20Hz map→odom TF
```

### 6.3 Sensor Fusion (Dual EKF)

Use two EKF instances: **local** (continuous, no GPS, smooth for motor control) and **global** (with GPS, may jump on corrections). This prevents GPS discontinuities from causing jerky motor commands. See `docs/references/ros2-architecture-research.md` for full dual YAML config.

```yaml
# ekf.yaml (robot_localization) — local EKF shown, global adds GPS odom1
ekf_filter_node:
  frequency: 50.0
  sensor_timeout: 0.5
  two_d_mode: true           # Garden rover stays on ground plane (set false for slopes)

  # IMU: provides orientation + angular velocity + linear acceleration
  imu0: /imu/data
  imu0_config: [false, false, false,   # x, y, z position
                true, true, true,       # roll, pitch, yaw
                false, false, false,    # x, y, z velocity
                true, true, true,       # roll_vel, pitch_vel, yaw_vel
                true, true, true]       # x_accel, y_accel, z_accel

  # Wheel odometry: provides x, y position + yaw
  odom0: /wheel_odom
  odom0_config: [true, true, false,    # x, y, z position
                 false, false, true,    # roll, pitch, yaw
                 false, false, false,
                 false, false, false,
                 false, false, false]

  # GPS: provides absolute x, y position (via navsat_transform)
  odom1: /gps/odom
  odom1_config: [true, true, false,    # x, y from GPS
                 false, false, false,
                 false, false, false,
                 false, false, false,
                 false, false, false]
```

---

## 7. AI Pipeline

### 7.1 YOLO Object Detection

Running on Jetson Orin Nano with TensorRT:

```python
# yolo_node.py (simplified)
import tensorrt as trt
from ultralytics import YOLO

class YoloNode(Node):
    def __init__(self):
        super().__init__('yolo_node')

        # Load YOLO v8n (nano — fastest) with TensorRT engine
        self.model = YOLO('yolov8n.engine')  # Pre-exported TensorRT

        # Subscribe to front camera (primary detection source)
        self.sub = self.create_subscription(
            Image, '/camera/front/image_raw', self.detect_callback, 10)

        # Publish detections
        self.pub = self.create_publisher(DetectionArray, '/detections', 10)

    def detect_callback(self, msg):
        # Convert ROS Image → numpy
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        # Run inference (TensorRT accelerated)
        results = self.model(frame, conf=0.5)

        # Publish detections
        for r in results[0].boxes:
            det = Detection()
            det.class_name = self.model.names[int(r.cls)]
            det.confidence = float(r.conf)
            det.bbox = [int(x) for x in r.xyxy[0]]
            self.detections.append(det)
```

**Performance on Jetson Orin Nano Super (67 TOPS)**:
- YOLOv8n: ~60 FPS at 640×480
- YOLOv8s: ~30 FPS at 640×480
- YOLOv8m: ~15 FPS at 640×480

Use YOLOv8n for real-time detection (60 FPS), YOLOv8s for higher accuracy when stationary.

### 7.2 Depth-Enhanced Detection

Combine YOLO 2D bounding boxes with OAK-D Lite depth map to get 3D positions:

```python
# For each YOLO detection:
# 1. Get centre pixel of bounding box
# 2. Look up depth at that pixel in depth map
# 3. Convert pixel + depth to 3D point using camera intrinsics
# 4. Transform to base_link frame using TF2
```

This gives estimated distance to each detected object — used for human proximity safety (EA-15).

---

## 8. Behaviour Trees

### 8.1 Patrol Behaviour

```xml
<!-- patrol.xml -->
<root main_tree_to_execute="Patrol">
  <BehaviorTree ID="Patrol">
    <Sequence>
      <CheckBattery min_percent="20"/>
      <CheckGeofence/>
      <RepeatNode num_cycles="-1">
        <Sequence>
          <GetNextWaypoint waypoints="{patrol_route}"/>
          <NavigateToWaypoint goal="{waypoint}"/>
          <Wait duration="10"/>
          <CapturePhoto camera="mast"/>
          <CheckForHumans min_distance="3.0"/>
        </Sequence>
      </RepeatNode>
    </Sequence>
  </BehaviorTree>
</root>
```

### 8.2 Return-to-Home

```xml
<!-- return_home.xml -->
<root main_tree_to_execute="ReturnHome">
  <BehaviorTree ID="ReturnHome">
    <Sequence>
      <SaveCurrentPosition name="resume_point"/>
      <SetSpeedLimit max_speed="0.56"/>  <!-- 2 km/h -->
      <NavigateToWaypoint goal="{home_position}"/>
      <AlignWithDock target="dock_aruco"/>
      <DockApproach speed="0.1"/>
      <VerifyDocked/>
      <NotifyUser message="Rover docked and charging"/>
    </Sequence>
  </BehaviorTree>
</root>
```

---

## 9. Launch File Structure

### 9.1 Full System Launch

```python
# rover.launch.py
def generate_launch_description():
    return LaunchDescription([
        # Hardware layer
        IncludeLaunchDescription('hardware.launch.py'),

        # Sensor drivers
        Node(package='rplidar_ros', executable='rplidar_node'),
        Node(package='rover_perception', executable='camera_manager'),
        Node(package='rover_perception', executable='depth_processor'),

        # Localisation
        Node(package='robot_localization', executable='ekf_node',
             parameters=['ekf.yaml']),
        Node(package='slam_toolbox', executable='async_slam_toolbox_node',
             parameters=['slam_params.yaml']),

        # Navigation
        IncludeLaunchDescription('nav.launch.py'),
        Node(package='rover_navigation', executable='geofence_node'),

        # AI
        Node(package='rover_perception', executable='yolo_node'),

        # Teleop
        Node(package='rover_teleop', executable='web_server_node'),

        # Robot model
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': urdf}]),
    ])
```

### 9.2 Mode-Specific Launches

| Launch File | Use Case | Nodes Started |
|-------------|----------|---------------|
| `hardware.launch.py` | Hardware test only | uart_bridge, robot_state_publisher |
| `teleop.launch.py` | Manual driving | hardware + web_server + ackermann_controller |
| `nav.launch.py` | Navigation test | hardware + teleop + EKF + SLAM + Nav2 |
| `perception.launch.py` | Camera/AI test | cameras + YOLO + depth |
| `rover.launch.py` | Full system | Everything |

---

## 10. Development Phases

### 10.1 Software Development Roadmap

| Step | Milestone | Dependencies |
|------|-----------|-------------|
| 1 | uart_bridge node (UART ↔ ROS2) | ESP32 firmware (done), Jetson setup |
| 2 | Ackermann controller (Twist → wheels) | uart_bridge |
| 3 | Teleop web server (phone control via ROS2) | ackermann_controller |
| 4 | Robot model (URDF + TF) | Physical measurements |
| 5 | LIDAR driver + slam_toolbox | RPLidar A1 hardware |
| 6 | EKF sensor fusion | IMU + encoder data flowing |
| 7 | Nav2 basic navigation | SLAM map + EKF odom |
| 8 | Camera pipeline | USB cameras connected |
| 9 | YOLO object detection | Camera pipeline + TensorRT export |
| 10 | Behaviour trees (patrol, explore) | Navigation working |
| 11 | GPS waypoint following | GPS module + EKF GPS fusion |
| 12 | Return-to-home + docking | GPS + vision-based alignment |

Each step is independently testable. The rover is driveable after step 3 (manual phone control through ROS2).

---

## 11. Resource Usage Estimates

### 11.1 Jetson Orin Nano Super

| Process | CPU % | GPU % | RAM (MB) | Notes |
|---------|-------|-------|----------|-------|
| Ubuntu + ROS2 core | 5% | 0% | 500 | Base overhead |
| uart_bridge | 2% | 0% | 20 | 50Hz serial parsing |
| robot_localization | 3% | 0% | 50 | EKF computation |
| slam_toolbox | 10% | 0% | 200 | SLAM is CPU-heavy |
| Nav2 | 8% | 0% | 150 | Path planning |
| camera_manager (7 cams) | 15% | 0% | 300 | USB frame grabbing |
| yolo_node (TensorRT) | 5% | 40% | 400 | GPU inference |
| depth_processor | 5% | 10% | 200 | OAK-D processing |
| web_server_node | 3% | 0% | 50 | WebSocket serving |
| **Total** | **~56%** | **~50%** | **~1,870 MB** | |

**Available**: 6-core CPU, 67 TOPS GPU, 8 GB RAM
**Headroom**: ~44% CPU, ~50% GPU, ~6 GB RAM — comfortable.

---

*Document EA-13 v1.0 — 2026-03-15*

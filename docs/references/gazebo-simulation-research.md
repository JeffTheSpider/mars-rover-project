# Gazebo Simulation Best Practices Research

**Date**: 2026-03-15
**Source**: Research agent — gazebo_ros_pkgs docs, Nav2 guides, community experience

## 1. Ackermann Steering in Gazebo

### `gazebo_ros_ackermann_drive` Plugin (Recommended for Phase 1)

Available in `gazebo_ros_pkgs` for ROS 2 Humble. Subscribes to `cmd_vel`, computes Ackermann geometry internally.

```xml
<plugin name="ackermann_drive" filename="libgazebo_ros_ackermann_drive.so">
  <num_wheel_pairs>2</num_wheel_pairs>
  <left_joint>front_left_wheel_steering_joint</left_joint>
  <right_joint>front_right_wheel_steering_joint</right_joint>
  <steering_limit>0.6</steering_limit>
  <wheel_separation>0.4</wheel_separation>
  <wheel_radius>0.1</wheel_radius>
  <publish_odom>true</publish_odom>
  <publish_odom_tf>true</publish_odom_tf>
</plugin>
```

### Migration Path
Start with `gazebo_ros_ackermann_drive` (simplest). Migrate to `gazebo_ros2_control` + `ackermann_steering_controller` when preparing for real hardware (same controller config works in sim and on physical rover).

## 2. Sensor Simulation Configs

### RPLidar A1
- Plugin: `libgazebo_ros_ray_sensor.so`, type `ray`
- 360 samples, -pi to pi, 0.15-12m range, 5.5 Hz update
- Gaussian noise stddev ~0.01m

### OAK-D Lite Depth Camera
- Plugin: `libgazebo_ros_camera.so`, type `depth`
- 640x480, 73 deg FOV, 0.2-9m range, 30 Hz
- Noise stddev ~0.005m

### BNO055 IMU
- Plugin: `libgazebo_ros_imu_sensor.so`
- 100 Hz, gyro noise 0.0002 rad/s, accel noise 0.017 m/s²

### GPS
- Plugin: `libgazebo_ros_gps_sensor.so`
- 5 Hz, horizontal noise 1.0m (consumer) or 0.01m (RTK)
- **Must set `<spherical_coordinates>` in world file** for GPS to work

### HC-SR04 Ultrasonic (6x)
- Plugin: `libgazebo_ros_ray_sensor.so`, output `sensor_msgs/Range`
- 5 samples, ±0.13 rad (15 deg cone), 0.02-4m, 20 Hz

## 3. Terrain Simulation

### Heightmap
- Image must be square, (2^n)+1 pixels (129, 257, 513)
- 8/16-bit grayscale PNG, black=low, white=high
- Multiple texture layers blend by height (grass/dirt/rock)

### Friction Values for Garden Surfaces
| Surface | mu (ODE) |
|---------|----------|
| Dry concrete | 0.8-1.0 |
| Gravel | 0.4-0.6 |
| Dry grass | 0.6-0.8 |
| Wet grass | 0.2-0.4 |
| Mud | 0.1-0.3 |
| Paving stones | 0.7-0.9 |

Use separate collision planes overlaid on heightmap with different friction per zone.

## 4. What Can Be Validated in Simulation

**Fully testable (transfers well to hardware):**
- Nav2 path planning (global + local planners)
- SLAM mapping (slam_toolbox with simulated LiDAR)
- Behaviour tree missions (pure software)
- Costmap generation and obstacle layers
- Waypoint following
- Recovery behaviors
- Launch file and TF tree validation
- rosbag2 recording/playback workflows

**Testable with caveats (needs re-tuning on hardware):**
- EKF sensor fusion (sim noise simpler than real)
- Obstacle avoidance (sim physics imperfect)
- Camera-based detection (lighting differs)

## 5. Known Issues & Gotchas

### Critical
- **Always set `use_sim_time:=true`** in ALL launch files — mixed sim/wall time causes silent TF failures
- **Spherical coordinates required** in world file for GPS simulation
- **Inertia values matter** — missing/wrong `<inertial>` causes flying/sinking robots

### Performance
- 4 cameras + LiDAR + depth = GPU-heavy (~10-20 FPS on RTX 3060)
- Mitigate: reduce camera resolution (320x240), lower update rates, `GAZEBO_GUI=false`
- Disable shadows: `<shadows>false</shadows>` for better FPS

### Nav2 Common Issues
- Costmap not updating → check topic names match between Gazebo plugins and nav2_params.yaml
- Robot not moving → `min_vel_x` too high, set to 0.0
- Recovery behavior loops → local costmap too small or inflation radius too large
- "Could not transform global plan" → missing TF link in chain

### Model/URDF
- Use simplified collision geometry (boxes/cylinders), not detailed STL meshes
- Steering joints need `<limit>` tags to prevent 360° rotation
- Every link with mass needs realistic inertia tensors

## Sources

- [gazebo_ros_pkgs (ROS 2 Humble)](https://github.com/ros-simulation/gazebo_ros_pkgs)
- [Nav2 Setup Guides](https://navigation.ros.org/setup_guides/)
- [robot_localization docs](https://docs.ros.org/en/humble/p/robot_localization/)
- [slam_toolbox (ROS 2)](https://github.com/SteveMacenski/slam_toolbox)
- [Gazebo Classic Tutorials](https://classic.gazebosim.org/tutorials)

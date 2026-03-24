#ifndef ROVER_HARDWARE__UART_BRIDGE_HPP_
#define ROVER_HARDWARE__UART_BRIDGE_HPP_

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/bool.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <sensor_msgs/msg/battery_state.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <sensor_msgs/msg/range.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <rover_msgs/msg/wheel_speeds.hpp>
#include <rover_msgs/msg/steering_angles.hpp>
#include <rover_msgs/msg/rover_status.hpp>

#include <string>
#include <mutex>
#include <atomic>

namespace rover_hardware
{

/// NMEA-style UART bridge between Jetson and ESP32 motor controller.
/// Protocol: $CMD,data*XOR\n
/// Sends: MOT (motor), STR (steering), STP (stop), ARM/DSA (arm/disarm), PNG (ping)
/// Receives: ENC (encoders), IMU (orientation/gyro/accel), USS (ultrasonics),
///           BAT (battery), STS (status), ACK, ERR
class UartBridgeNode : public rclcpp::Node
{
public:
  explicit UartBridgeNode(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());
  ~UartBridgeNode() override;

private:
  // Serial port management
  bool open_serial();
  void close_serial();
  bool write_serial(const std::string & data);
  std::string read_line();

  // NMEA protocol
  std::string format_nmea(const std::string & cmd, const std::string & data);
  bool parse_nmea(const std::string & line, std::string & cmd, std::string & data);
  uint8_t compute_checksum(const std::string & sentence);

  // Callbacks
  void wheel_speeds_callback(const rover_msgs::msg::WheelSpeeds::SharedPtr msg);
  void steering_angles_callback(const rover_msgs::msg::SteeringAngles::SharedPtr msg);
  void estop_callback(const std_msgs::msg::Bool::SharedPtr msg);
  void arm_callback(const std_msgs::msg::Bool::SharedPtr msg);

  // Timer callbacks
  void serial_read_callback();
  void ping_callback();
  void watchdog_callback();

  // Message parsing
  void handle_encoder_msg(const std::string & data);
  void handle_imu_msg(const std::string & data);
  void handle_ultrasonic_msg(const std::string & data);
  void handle_battery_msg(const std::string & data);
  void handle_status_msg(const std::string & data);

  // Odometry computation
  void compute_odometry(double left_ticks, double right_ticks);

  // Publishers
  rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr encoder_pub_;
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu_pub_;
  rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr ultrasonic_pubs_[6];
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  rclcpp::Publisher<sensor_msgs::msg::BatteryState>::SharedPtr battery_pub_;
  rclcpp::Publisher<rover_msgs::msg::RoverStatus>::SharedPtr status_pub_;

  // Subscribers
  rclcpp::Subscription<rover_msgs::msg::WheelSpeeds>::SharedPtr wheel_speeds_sub_;
  rclcpp::Subscription<rover_msgs::msg::SteeringAngles>::SharedPtr steering_sub_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr estop_sub_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr arm_sub_;

  // Timers
  rclcpp::TimerBase::SharedPtr serial_read_timer_;
  rclcpp::TimerBase::SharedPtr ping_timer_;
  rclcpp::TimerBase::SharedPtr watchdog_timer_;

  // Serial state
  int serial_fd_;
  std::mutex serial_mutex_;
  std::string read_buffer_;

  // Parameters
  std::string serial_port_;
  int baud_rate_;
  int command_rate_hz_;

  // Watchdog
  std::atomic<rclcpp::Time> last_cmd_time_;
  std::atomic<rclcpp::Time> last_esp_time_;
  std::atomic<bool> estop_active_;

  // Mutex protecting shared sensor/odometry state between UART read thread
  // and main ROS thread (if using multi-threaded executor)
  std::mutex data_mutex_;

  // Odometry state (protected by data_mutex_)
  double odom_x_{0.0};
  double odom_y_{0.0};
  double odom_yaw_{0.0};
  rclcpp::Time last_odom_time_;
  double prev_ticks_left_{0.0};
  double prev_ticks_right_{0.0};
  bool odom_initialized_{false};

  // Constants
  static constexpr double WHEEL_RADIUS_M = 0.040;  // 80mm diameter / 2
  static constexpr double TRACK_WIDTH_M = 0.280;    // 280mm wheel-to-wheel
  static constexpr double TICKS_PER_REV = 360.0;    // Encoder ticks per revolution

  // Joint names for encoder publishing
  static constexpr const char * JOINT_NAMES[] = {
    "front_left_wheel", "mid_left_wheel", "rear_left_wheel",
    "rear_right_wheel", "mid_right_wheel", "front_right_wheel"
  };

  // Ultrasonic sensor frame names
  static constexpr const char * US_FRAME_NAMES[] = {
    "ultrasonic_fl_link", "ultrasonic_fr_link",
    "ultrasonic_l_link", "ultrasonic_r_link",
    "ultrasonic_rl_link", "ultrasonic_rr_link"
  };
};

}  // namespace rover_hardware

#endif  // ROVER_HARDWARE__UART_BRIDGE_HPP_

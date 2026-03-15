#ifndef ROVER_HARDWARE__UART_BRIDGE_HPP_
#define ROVER_HARDWARE__UART_BRIDGE_HPP_

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/bool.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <sensor_msgs/msg/battery_state.hpp>
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
/// Sends: MOT (motor), STR (steering), STP (stop), PNG (ping)
/// Receives: ENC (encoders), BAT (battery), STS (status), ACK, ERR
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

  // Timer callbacks
  void serial_read_callback();
  void ping_callback();
  void watchdog_callback();

  // Message parsing
  void handle_encoder_msg(const std::string & data);
  void handle_battery_msg(const std::string & data);
  void handle_status_msg(const std::string & data);

  // Publishers
  rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr encoder_pub_;
  rclcpp::Publisher<sensor_msgs::msg::BatteryState>::SharedPtr battery_pub_;
  rclcpp::Publisher<rover_msgs::msg::RoverStatus>::SharedPtr status_pub_;

  // Subscribers
  rclcpp::Subscription<rover_msgs::msg::WheelSpeeds>::SharedPtr wheel_speeds_sub_;
  rclcpp::Subscription<rover_msgs::msg::SteeringAngles>::SharedPtr steering_sub_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr estop_sub_;

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

  // Joint names for encoder publishing
  static constexpr const char * JOINT_NAMES[] = {
    "front_left_wheel", "mid_left_wheel", "rear_left_wheel",
    "rear_right_wheel", "mid_right_wheel", "front_right_wheel"
  };
};

}  // namespace rover_hardware

#endif  // ROVER_HARDWARE__UART_BRIDGE_HPP_

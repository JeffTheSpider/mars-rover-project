#include "rover_hardware/uart_bridge.hpp"

#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <cstring>
#include <sstream>
#include <vector>
#include <algorithm>
#include <cmath>

namespace rover_hardware
{

constexpr const char * UartBridgeNode::JOINT_NAMES[];

UartBridgeNode::UartBridgeNode(const rclcpp::NodeOptions & options)
: Node("uart_bridge", options),
  serial_fd_(-1),
  estop_active_(false)
{
  // Declare parameters
  this->declare_parameter("serial_port", "/dev/ttyTHS1");
  this->declare_parameter("baud_rate", 115200);
  this->declare_parameter("command_rate_hz", 50);
  this->declare_parameter("watchdog_timeout_ms", 200);
  this->declare_parameter("ping_interval_ms", 1000);

  serial_port_ = this->get_parameter("serial_port").as_string();
  baud_rate_ = this->get_parameter("baud_rate").as_int();
  command_rate_hz_ = this->get_parameter("command_rate_hz").as_int();
  int watchdog_ms = this->get_parameter("watchdog_timeout_ms").as_int();
  int ping_ms = this->get_parameter("ping_interval_ms").as_int();

  RCLCPP_INFO(this->get_logger(), "UART Bridge starting on %s @ %d baud",
    serial_port_.c_str(), baud_rate_);

  // Publishers
  encoder_pub_ = this->create_publisher<sensor_msgs::msg::JointState>(
    "/encoders", 10);
  battery_pub_ = this->create_publisher<sensor_msgs::msg::BatteryState>(
    "/battery", 10);
  status_pub_ = this->create_publisher<rover_msgs::msg::RoverStatus>(
    "/rover/status", 10);

  // Subscribers
  wheel_speeds_sub_ = this->create_subscription<rover_msgs::msg::WheelSpeeds>(
    "/wheel_speeds", 10,
    std::bind(&UartBridgeNode::wheel_speeds_callback, this, std::placeholders::_1));
  steering_sub_ = this->create_subscription<rover_msgs::msg::SteeringAngles>(
    "/steering_angles", 10,
    std::bind(&UartBridgeNode::steering_angles_callback, this, std::placeholders::_1));
  estop_sub_ = this->create_subscription<std_msgs::msg::Bool>(
    "/estop", 10,
    std::bind(&UartBridgeNode::estop_callback, this, std::placeholders::_1));

  // Open serial port
  if (!open_serial()) {
    RCLCPP_ERROR(this->get_logger(), "Failed to open serial port %s", serial_port_.c_str());
    RCLCPP_WARN(this->get_logger(), "Running in MOCK mode - no serial communication");
  }

  // Timers
  // Read serial at 200Hz (5ms) to keep buffer clear
  serial_read_timer_ = this->create_wall_timer(
    std::chrono::milliseconds(5),
    std::bind(&UartBridgeNode::serial_read_callback, this));

  // Ping ESP32 periodically
  ping_timer_ = this->create_wall_timer(
    std::chrono::milliseconds(ping_ms),
    std::bind(&UartBridgeNode::ping_callback, this));

  // Watchdog: send stop if no commands received recently
  watchdog_timer_ = this->create_wall_timer(
    std::chrono::milliseconds(watchdog_ms),
    std::bind(&UartBridgeNode::watchdog_callback, this));

  last_cmd_time_.store(this->now());
  last_esp_time_.store(this->now());

  RCLCPP_INFO(this->get_logger(), "UART Bridge node initialized (%d Hz command rate)",
    command_rate_hz_);
}

UartBridgeNode::~UartBridgeNode()
{
  // Send stop command before shutting down
  write_serial(format_nmea("STP", "0"));
  close_serial();
}

bool UartBridgeNode::open_serial()
{
  std::lock_guard<std::mutex> lock(serial_mutex_);

  serial_fd_ = open(serial_port_.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
  if (serial_fd_ < 0) {
    RCLCPP_ERROR(this->get_logger(), "open(%s) failed: %s",
      serial_port_.c_str(), strerror(errno));
    return false;
  }

  struct termios tty;
  memset(&tty, 0, sizeof(tty));

  if (tcgetattr(serial_fd_, &tty) != 0) {
    RCLCPP_ERROR(this->get_logger(), "tcgetattr failed: %s", strerror(errno));
    close(serial_fd_);
    serial_fd_ = -1;
    return false;
  }

  // Set baud rate
  speed_t baud;
  switch (baud_rate_) {
    case 9600: baud = B9600; break;
    case 19200: baud = B19200; break;
    case 38400: baud = B38400; break;
    case 57600: baud = B57600; break;
    case 115200: baud = B115200; break;
    default:
      RCLCPP_ERROR(this->get_logger(), "Unsupported baud rate: %d", baud_rate_);
      close(serial_fd_);
      serial_fd_ = -1;
      return false;
  }

  cfsetispeed(&tty, baud);
  cfsetospeed(&tty, baud);

  // 8N1 configuration
  tty.c_cflag &= ~PARENB;   // No parity
  tty.c_cflag &= ~CSTOPB;   // 1 stop bit
  tty.c_cflag &= ~CSIZE;
  tty.c_cflag |= CS8;        // 8 data bits
  tty.c_cflag &= ~CRTSCTS;  // No hardware flow control
  tty.c_cflag |= CREAD | CLOCAL;  // Enable receiver, ignore modem controls

  // Raw input mode
  tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
  tty.c_iflag &= ~(IXON | IXOFF | IXANY);
  tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);

  // Raw output mode
  tty.c_oflag &= ~OPOST;

  // Non-blocking read
  tty.c_cc[VMIN] = 0;
  tty.c_cc[VTIME] = 0;

  if (tcsetattr(serial_fd_, TCSANOW, &tty) != 0) {
    RCLCPP_ERROR(this->get_logger(), "tcsetattr failed: %s", strerror(errno));
    close(serial_fd_);
    serial_fd_ = -1;
    return false;
  }

  // Flush any existing data
  tcflush(serial_fd_, TCIOFLUSH);

  RCLCPP_INFO(this->get_logger(), "Serial port %s opened successfully", serial_port_.c_str());
  return true;
}

void UartBridgeNode::close_serial()
{
  std::lock_guard<std::mutex> lock(serial_mutex_);
  if (serial_fd_ >= 0) {
    close(serial_fd_);
    serial_fd_ = -1;
  }
}

bool UartBridgeNode::write_serial(const std::string & data)
{
  std::lock_guard<std::mutex> lock(serial_mutex_);
  if (serial_fd_ < 0) {
    return false;
  }

  ssize_t written = write(serial_fd_, data.c_str(), data.size());
  if (written < 0) {
    RCLCPP_WARN(this->get_logger(), "Serial write failed: %s", strerror(errno));
    return false;
  }
  return written == static_cast<ssize_t>(data.size());
}

std::string UartBridgeNode::read_line()
{
  std::lock_guard<std::mutex> lock(serial_mutex_);
  if (serial_fd_ < 0) {
    return "";
  }

  char buf[256];
  ssize_t n = read(serial_fd_, buf, sizeof(buf) - 1);
  if (n > 0) {
    buf[n] = '\0';
    read_buffer_ += buf;
  }

  // Extract complete lines
  size_t newline_pos = read_buffer_.find('\n');
  if (newline_pos != std::string::npos) {
    std::string line = read_buffer_.substr(0, newline_pos);
    read_buffer_ = read_buffer_.substr(newline_pos + 1);
    // Strip \r if present
    if (!line.empty() && line.back() == '\r') {
      line.pop_back();
    }
    return line;
  }

  // Guard against buffer overflow from garbage data
  if (read_buffer_.size() > 1024) {
    RCLCPP_WARN(this->get_logger(), "Read buffer overflow, clearing");
    read_buffer_.clear();
  }

  return "";
}

uint8_t UartBridgeNode::compute_checksum(const std::string & sentence)
{
  uint8_t checksum = 0;
  for (char c : sentence) {
    checksum ^= static_cast<uint8_t>(c);
  }
  return checksum;
}

std::string UartBridgeNode::format_nmea(const std::string & cmd, const std::string & data)
{
  std::string body = cmd + "," + data;
  uint8_t cs = compute_checksum(body);

  char buf[256];
  snprintf(buf, sizeof(buf), "$%s*%02X\n", body.c_str(), cs);
  return std::string(buf);
}

bool UartBridgeNode::parse_nmea(const std::string & line, std::string & cmd, std::string & data)
{
  // Expected format: $CMD,data*XOR
  if (line.empty() || line[0] != '$') {
    return false;
  }

  // Find checksum separator
  size_t star_pos = line.find('*');
  if (star_pos == std::string::npos || star_pos < 2) {
    return false;
  }

  // Extract body (between $ and *)
  std::string body = line.substr(1, star_pos - 1);

  // Verify checksum
  std::string cs_str = line.substr(star_pos + 1);
  if (cs_str.size() < 2) {
    return false;
  }
  uint8_t received_cs = static_cast<uint8_t>(std::stoi(cs_str.substr(0, 2), nullptr, 16));
  uint8_t computed_cs = compute_checksum(body);
  if (received_cs != computed_cs) {
    RCLCPP_WARN(this->get_logger(), "Checksum mismatch: got %02X, expected %02X",
      received_cs, computed_cs);
    return false;
  }

  // Split cmd from data
  size_t comma_pos = body.find(',');
  if (comma_pos == std::string::npos) {
    cmd = body;
    data = "";
  } else {
    cmd = body.substr(0, comma_pos);
    data = body.substr(comma_pos + 1);
  }

  return true;
}

void UartBridgeNode::wheel_speeds_callback(
  const rover_msgs::msg::WheelSpeeds::SharedPtr msg)
{
  if (estop_active_.load()) {
    RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
      "E-stop active, ignoring wheel speed command");
    return;
  }

  // Clamp speeds to [-100, 100]
  char buf[128];
  snprintf(buf, sizeof(buf), "%.1f,%.1f,%.1f,%.1f,%.1f,%.1f",
    std::clamp(msg->speeds[0], -100.0f, 100.0f),
    std::clamp(msg->speeds[1], -100.0f, 100.0f),
    std::clamp(msg->speeds[2], -100.0f, 100.0f),
    std::clamp(msg->speeds[3], -100.0f, 100.0f),
    std::clamp(msg->speeds[4], -100.0f, 100.0f),
    std::clamp(msg->speeds[5], -100.0f, 100.0f));

  write_serial(format_nmea("MOT", buf));
  last_cmd_time_.store(this->now());
}

void UartBridgeNode::steering_angles_callback(
  const rover_msgs::msg::SteeringAngles::SharedPtr msg)
{
  if (estop_active_.load()) {
    return;
  }

  // Clamp angles to [-35, 35] degrees
  char buf[64];
  snprintf(buf, sizeof(buf), "%.1f,%.1f,%.1f,%.1f",
    std::clamp(msg->angles[0], -35.0f, 35.0f),
    std::clamp(msg->angles[1], -35.0f, 35.0f),
    std::clamp(msg->angles[2], -35.0f, 35.0f),
    std::clamp(msg->angles[3], -35.0f, 35.0f));

  write_serial(format_nmea("STR", buf));
  last_cmd_time_.store(this->now());
}

void UartBridgeNode::estop_callback(const std_msgs::msg::Bool::SharedPtr msg)
{
  estop_active_.store(msg->data);
  if (msg->data) {
    RCLCPP_WARN(this->get_logger(), "E-STOP ACTIVATED");
    write_serial(format_nmea("STP", "1"));
  } else {
    RCLCPP_INFO(this->get_logger(), "E-stop released");
  }
}

void UartBridgeNode::serial_read_callback()
{
  std::string line = read_line();
  if (line.empty()) {
    return;
  }

  std::string cmd, data;
  if (!parse_nmea(line, cmd, data)) {
    RCLCPP_DEBUG(this->get_logger(), "Invalid NMEA: %s", line.c_str());
    return;
  }

  last_esp_time_.store(this->now());

  if (cmd == "ENC") {
    handle_encoder_msg(data);
  } else if (cmd == "BAT") {
    handle_battery_msg(data);
  } else if (cmd == "STS") {
    handle_status_msg(data);
  } else if (cmd == "ACK") {
    RCLCPP_DEBUG(this->get_logger(), "ACK received: %s", data.c_str());
  } else if (cmd == "ERR") {
    RCLCPP_ERROR(this->get_logger(), "ESP32 error: %s", data.c_str());
  } else {
    RCLCPP_WARN(this->get_logger(), "Unknown command: %s", cmd.c_str());
  }
}

void UartBridgeNode::handle_encoder_msg(const std::string & data)
{
  // Expected: tick0,tick1,tick2,tick3,tick4,tick5
  std::vector<double> ticks;
  std::stringstream ss(data);
  std::string token;
  while (std::getline(ss, token, ',')) {
    try {
      ticks.push_back(std::stod(token));
    } catch (...) {
      RCLCPP_WARN(this->get_logger(), "Invalid encoder value: %s", token.c_str());
      return;
    }
  }

  if (ticks.size() != 6) {
    RCLCPP_WARN(this->get_logger(), "Expected 6 encoder values, got %zu", ticks.size());
    return;
  }

  auto msg = sensor_msgs::msg::JointState();
  msg.header.stamp = this->now();
  msg.header.frame_id = "base_link";

  for (int i = 0; i < 6; i++) {
    msg.name.push_back(JOINT_NAMES[i]);
    msg.position.push_back(ticks[i]);
  }

  encoder_pub_->publish(msg);
}

void UartBridgeNode::handle_battery_msg(const std::string & data)
{
  // Expected: voltage,percentage,current
  std::vector<float> values;
  std::stringstream ss(data);
  std::string token;
  while (std::getline(ss, token, ',')) {
    try {
      values.push_back(std::stof(token));
    } catch (...) {
      return;
    }
  }

  if (values.size() < 2) {
    return;
  }

  auto msg = sensor_msgs::msg::BatteryState();
  msg.header.stamp = this->now();
  msg.voltage = values[0];
  msg.percentage = values[1] / 100.0f;
  if (values.size() >= 3) {
    msg.current = values[2];
  }
  msg.power_supply_status = sensor_msgs::msg::BatteryState::POWER_SUPPLY_STATUS_DISCHARGING;
  msg.power_supply_technology = sensor_msgs::msg::BatteryState::POWER_SUPPLY_TECHNOLOGY_LIPO;
  msg.present = true;

  battery_pub_->publish(msg);
}

void UartBridgeNode::handle_status_msg(const std::string & data)
{
  // Expected: state,temperature,uptime_s[,error_msg]
  std::vector<std::string> parts;
  std::stringstream ss(data);
  std::string token;
  while (std::getline(ss, token, ',')) {
    parts.push_back(token);
  }

  if (parts.size() < 3) {
    return;
  }

  auto msg = rover_msgs::msg::RoverStatus();
  try {
    msg.state = static_cast<uint8_t>(std::stoi(parts[0]));
    msg.temperature = std::stof(parts[1]);
    msg.uptime_s = static_cast<uint32_t>(std::stoul(parts[2]));
  } catch (...) {
    RCLCPP_WARN(this->get_logger(), "Failed to parse status message");
    return;
  }

  if (parts.size() >= 4) {
    msg.error_msg = parts[3];
  }

  status_pub_->publish(msg);
}

void UartBridgeNode::ping_callback()
{
  write_serial(format_nmea("PNG", "1"));
}

void UartBridgeNode::watchdog_callback()
{
  auto now = this->now();
  int watchdog_ms = this->get_parameter("watchdog_timeout_ms").as_int();

  // Check if we've received any commands recently
  rclcpp::Time last_cmd = last_cmd_time_.load();
  auto elapsed = (now - last_cmd).nanoseconds() / 1e6;

  if (elapsed > watchdog_ms && !estop_active_.load()) {
    // No commands received within timeout - send stop for safety
    write_serial(format_nmea("STP", "0"));
    RCLCPP_DEBUG_THROTTLE(this->get_logger(), *this->get_clock(), 5000,
      "Watchdog: no commands for %.0f ms, sending stop", elapsed);
  }

  // Check ESP32 liveness
  rclcpp::Time last_esp = last_esp_time_.load();
  auto esp_elapsed = (now - last_esp).nanoseconds() / 1e6;
  if (esp_elapsed > 5000) {
    RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 5000,
      "No response from ESP32 for %.0f ms", esp_elapsed);
  }
}

}  // namespace rover_hardware

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rover_hardware::UartBridgeNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}

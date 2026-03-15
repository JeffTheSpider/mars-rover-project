#ifndef CONFIG_H
#define CONFIG_H

// ============================================================
// Mars Rover Phase 1 — Configuration
// ESP32-S3 DevKitC-1 (N16R8)
// Version: 0.1.0
// See EA-09 for full GPIO pin map
// ============================================================

// --- Firmware Version ---
#define FW_VERSION "0.1.0"
#define FW_NAME "MarsRover-P1"

// --- WiFi ---
#define WIFI_SSID "VM9388584"
#define WIFI_PASS ""  // Set before upload
#define WIFI_HOSTNAME "rover"
#define WIFI_CONNECT_TIMEOUT_MS 15000
#define WIFI_RECONNECT_INTERVAL_MS 5000
#define WEB_SERVER_PORT 80
#define WS_PORT 81

// --- Motor Pins (L298N, 4-channel: 2 per side) ---
// Left front motor (W1)
#define MOTOR_LF_PWM  4   // LEDC Ch0
#define MOTOR_LF_IN1  5
#define MOTOR_LF_IN2  6

// Left mid+rear motors (W2+W3 in parallel)
#define MOTOR_LR_PWM  7   // LEDC Ch1
#define MOTOR_LR_IN1  15
#define MOTOR_LR_IN2  16

// Right front motor (W6)
#define MOTOR_RF_PWM  8   // LEDC Ch2
#define MOTOR_RF_IN1  9
#define MOTOR_RF_IN2  10

// Right mid+rear motors (W5+W4 in parallel)
#define MOTOR_RR_PWM  11  // LEDC Ch3
#define MOTOR_RR_IN1  12
#define MOTOR_RR_IN2  13

// --- Motor PWM Config ---
#define MOTOR_PWM_FREQ     1000   // 1 kHz for L298N
#define MOTOR_PWM_RES      8      // 8-bit (0-255)
#define MOTOR_LEDC_CH_LF   0
#define MOTOR_LEDC_CH_LR   1
#define MOTOR_LEDC_CH_RF   2
#define MOTOR_LEDC_CH_RR   3
#define MOTOR_LEDC_TIMER   0

// --- Servo Pins (SG90, direct PWM) ---
#define SERVO_FL_PIN  1    // LEDC Ch4
#define SERVO_FR_PIN  2    // LEDC Ch5
#define SERVO_RL_PIN  41   // LEDC Ch6
#define SERVO_RR_PIN  42   // LEDC Ch7

// --- Servo PWM Config ---
#define SERVO_PWM_FREQ     50     // 50 Hz standard servo
#define SERVO_PWM_RES      16     // 16-bit for precise pulse width
#define SERVO_LEDC_CH_FL   4
#define SERVO_LEDC_CH_FR   5
#define SERVO_LEDC_CH_RL   6
#define SERVO_LEDC_CH_RR   7
#define SERVO_LEDC_TIMER   1

// Servo pulse widths (microseconds)
#define SERVO_MIN_US    500
#define SERVO_MAX_US    2400
#define SERVO_CENTER_US 1500
#define SERVO_US_PER_DEG 11.11f

// Steering limits (degrees)
#define STEER_MAX_ANGLE   35.0f
#define STEER_DEADBAND    1.0f
#define STEER_MAX_RATE    60.0f   // degrees per second

// --- Encoder Pins (optional, 2 wheels for Phase 1) ---
#define ENC_W1_CHA  38
#define ENC_W1_CHB  39
#define ENC_W6_CHA  40
#define ENC_W6_CHB  48

// --- Battery Monitoring ---
#define BATT_ADC_PIN  14
#define BATT_CELLS    2          // 2S LiPo
#define BATT_FULL_V   8.4f      // 4.2V per cell × 2
#define BATT_NOMINAL_V 7.4f
#define BATT_WARN_V   7.0f      // 3.5V per cell
#define BATT_CUTOFF_V  6.4f     // 3.2V per cell
#define BATT_DIVIDER_RATIO 3.128f  // (10k + 4.7k) / 4.7k — see EA-09

// --- Status LED ---
#define STATUS_LED_PIN  0

// --- E-Stop Button ---
#define ESTOP_PIN  46   // Input-only pin, internal pull-down

// --- Rover Geometry (0.4 scale, millimetres) ---
#define WHEELBASE_MM    360.0f   // Front to rear axle
#define TRACK_WIDTH_MM  280.0f   // Wheel centre to centre
#define HALF_TRACK_MM   140.0f   // Track / 2
#define L_FM_MM         180.0f   // Front to middle axle
#define L_MR_MM         180.0f   // Middle to rear axle
#define WHEEL_RADIUS_MM  40.0f   // 80mm diameter / 2
#define MIN_TURN_RADIUS  397.0f  // See EA-10

// --- Timing ---
#define MOTOR_UPDATE_MS   20     // 50 Hz motor control loop
#define SENSOR_UPDATE_MS  100    // 10 Hz sensor reading
#define BATT_UPDATE_MS    1000   // 1 Hz battery check
#define WS_UPDATE_MS      200    // 5 Hz WebSocket status broadcast
#define WATCHDOG_TIMEOUT_S  5    // Watchdog timer (seconds)

// --- Safety ---
#define SPEED_LIMIT_PCT  100     // Max motor speed (0-100%)
#define RAMP_RATE        10      // Max speed change per update (% per tick)

#endif // CONFIG_H

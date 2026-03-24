// ============================================================
// Mars Rover — Phase 1 Firmware
// ESP32-S3 DevKitC-1 (N16R8)
// Version: 0.2.0
//
// Phase 1: 0.4 scale prototype
// - 4-channel motor control (L298N, 6 motors as 4 groups)
// - 4 SG90 steering servos (Ackermann + point turn + crab)
// - WiFi web server + WebSocket for phone control
// - NMEA text UART protocol for Jetson communication (EA-12)
// - Battery monitoring (ADC)
// - 2 wheel encoders (optional)
// - E-stop button
// - Phase 2: define PHASE2_BINARY_PROTOCOL for COBS binary UART (EA-18)
//
// Architecture: Single translation unit (.h includes)
// Same proven pattern as Clock/Lamp ESP8266 projects
//
// See EA-08 for hardware spec, EA-09 for pin map,
// EA-10 for steering geometry, EA-12 for UART protocol (Phase 2)
// ============================================================

#include <WiFi.h>
#include <esp_task_wdt.h>

#include "config.h"
#include "motors.h"
#include "steering.h"
#include "sensors.h"
#include "leds.h"
#include "rover_webserver.h"
#include "ota.h"
#include "uart_nmea.h"
#include "uart_binary.h"

// --- Timing ---
unsigned long lastMotorUpdate = 0;
unsigned long lastSensorUpdate = 0;
unsigned long lastBattUpdate = 0;
unsigned long lastCommandTime = 0;

// --- State ---
bool estopActive = false;
bool wifiConnected = false;
bool roverArmed = false;        // Must be armed before motors accept commands

// ---- Setup ----

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println();
  Serial.println("========================================");
  Serial.printf("  Mars Rover Phase 1 — v%s\n", FW_VERSION);
  Serial.println("  ESP32-S3 Motor Controller");
  Serial.println("========================================");

  // Status LED
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, LOW);

  // Initialise subsystems
  setupMotors();
  setupSteering();
  setupSensors();

  // Connect WiFi
  connectWiFi();

  // Start web server
  setupWebServer();

  // OTA firmware updates
  setupOTA();

  // Start UART for Jetson communication (Phase 1: NMEA text)
#ifndef PHASE2_BINARY_PROTOCOL
  setupUartNMEA();
#endif

  // Enable watchdog (5 second timeout)
  // ESP32 Arduino Core v3.x uses config struct
  esp_task_wdt_config_t wdt_config = {
    .timeout_ms = WATCHDOG_TIMEOUT_S * 1000,
    .idle_core_mask = 0,
    .trigger_panic = true
  };
  esp_task_wdt_init(&wdt_config);
  esp_task_wdt_add(NULL);  // Add current task

  Serial.println("[MAIN] Setup complete — ready to drive!");
  Serial.printf("[MAIN] Free heap: %d bytes\n", ESP.getFreeHeap());

  lastCommandTime = millis();
}

// ---- Main Loop ----

void loop() {
  unsigned long now = millis();

  // Feed watchdog
  esp_task_wdt_reset();

  // Handle WiFi reconnection (non-blocking)
  static bool wifiReconnecting = false;
  static unsigned long wifiReconnectStart = 0;
  if (WiFi.status() != WL_CONNECTED) {
    if (wifiConnected) {
      Serial.println("[WIFI] Disconnected — attempting reconnect");
      wifiConnected = false;
      stopAllMotors();
    }
    if (!wifiReconnecting) {
      WiFi.mode(WIFI_STA);
      WiFi.begin(WIFI_SSID, WIFI_PASS);
      wifiReconnecting = true;
      wifiReconnectStart = millis();
    } else if (millis() - wifiReconnectStart > WIFI_RECONNECT_INTERVAL_MS) {
      wifiReconnecting = false; // will retry next loop
    }
  } else {
    wifiReconnecting = false;
    if (!wifiConnected) {
      wifiConnected = true;
      String ip = WiFi.localIP().toString();
      Serial.printf("[WIFI] Reconnected! IP: %s\n", ip.c_str());
    }
  }

  // Handle OTA updates
  handleOTA();

  // Handle web server + WebSocket
  handleWeb();

  // Handle UART protocol (Jetson communication)
#ifndef PHASE2_BINARY_PROTOCOL
  handleUartNMEA();
#endif

  // Check E-stop (debounced)
  static unsigned long lastEstopChange = 0;
  bool raw = isEStopPressed();
  if (raw != estopActive && (now - lastEstopChange > 50)) {
    lastEstopChange = now;
    estopActive = raw;
    if (estopActive) {
      stopAllMotors();
      Serial.println("[ESTOP] Activated — all motors stopped");
    } else {
      Serial.println("[ESTOP] Released — ready to drive");
    }
  }

  // Motor speed ramping + steering update (50 Hz)
  if (now - lastMotorUpdate >= MOTOR_UPDATE_MS) {
    if (!estopActive && !batteryCritical && roverArmed) {
      updateMotors();
      updateSteering();
      checkStall(motorSpeed);
    } else if (!roverArmed) {
      // Silently keep motors stopped when not armed
      stopAllMotors();
    }
    lastMotorUpdate = now;
  }

  // Sensor reading (10 Hz)
  if (now - lastSensorUpdate >= SENSOR_UPDATE_MS) {
    // Encoders are interrupt-driven, no polling needed
    lastSensorUpdate = now;
  }

  // Battery monitoring (1 Hz)
  if (now - lastBattUpdate >= BATT_UPDATE_MS) {
    updateBattery();
    lastBattUpdate = now;
  }

  // Command timeout: stop motors if no command received
  // (WebSocket disconnect already stops, but this catches other cases)
  if (now - lastCommandTime > CMD_TIMEOUT_MS && (motorTarget[0] != 0 || motorTarget[1] != 0 || motorTarget[2] != 0 || motorTarget[3] != 0)) {
    stopAllMotors();
    Serial.println("[MAIN] Command timeout — motors stopped");
  }

  // Blink status LED based on state
  updateStatusLED(now);
}

// ---- WiFi Connection ----

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    return;
  }

  Serial.printf("[WIFI] Connecting to %s", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(WIFI_HOSTNAME);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < WIFI_CONNECT_TIMEOUT_MS) {
    delay(500);
    Serial.print(".");
    esp_task_wdt_reset();
  }

  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    String ip = WiFi.localIP().toString();
    Serial.printf("\n[WIFI] Connected! IP: %s\n", ip.c_str());
    Serial.printf("[WIFI] Open http://%s in browser\n", ip.c_str());
  } else {
    Serial.println("\n[WIFI] Connection failed — will retry");
  }
}

// ---- Status LED ----

// LED Patterns (5 distinct states, EA-22 DFT-07):
//   Idle (not armed):  Slow pulse (1s on, 1s off)
//   Armed (ready):     Double blink (2 quick flashes, pause)
//   Driving (active):  Solid on
//   Warning (battery): Fast blink (250ms)
//   Error (E-stop/critical): SOS pattern (3 short, 3 long, 3 short)
void updateStatusLED(unsigned long now) {
  if (estopActive) {
    // SOS pattern: 3 short (100ms), 3 long (300ms), 3 short (100ms)
    int cycle = (now % 3000);
    bool on = false;
    if (cycle < 300) on = (cycle / 100) % 2 == 0;           // 3 short
    else if (cycle < 600) on = false;                         // gap
    else if (cycle < 1500) on = ((cycle - 600) / 300) % 2 == 0;  // 3 long
    else if (cycle < 1800) on = false;                        // gap
    else if (cycle < 2100) on = ((cycle - 1800) / 100) % 2 == 0; // 3 short
    else on = false;                                          // pause
    digitalWrite(STATUS_LED_PIN, on ? HIGH : LOW);
  } else if (batteryCritical) {
    // Very fast blink — error state
    digitalWrite(STATUS_LED_PIN, (now / 100) % 2);
  } else if (batteryWarning) {
    // Fast blink — warning
    digitalWrite(STATUS_LED_PIN, (now / 250) % 2);
  } else if (stallDetected) {
    // Triple quick blink — stall warning
    int phase = (now / 120) % 8;
    digitalWrite(STATUS_LED_PIN, (phase < 6 && phase % 2 == 0) ? HIGH : LOW);
  } else if (!wifiConnected) {
    // Double blink — WiFi connecting
    int phase = (now / 150) % 6;
    digitalWrite(STATUS_LED_PIN, (phase == 0 || phase == 2) ? HIGH : LOW);
  } else if (!roverArmed) {
    // Slow pulse — idle, waiting for arm command
    digitalWrite(STATUS_LED_PIN, (now / 1000) % 2);
  } else if (motorTarget[0] != 0 || motorTarget[1] != 0 ||
             motorTarget[2] != 0 || motorTarget[3] != 0) {
    // Solid on — actively driving
    digitalWrite(STATUS_LED_PIN, HIGH);
  } else {
    // Armed, connected, idle — double blink (ready)
    int phase = (now / 200) % 6;
    digitalWrite(STATUS_LED_PIN, (phase == 0 || phase == 2) ? HIGH : LOW);
  }
}

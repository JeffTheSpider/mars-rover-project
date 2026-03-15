// ============================================================
// Mars Rover — Phase 1 Firmware
// ESP32-S3 DevKitC-1 (N16R8)
// Version: 0.1.0
//
// Phase 1: 0.4 scale prototype
// - 4-channel motor control (L298N, 6 motors as 4 groups)
// - 4 SG90 steering servos (Ackermann + point turn + crab)
// - WiFi web server + WebSocket for phone control
// - Battery monitoring (ADC)
// - 2 wheel encoders (optional)
// - E-stop button
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
#include "rover_webserver.h"

// --- Timing ---
unsigned long lastMotorUpdate = 0;
unsigned long lastSensorUpdate = 0;
unsigned long lastBattUpdate = 0;
unsigned long lastCommandTime = 0;

// --- State ---
bool estopActive = false;
bool wifiConnected = false;

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

  // Handle WiFi reconnection
  if (WiFi.status() != WL_CONNECTED) {
    if (wifiConnected) {
      Serial.println("[WIFI] Disconnected — attempting reconnect");
      wifiConnected = false;
      stopAllMotors();
    }
    connectWiFi();
  }

  // Handle web server + WebSocket
  handleWeb();

  // Check E-stop
  if (isEStopPressed() && !estopActive) {
    estopActive = true;
    stopAllMotors();
    Serial.println("[ESTOP] Activated — all motors stopped");
  } else if (!isEStopPressed() && estopActive) {
    estopActive = false;
    Serial.println("[ESTOP] Released — ready to drive");
  }

  // Motor speed ramping (50 Hz)
  if (now - lastMotorUpdate >= MOTOR_UPDATE_MS) {
    if (!estopActive && !batteryCritical) {
      updateMotors();
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

  // Command timeout: stop motors if no command for 2 seconds
  // (WebSocket disconnect already stops, but this catches other cases)
  if (now - lastCommandTime > 2000 && (motorTarget[0] != 0 || motorTarget[2] != 0)) {
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

void updateStatusLED(unsigned long now) {
  if (estopActive) {
    // Fast blink red (using built-in LED, on/off)
    digitalWrite(STATUS_LED_PIN, (now / 200) % 2);
  } else if (batteryCritical) {
    // Very fast blink
    digitalWrite(STATUS_LED_PIN, (now / 100) % 2);
  } else if (batteryWarning) {
    // Slow blink
    digitalWrite(STATUS_LED_PIN, (now / 1000) % 2);
  } else if (wifiConnected) {
    // Solid on
    digitalWrite(STATUS_LED_PIN, HIGH);
  } else {
    // Double blink (WiFi connecting)
    int phase = (now / 150) % 6;
    digitalWrite(STATUS_LED_PIN, (phase == 0 || phase == 2) ? HIGH : LOW);
  }
}

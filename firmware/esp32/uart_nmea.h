#ifndef UART_NMEA_H
#define UART_NMEA_H

// ============================================================
// NMEA Text UART Protocol Handler (EA-12)
// Phase 1: Debug/development protocol over USB Serial or UART1
// Phase 2: Replaced by binary COBS protocol (EA-18, uart_binary.h)
//
// Format: $CMD,data1,data2,...*XOR\n
// ============================================================

#ifndef PHASE2_BINARY_PROTOCOL  // Only compile for Phase 1

// Forward declarations from other modules
extern bool estopActive;
extern bool batteryCritical;
extern int8_t motorTarget[];
extern float batteryVoltage;
extern uint8_t batteryPercent;
extern unsigned long lastCommandTime;
void stopAllMotors();
void setDrive(int8_t leftSpeed, int8_t rightSpeed);
void setServoAngle(uint8_t idx, float angleDeg);
void applyAckermann(float turnRadiusMM);
void applyPointTurn(float rotSpeed);
void applyCrabWalk(float angleDeg);
void applyStraight();
void getAndResetEncoders(int32_t* w1, int32_t* w6);

// --- Configuration ---
#define UART_BAUD        115200
#define UART_RX_BUF_SIZE 256
#define UART_TX_BUF_SIZE 256
#define UART_WATCHDOG_MS 2000   // Stop motors if no command for 2s

// Use Serial1 for Jetson UART (GPIO43 TX, GPIO44 RX per EA-09)
// Use Serial for USB debug
#define UART_PORT Serial1
#define UART_TX_PIN 43
#define UART_RX_PIN 44

// --- State ---
char uartRxBuf[UART_RX_BUF_SIZE];
uint16_t uartRxIdx = 0;
bool uartRxInMsg = false;
unsigned long lastUartRxTime = 0;
uint8_t uartTxSeq = 0;

// --- Checksum ---

uint8_t nmeaChecksum(const char* msg) {
  // XOR of all bytes between $ and * (exclusive)
  uint8_t xor_val = 0;
  for (int i = 1; msg[i] != '*' && msg[i] != '\0'; i++) {
    xor_val ^= (uint8_t)msg[i];
  }
  return xor_val;
}

bool verifyChecksum(const char* msg) {
  // Find the * delimiter
  const char* star = strchr(msg, '*');
  if (!star || star == msg) return false;

  // Parse the 2-char hex checksum after *
  char hexStr[3] = {star[1], star[2], '\0'};
  uint8_t expected = (uint8_t)strtol(hexStr, NULL, 16);

  return nmeaChecksum(msg) == expected;
}

// --- Transmit ---

void nmeaSend(const char* body) {
  // body should be like "ENC,1234,5678,..." (without $ and *XX)
  char msg[UART_TX_BUF_SIZE];
  snprintf(msg, sizeof(msg), "$%s*00", body);

  // Calculate and insert checksum
  uint8_t cs = nmeaChecksum(msg);
  char* star = strchr(msg, '*');
  if (star) {
    snprintf(star + 1, 3, "%02X", cs);
  }

  UART_PORT.println(msg);
}

void sendEncoderReport() {
  int32_t w1, w6;
  getAndResetEncoders(&w1, &w6);

  char body[64];
  // Phase 1 only has 2 encoders, report 0 for unused wheels
  snprintf(body, sizeof(body), "ENC,%ld,0,0,0,0,%ld", (long)w1, (long)w6);
  nmeaSend(body);
}

void sendIMUReport() {
  // Phase 1: no IMU connected, send zeroes
  // Phase 2: read BNO055 quaternion + accel
  nmeaSend("IMU,1.000,0.000,0.000,0.000,0.00,0.00,9.81");
}

void sendBatteryReport() {
  char body[48];
  snprintf(body, sizeof(body), "BAT,%.2f,0.00,%d",
    batteryVoltage, batteryPercent);
  nmeaSend(body);
}

void sendStatusReport() {
  uint8_t state = 1; // 0=boot, 1=ok, 2=estop, 3=error
  if (estopActive) state = 2;
  if (batteryCritical) state = 3;

  char body[48];
  snprintf(body, sizeof(body), "STS,%d,%lu,%d",
    state, millis() / 1000, 0);  // temp=0 (no sensor in Phase 1)
  nmeaSend(body);
}

void sendPong() {
  nmeaSend("PON");
}

void sendAck(const char* cmd) {
  char body[16];
  snprintf(body, sizeof(body), "ACK,%s", cmd);
  nmeaSend(body);
}

void sendError(uint8_t code, const char* msg) {
  char body[64];
  snprintf(body, sizeof(body), "ERR,%d,%s", code, msg);
  nmeaSend(body);
}

// --- Command Parsing ---

void parseNMEACommand(const char* msg) {
  if (!verifyChecksum(msg)) {
    sendError(1, "checksum_mismatch");
    return;
  }

  lastUartRxTime = millis();

  // Extract command ID (3 chars after $)
  char cmd[4] = {0};
  strncpy(cmd, msg + 1, 3);

  // Find first comma (start of data)
  const char* data = strchr(msg + 1, ',');

  if (strcmp(cmd, "MOT") == 0 && data) {
    // $MOT,w1,w2,w3,w4,w5,w6*XX
    // Phase 1: 4 motor groups (LF, LR, RF, RR)
    lastCommandTime = millis();
    int w1, w2, w3, w4, w5, w6;
    if (sscanf(data, ",%d,%d,%d,%d,%d,%d", &w1, &w2, &w3, &w4, &w5, &w6) >= 4) {
      if (!estopActive && !batteryCritical) {
        // Map 6 wheels to 4 motor groups
        setDrive((int8_t)constrain(w1, -100, 100),
                 (int8_t)constrain(w4, -100, 100));
      }
      sendAck("MOT");
    }

  } else if (strcmp(cmd, "STR") == 0 && data) {
    // $STR,fl,fr,rl,rr*XX
    lastCommandTime = millis();
    float fl, fr, rl, rr;
    if (sscanf(data, ",%f,%f,%f,%f", &fl, &fr, &rl, &rr) == 4) {
      setServoAngle(0, fl);
      setServoAngle(1, fr);
      setServoAngle(2, rl);
      setServoAngle(3, rr);
      sendAck("STR");
    }

  } else if (strcmp(cmd, "STP") == 0) {
    // $STP*XX — Emergency stop
    estopActive = true;
    stopAllMotors();
    sendAck("STP");
    Serial.println("[UART] E-stop received from Jetson");

  } else if (strcmp(cmd, "RSM") == 0) {
    // $RSM*XX — Resume from E-stop
    estopActive = false;
    sendAck("RSM");
    Serial.println("[UART] Resume received from Jetson");

  } else if (strcmp(cmd, "REQ") == 0 && data) {
    // $REQ,type*XX — Request sensor data
    char type[4] = {0};
    sscanf(data, ",%3s", type);

    if (strcmp(type, "ALL") == 0) {
      sendEncoderReport();
      sendIMUReport();
      sendBatteryReport();
      sendStatusReport();
    } else if (strcmp(type, "ENC") == 0) {
      sendEncoderReport();
    } else if (strcmp(type, "IMU") == 0) {
      sendIMUReport();
    } else if (strcmp(type, "BAT") == 0) {
      sendBatteryReport();
    } else if (strcmp(type, "STS") == 0) {
      sendStatusReport();
    }

  } else if (strcmp(cmd, "MOD") == 0 && data) {
    // $MOD,mode,param*XX — Steering mode
    int mode;
    float param;
    if (sscanf(data, ",%d,%f", &mode, &param) >= 1) {
      switch (mode) {
        case 0: applyAckermann(param); break;
        case 1: applyPointTurn((float)param); break;
        case 2: applyCrabWalk(param); break;
        case 3: applyStraight(); break;
      }
      sendAck("MOD");
    }

  } else if (strcmp(cmd, "PNG") == 0) {
    // $PNG*XX — Ping
    sendPong();

  } else if (strcmp(cmd, "LED") == 0) {
    // $LED,mode,r,g,b*XX — LED control (Phase 1: status LED only)
    sendAck("LED");

  } else if (strcmp(cmd, "BUZ") == 0) {
    // $BUZ,freq,duration*XX — Buzzer (Phase 1: no buzzer)
    sendAck("BUZ");

  } else {
    sendError(2, "unknown_command");
  }
}

// --- Non-blocking Receive ---

void uartReceive() {
  while (UART_PORT.available()) {
    char c = UART_PORT.read();

    if (c == '$') {
      // Start of new message
      uartRxIdx = 0;
      uartRxInMsg = true;
      uartRxBuf[uartRxIdx++] = c;

    } else if (c == '\n' && uartRxInMsg) {
      // End of message
      uartRxBuf[uartRxIdx] = '\0';
      uartRxInMsg = false;
      parseNMEACommand(uartRxBuf);
      uartRxIdx = 0;

    } else if (uartRxInMsg) {
      if (uartRxIdx < UART_RX_BUF_SIZE - 1) {
        uartRxBuf[uartRxIdx++] = c;
      } else {
        // Buffer overflow — discard
        uartRxInMsg = false;
        uartRxIdx = 0;
        sendError(2, "rx_overflow");
      }
    }
  }

  // Watchdog: stop motors if no UART command received recently
  if (lastUartRxTime > 0 && millis() - lastUartRxTime > UART_WATCHDOG_MS) {
    if (motorTarget[0] != 0 || motorTarget[2] != 0) {
      stopAllMotors();
      sendError(8, "watchdog_timeout");
      Serial.println("[UART] Watchdog timeout — motors stopped");
    }
    lastUartRxTime = millis(); // Reset to avoid spamming
  }
}

// --- Periodic Telemetry ---

unsigned long lastEncTx = 0;
unsigned long lastBatTx = 0;
unsigned long lastStsTx = 0;

void uartTelemetry() {
  unsigned long now = millis();

  // Encoder data at 50 Hz (every 20ms)
  if (now - lastEncTx >= 20) {
    sendEncoderReport();
    lastEncTx = now;
  }

  // Battery at 1 Hz
  if (now - lastBatTx >= 1000) {
    sendBatteryReport();
    lastBatTx = now;
  }

  // Status at 1 Hz (offset 500ms from battery)
  if (now - lastStsTx >= 1000 && now - lastBatTx >= 500) {
    sendStatusReport();
    lastStsTx = now;
  }
}

// --- Setup ---

void setupUartNMEA() {
  UART_PORT.begin(UART_BAUD, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);

  Serial.printf("[UART] NMEA protocol on UART1 at %d baud (TX=%d, RX=%d)\n",
    UART_BAUD, UART_TX_PIN, UART_RX_PIN);
}

// --- Main handler (call from loop) ---

void handleUartNMEA() {
  uartReceive();
  uartTelemetry();
}

#endif // !PHASE2_BINARY_PROTOCOL

#endif // UART_NMEA_H

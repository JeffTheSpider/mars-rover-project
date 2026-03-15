#ifndef UART_BINARY_H
#define UART_BINARY_H

// ============================================================
// Mars Rover — Phase 2 Binary UART Protocol (EA-18)
// COBS-framed, CRC-16/CCITT, integer-only encoding
// ESP32-S3 ↔ Jetson Orin Nano over UART1 (GPIO43 TX, GPIO44 RX)
//
// Enable with: #define PHASE2_BINARY_PROTOCOL
// ============================================================

#ifdef PHASE2_BINARY_PROTOCOL

#include <Arduino.h>
#include <cstring>

// --- UART1 Pin Assignments (EA-09) ---
#define UART1_TX_PIN  43
#define UART1_RX_PIN  44
#define UART1_BAUD    460800

// --- Protocol Constants ---
#define BIN_MAX_PAYLOAD     250
#define BIN_MAX_FRAME       255   // header(3) + payload(250) + crc(2)
#define BIN_COBS_OVERHEAD   3     // worst case COBS overhead for 255 bytes
#define BIN_MAX_ENCODED     (BIN_MAX_FRAME + BIN_COBS_OVERHEAD + 2) // + delimiters
#define BIN_RX_RING_SIZE    512
#define BIN_FRAME_DELIMITER 0x00

// --- Message IDs: Jetson -> ESP32 Commands (0x01-0x7F) ---
static constexpr uint8_t MSG_MOTOR_CMD     = 0x01;
static constexpr uint8_t MSG_SERVO_CMD     = 0x02;
static constexpr uint8_t MSG_LED_CMD       = 0x03;
static constexpr uint8_t MSG_BUZZER_CMD    = 0x04;
static constexpr uint8_t MSG_SENSOR_REQ    = 0x05;
static constexpr uint8_t MSG_E_STOP        = 0x0E;
static constexpr uint8_t MSG_HEARTBEAT_CMD = 0x0F;

// --- Message IDs: ESP32 -> Jetson Telemetry (0x80-0xFF) ---
static constexpr uint8_t MSG_ENCODER_DATA  = 0x81;
static constexpr uint8_t MSG_IMU_DATA      = 0x82;
static constexpr uint8_t MSG_BATTERY_DATA  = 0x83;
static constexpr uint8_t MSG_STATUS        = 0x84;
static constexpr uint8_t MSG_ACK           = 0x85;
static constexpr uint8_t MSG_ERROR_RSP     = 0x8E;
static constexpr uint8_t MSG_HEARTBEAT_RSP = 0x8F;

// --- ACK Result Codes ---
static constexpr uint8_t ACK_OK             = 0x00;
static constexpr uint8_t ACK_INVALID_PARAM  = 0x01;
static constexpr uint8_t ACK_BUSY           = 0x02;
static constexpr uint8_t ACK_NOT_SUPPORTED  = 0x03;

// --- System States ---
static constexpr uint8_t STATE_BOOT     = 0;
static constexpr uint8_t STATE_OK       = 1;
static constexpr uint8_t STATE_ESTOP    = 2;
static constexpr uint8_t STATE_ERROR    = 3;
static constexpr uint8_t STATE_LOW_BATT = 4;

// --- Error Flags (bitmask) ---
static constexpr uint8_t ERR_MOTOR_FAULT    = 0x01;
static constexpr uint8_t ERR_IMU_FAULT      = 0x02;
static constexpr uint8_t ERR_ENCODER_FAULT  = 0x04;
static constexpr uint8_t ERR_SERVO_FAULT    = 0x08;
static constexpr uint8_t ERR_BATTERY_CRIT   = 0x10;

// ============================================================
// Packed Message Structs
// ============================================================

// --- Commands (Jetson -> ESP32) ---

struct __attribute__((packed)) MotorCmd {
  int16_t wheels[6];    // FL, FR, ML, MR, RL, RR — range -1000 to +1000
};

struct __attribute__((packed)) ServoCmd {
  uint16_t angles[4];   // FL, FR, RL, RR — range 0-1800 (0.1 degree)
};

struct __attribute__((packed)) LedCmd {
  uint8_t mode;          // 0=off, 1=solid, 2=blink, 3=chase
  uint8_t r, g, b;
  uint8_t brightness;    // 0-255
};

struct __attribute__((packed)) BuzzerCmd {
  uint16_t freq_hz;
  uint16_t duration_ms;
  uint8_t  pattern;      // 0=single, 1=double, 2=triple, 3=continuous
};

// --- Telemetry (ESP32 -> Jetson) ---

struct __attribute__((packed)) EncoderData {
  int32_t ticks[6];      // Cumulative encoder counts
};

struct __attribute__((packed)) ImuData {
  int16_t quat[4];       // w,x,y,z — raw BNO055 (÷16384 for unit quat)
  int16_t accel[3];      // x,y,z in milli-g
  int16_t gyro[3];       // x,y,z in 0.1 deg/s
};

struct __attribute__((packed)) BatteryData {
  uint16_t voltage_mv;
  uint16_t current_ma;
  uint8_t  percent;      // 0-100
};

struct __attribute__((packed)) StatusData {
  uint8_t  state;        // STATE_BOOT..STATE_LOW_BATT
  uint8_t  error_flags;  // ERR_* bitmask
  uint16_t loop_time_us;
  uint8_t  cpu_temp;     // Celsius
};

struct __attribute__((packed)) AckData {
  uint8_t acked_msg_id;
  uint8_t acked_seq;
  uint8_t result_code;   // ACK_OK..ACK_NOT_SUPPORTED
};

struct __attribute__((packed)) ErrorData {
  uint8_t  error_code;
  uint8_t  severity;     // 0=info, 1=warning, 2=critical
  uint16_t detail;
};

struct __attribute__((packed)) HeartbeatRsp {
  uint8_t system_state;
  uint8_t fw_major;
  uint8_t fw_minor;
};

// ============================================================
// CRC-16/CCITT-FALSE Lookup Table
// Polynomial: 0x1021, Init: 0xFFFF
// ============================================================

static const uint16_t crc16_table[256] = {
  0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
  0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
  0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6,
  0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
  0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485,
  0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
  0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4,
  0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
  0x4864, 0x5845, 0x6826, 0x7807, 0x08E0, 0x18C1, 0x28A2, 0x38A3,
  0xC94C, 0xD96D, 0xE90E, 0xF92F, 0x89C8, 0x99E9, 0xA98A, 0xB9AB,
  0x5A75, 0x4A54, 0x7A37, 0x6A16, 0x1AF1, 0x0AD0, 0x3AB3, 0x2A92,
  0xDB7D, 0xCB5C, 0xFB3F, 0xEB1E, 0x9BF9, 0x8BD8, 0xBBBB, 0xAB9A,
  0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41,
  0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
  0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70,
  0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
  0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F,
  0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
  0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E,
  0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
  0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D,
  0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
  0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C,
  0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
  0xD9EC, 0xC9CD, 0xF9AE, 0xE98F, 0x9968, 0x8949, 0xB92A, 0xA90B,
  0x58E4, 0x48C5, 0x78A6, 0x6887, 0x1860, 0x0841, 0x3822, 0x2803,
  0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBBAA,
  0x4A45, 0x5A64, 0x6A07, 0x7A26, 0x0AC1, 0x1AE0, 0x2A83, 0x3AA2,
  0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9,
  0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
  0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8,
  0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0
};

// ============================================================
// CRC-16/CCITT Calculation
// ============================================================

uint16_t binaryCrc16(const uint8_t* data, size_t length) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < length; i++) {
    uint8_t idx = (uint8_t)((crc >> 8) ^ data[i]);
    crc = (crc << 8) ^ crc16_table[idx];
  }
  return crc;
}

// ============================================================
// COBS Encoding
// Returns encoded length. Output must be >= (length + length/254 + 1).
// ============================================================

size_t cobsEncode(const uint8_t* input, size_t length, uint8_t* output) {
  size_t readIdx = 0, writeIdx = 1, codeIdx = 0;
  uint8_t code = 1;

  while (readIdx < length) {
    if (input[readIdx] == 0x00) {
      output[codeIdx] = code;
      code = 1;
      codeIdx = writeIdx++;
    } else {
      output[writeIdx++] = input[readIdx];
      if (++code == 0xFF) {
        output[codeIdx] = code;
        code = 1;
        codeIdx = writeIdx++;
      }
    }
    readIdx++;
  }
  output[codeIdx] = code;
  return writeIdx;
}

// ============================================================
// COBS Decoding
// Returns decoded length, or 0 on error.
// ============================================================

size_t cobsDecode(const uint8_t* input, size_t length, uint8_t* output) {
  size_t readIdx = 0, writeIdx = 0;
  bool lastGroupAddedZero = false;

  while (readIdx < length) {
    uint8_t code = input[readIdx++];
    if (code == 0) return 0; // Invalid COBS encoding

    for (uint8_t i = 1; i < code; i++) {
      if (readIdx >= length) return 0; // Truncated frame
      output[writeIdx++] = input[readIdx++];
    }
    if (code < 0xFF && readIdx < length) {
      output[writeIdx++] = 0x00;
      lastGroupAddedZero = true;
    } else {
      lastGroupAddedZero = false;
    }
  }

  // Remove trailing implicit zero only if the last group boundary added one
  if (lastGroupAddedZero && writeIdx > 0) {
    writeIdx--;
  }
  return writeIdx;
}

// ============================================================
// Ring Buffer for Non-Blocking Receive
// ============================================================

static uint8_t  binRxRing[BIN_RX_RING_SIZE];
static uint16_t binRxHead = 0;  // Write position
static uint16_t binRxTail = 0;  // Read position

static inline uint16_t ringAvailable() {
  return (uint16_t)((binRxHead - binRxTail) & (BIN_RX_RING_SIZE - 1));
}

static inline bool ringPush(uint8_t b) {
  uint16_t next = (binRxHead + 1) & (BIN_RX_RING_SIZE - 1);
  if (next == binRxTail) return false; // Full
  binRxRing[binRxHead] = b;
  binRxHead = next;
  return true;
}

static inline bool ringPop(uint8_t* b) {
  if (binRxHead == binRxTail) return false; // Empty
  *b = binRxRing[binRxTail];
  binRxTail = (binRxTail + 1) & (BIN_RX_RING_SIZE - 1);
  return true;
}

// ============================================================
// Protocol State
// ============================================================

static uint8_t  binTxSeq = 0;
static int16_t  binLastRxSeq = -1;
static uint32_t binErrCount = 0;
static uint32_t binDropCount = 0;
static uint32_t binRxMsgCount = 0;
static uint32_t binTxMsgCount = 0;

// Frame accumulation buffer (between 0x00 delimiters)
static uint8_t  binFrameBuf[BIN_MAX_ENCODED];
static size_t   binFrameLen = 0;
static bool     binFrameStarted = false;

// Debug flag — set true to print decoded messages on USB serial
static bool binDebugEnabled = false;

// ============================================================
// Message Callback Type
// Called when a valid message is received and CRC verified.
// Parameters: msg_id, sequence, pointer to data, data length
// ============================================================

typedef void (*BinaryMsgCallback)(uint8_t msgId, uint8_t seq,
                                   const uint8_t* data, uint8_t len);

static BinaryMsgCallback binMsgCallback = nullptr;

// ============================================================
// Process a Complete Frame (COBS-encoded bytes between delimiters)
// ============================================================

static void binProcessFrame(const uint8_t* cobsData, size_t cobsLen) {
  if (cobsLen == 0) return;

  // Decode COBS
  uint8_t decoded[BIN_MAX_FRAME];
  size_t decLen = cobsDecode(cobsData, cobsLen, decoded);

  // Minimum frame: msg_id(1) + seq(1) + length(1) + crc(2) = 5
  if (decLen < 5) {
    binErrCount++;
    if (binDebugEnabled) {
      Serial.printf("[BIN-RX] Frame too short: %d bytes\n", (int)decLen);
    }
    return;
  }

  uint8_t msgId   = decoded[0];
  uint8_t seq     = decoded[1];
  uint8_t dataLen = decoded[2];

  // Verify length consistency
  if ((size_t)(dataLen + 5) != decLen) {
    binErrCount++;
    if (binDebugEnabled) {
      Serial.printf("[BIN-RX] Length mismatch: hdr=%d dec=%d\n", dataLen + 5, (int)decLen);
    }
    return;
  }

  // Verify data length limit
  if (dataLen > BIN_MAX_PAYLOAD) {
    binErrCount++;
    if (binDebugEnabled) {
      Serial.printf("[BIN-RX] Payload too large: %d\n", dataLen);
    }
    return;
  }

  // CRC check: computed over everything except the last 2 bytes
  uint16_t rxCrc = ((uint16_t)decoded[decLen - 2] << 8) | decoded[decLen - 1];
  uint16_t calcCrc = binaryCrc16(decoded, decLen - 2);

  if (rxCrc != calcCrc) {
    binErrCount++;
    if (binDebugEnabled) {
      Serial.printf("[BIN-RX] CRC fail: rx=0x%04X calc=0x%04X\n", rxCrc, calcCrc);
    }
    return;
  }

  // Track sequence number gaps
  if (binLastRxSeq >= 0 && seq != (uint8_t)(binLastRxSeq + 1)) {
    binDropCount++;
    if (binDebugEnabled) {
      uint8_t expected = (uint8_t)(binLastRxSeq + 1);
      Serial.printf("[BIN-RX] Seq gap: expected=%d got=%d\n", expected, seq);
    }
  }
  binLastRxSeq = seq;
  binRxMsgCount++;

  if (binDebugEnabled) {
    Serial.printf("[BIN-RX] ID=0x%02X SEQ=%d LEN=%d\n", msgId, seq, dataLen);
  }

  // Dispatch to callback
  if (binMsgCallback) {
    binMsgCallback(msgId, seq, &decoded[3], dataLen);
  }
}

// ============================================================
// Transmit a Binary Message
// Builds: [msg_id][seq][length][data][crc16] -> COBS encode -> [0x00][encoded][0x00]
// ============================================================

bool binaryTx(uint8_t msgId, const void* data, size_t len) {
  if (len > BIN_MAX_PAYLOAD) return false;

  // Build raw frame: header(3) + data + crc(2)
  uint8_t raw[BIN_MAX_FRAME];
  raw[0] = msgId;
  raw[1] = binTxSeq++;  // Wraps at 255 automatically (uint8_t)
  raw[2] = (uint8_t)len;

  if (len > 0 && data != nullptr) {
    memcpy(&raw[3], data, len);
  }

  size_t rawLen = 3 + len;

  // Calculate CRC over header + data
  uint16_t crc = binaryCrc16(raw, rawLen);
  raw[rawLen]     = (uint8_t)(crc >> 8);   // CRC high byte
  raw[rawLen + 1] = (uint8_t)(crc & 0xFF); // CRC low byte
  rawLen += 2;

  // COBS encode
  uint8_t encoded[BIN_MAX_ENCODED];
  size_t encLen = cobsEncode(raw, rawLen, encoded);

  // Write frame with 0x00 delimiters
  Serial1.write((uint8_t)BIN_FRAME_DELIMITER);
  Serial1.write(encoded, encLen);
  Serial1.write((uint8_t)BIN_FRAME_DELIMITER);

  binTxMsgCount++;

  if (binDebugEnabled) {
    Serial.printf("[BIN-TX] ID=0x%02X SEQ=%d LEN=%d\n", msgId, raw[1], (int)len);
  }

  return true;
}

// ============================================================
// Typed Transmit Helpers
// ============================================================

bool binaryTxEncoder(const EncoderData& enc) {
  return binaryTx(MSG_ENCODER_DATA, &enc, sizeof(enc));
}

bool binaryTxImu(const ImuData& imu) {
  return binaryTx(MSG_IMU_DATA, &imu, sizeof(imu));
}

bool binaryTxBattery(const BatteryData& batt) {
  return binaryTx(MSG_BATTERY_DATA, &batt, sizeof(batt));
}

bool binaryTxStatus(const StatusData& status) {
  return binaryTx(MSG_STATUS, &status, sizeof(status));
}

bool binaryTxAck(uint8_t ackedMsgId, uint8_t ackedSeq, uint8_t result) {
  AckData ack;
  ack.acked_msg_id = ackedMsgId;
  ack.acked_seq = ackedSeq;
  ack.result_code = result;
  return binaryTx(MSG_ACK, &ack, sizeof(ack));
}

bool binaryTxError(uint8_t errorCode, uint8_t severity, uint16_t detail) {
  ErrorData err;
  err.error_code = errorCode;
  err.severity = severity;
  err.detail = detail;
  return binaryTx(MSG_ERROR_RSP, &err, sizeof(err));
}

bool binaryTxHeartbeat(uint8_t state, uint8_t fwMajor, uint8_t fwMinor) {
  HeartbeatRsp hb;
  hb.system_state = state;
  hb.fw_major = fwMajor;
  hb.fw_minor = fwMinor;
  return binaryTx(MSG_HEARTBEAT_RSP, &hb, sizeof(hb));
}

// ============================================================
// Non-Blocking Receive (call from loop())
// Reads available bytes from Serial1 into ring buffer,
// then extracts complete frames delimited by 0x00.
// ============================================================

void binaryRxUpdate() {
  // Drain Serial1 hardware buffer into ring buffer
  while (Serial1.available()) {
    int b = Serial1.read();
    if (b < 0) break;
    ringPush((uint8_t)b);
  }

  // Process ring buffer: extract bytes, accumulate frames
  uint8_t byte;
  while (ringPop(&byte)) {
    if (byte == BIN_FRAME_DELIMITER) {
      // Delimiter found — process accumulated frame if any
      if (binFrameLen > 0) {
        binProcessFrame(binFrameBuf, binFrameLen);
        binFrameLen = 0;
      }
      binFrameStarted = true;
    } else {
      if (binFrameStarted) {
        if (binFrameLen < sizeof(binFrameBuf)) {
          binFrameBuf[binFrameLen++] = byte;
        } else {
          // Frame too large — discard and wait for next delimiter
          binFrameLen = 0;
          binFrameStarted = false;
          binErrCount++;
          if (binDebugEnabled) {
            Serial.println("[BIN-RX] Frame overflow — discarded");
          }
        }
      }
      // else: bytes before first delimiter are discarded (sync)
    }
  }
}

// ============================================================
// Initialisation
// ============================================================

void setupBinaryUart(BinaryMsgCallback callback) {
  binMsgCallback = callback;

  // Reset state
  binTxSeq = 0;
  binLastRxSeq = -1;
  binErrCount = 0;
  binDropCount = 0;
  binRxMsgCount = 0;
  binTxMsgCount = 0;
  binFrameLen = 0;
  binFrameStarted = false;
  binRxHead = 0;
  binRxTail = 0;

  // Initialise UART1 on GPIO43(TX)/GPIO44(RX) at 460800 baud
  Serial1.begin(UART1_BAUD, SERIAL_8N1, UART1_RX_PIN, UART1_TX_PIN);
  Serial1.setRxBufferSize(BIN_RX_RING_SIZE);

  Serial.printf("[BIN] Binary UART protocol initialised at %d baud\n", UART1_BAUD);
  Serial.printf("[BIN] TX=GPIO%d RX=GPIO%d\n", UART1_TX_PIN, UART1_RX_PIN);
}

// ============================================================
// Diagnostics (for debug / status reporting)
// ============================================================

uint32_t binaryGetErrorCount()   { return binErrCount; }
uint32_t binaryGetDropCount()    { return binDropCount; }
uint32_t binaryGetRxMsgCount()   { return binRxMsgCount; }
uint32_t binaryGetTxMsgCount()   { return binTxMsgCount; }

void binarySetDebug(bool enabled) { binDebugEnabled = enabled; }

void binaryPrintStats() {
  Serial.println("[BIN] --- Protocol Stats ---");
  Serial.printf("[BIN]  TX messages:  %lu\n", (unsigned long)binTxMsgCount);
  Serial.printf("[BIN]  RX messages:  %lu\n", (unsigned long)binRxMsgCount);
  Serial.printf("[BIN]  CRC/framing errors: %lu\n", (unsigned long)binErrCount);
  Serial.printf("[BIN]  Sequence drops: %lu\n", (unsigned long)binDropCount);
}

#endif // PHASE2_BINARY_PROTOCOL
#endif // UART_BINARY_H

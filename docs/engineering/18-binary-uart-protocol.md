# Engineering Analysis 18: Binary UART Protocol (Phase 2 Upgrade)

**Document**: EA-18
**Date**: 2026-03-15
**Purpose**: Upgrade the Phase 2 Jetson↔ESP32 serial protocol from text-based NMEA (EA-12) to binary COBS-framed with CRC-16 for improved reliability, bandwidth, and latency.
**Depends on**: EA-12 (original protocol), EA-04 (Compute), EA-09 (GPIO Pin Map), EA-10 (Ackermann Steering)
**Supersedes**: EA-12 sections 2-7 for Phase 2 use. EA-12 remains the Phase 1 reference (WiFi/WebSocket control, no UART).

---

## 1. Why Upgrade from Text-Based NMEA?

EA-12 specified a text-based NMEA protocol at 115200 baud. While excellent for Phase 1 debugging and prototyping, the research analysis identified several concerns for Phase 2 real-time control:

| Issue | EA-12 (NMEA Text) | EA-18 (Binary COBS) |
|-------|-------------------|---------------------|
| Bandwidth utilisation | **72%** at 115200 | **12%** at 460800 |
| Checksum strength | XOR (8-bit) — misses all even-count bit flips | CRC-16/CCITT — catches all 1-2 bit errors, bursts up to 16 bits |
| Message size (motor cmd) | ~35 bytes | ~18 bytes (COBS-encoded) |
| Round-trip latency | ~7.7ms | ~1.1ms |
| Parsing overhead | `atoi`/`strtol` string parsing | Direct struct cast, zero string ops |
| Float on ESP32 | IMU sends `"0.998,0.012,..."` (float→string→float) | Raw int16 scaled values, no float on ESP32 |
| Sync recovery | Scan for `$` character | Instant: next `0x00` byte = frame boundary |

**Decision**: Use NMEA text (EA-12) for Phase 1 development and serial monitor debugging. Switch to binary COBS (EA-18) for Phase 2 when the Jetson is connected and real-time performance matters.

The Phase 1 firmware is structured so the motor/sensor core is protocol-agnostic — only the input/output layer changes between phases.

---

## 2. Physical Layer Changes

| Parameter | EA-12 Value | EA-18 Value | Rationale |
|-----------|-------------|-------------|-----------|
| Baud rate | 115200 | **460800** | 12% utilisation leaves massive headroom |
| Data bits | 8 | 8 | Unchanged |
| Parity | None | None | CRC-16 handles error detection |
| Stop bits | 1 | 1 | Unchanged |
| Flow control | None | None | 12% utilisation = no overflow risk |
| Wire | 3-wire (TX, RX, GND) | 3-wire | Unchanged |

### 2.1 Baud Rate Comparison

| Baud Rate | Raw Bytes/s | Usable (~80%) | 50B Round-trip | Notes |
|-----------|-------------|---------------|----------------|-------|
| 115200 | 11,520 | 9,216 | ~8.7ms | Tight for 50Hz bidirectional |
| 230400 | 23,040 | 18,432 | ~4.3ms | Comfortable margin |
| **460800** | **46,080** | **36,864** | **~2.2ms** | **Good margin, widely supported** |
| 921600 | 92,160 | 73,728 | ~1.1ms | Overkill, higher error rate on long wires |

460800 is natively supported by both the Jetson Orin Nano (Linux ttyTHS1) and ESP32-S3 (hardware UART). At 30cm wire length inside the rover body, signal integrity is not a concern.

---

## 3. Framing: COBS (Consistent Overhead Byte Stuffing)

### 3.1 Why COBS?

COBS encodes messages so that `0x00` never appears in the payload. This allows `0x00` to serve as an unambiguous frame delimiter.

**Key properties:**
- **Overhead**: 1 byte per 254 payload bytes (~0.4%) — negligible
- **Framing**: `0x00` delimiters at start and end of every frame
- **Sync recovery**: To resync after corruption, discard bytes until `0x00`. Worst case at 460800 baud: ~5.5ms for a max-length frame
- **No ambiguity**: Unlike text protocols where `$` could appear in data, `0x00` is guaranteed absent from COBS-encoded payload

### 3.2 Wire Format

```
[0x00] [COBS-encoded payload] [0x00]
```

The payload (before COBS encoding) has this structure:

```
| Byte 0    | Byte 1    | Byte 2    | Bytes 3..N  | Byte N+1  | Byte N+2  |
|-----------|-----------|-----------|-------------|-----------|-----------|
| MSG_ID    | SEQ       | LENGTH    | DATA        | CRC16_HI  | CRC16_LO  |
```

- **MSG_ID** (1 byte): Message type identifier (0x01-0x7F = commands, 0x80-0xFF = telemetry)
- **SEQ** (1 byte): Sequence number (0-255, wrapping) — detects dropped messages
- **LENGTH** (1 byte): Length of DATA field only (0-250)
- **DATA** (0-250 bytes): Payload specific to MSG_ID
- **CRC16** (2 bytes): CRC-16/CCITT over MSG_ID + SEQ + LENGTH + DATA, big-endian

CRC is computed before COBS encoding. Receiver decodes COBS first, then verifies CRC.

---

## 4. CRC-16/CCITT

### 4.1 Why CRC-16 over XOR?

| Property | XOR (EA-12) | CRC-16/CCITT (EA-18) |
|----------|-------------|----------------------|
| Size | 8 bits | 16 bits |
| Single-bit errors | Detects | Detects |
| Double-bit errors | **Misses** (50% chance) | Detects all |
| Odd-count bit errors | Detects | Detects all |
| Even-count bit errors | **Misses all** | Detects |
| Burst errors | Up to 8 bits | Up to 16 bits |
| Transposed characters | **Misses** | Detects |

For a rover where a corrupted motor command could cause unexpected movement, CRC-16 is the minimum acceptable error detection.

### 4.2 Implementation

Polynomial: `0x1021` (CRC-16/CCITT-FALSE)
Initial value: `0xFFFF`
Lookup table: 256 entries × 2 bytes = 512 bytes of flash (trivial on ESP32-S3's 16MB)

```c
uint16_t crc16(const uint8_t* data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        uint8_t idx = (uint8_t)((crc >> 8) ^ data[i]);
        crc = (crc << 8) ^ crc16_table[idx];
    }
    return crc;
}
```

---

## 5. Integer-Only Encoding (No Float on ESP32)

All values use scaled integers to eliminate floating-point math on the ESP32-S3:

| Value | Encoding | Range | Resolution | Conversion (Jetson side) |
|-------|----------|-------|------------|--------------------------|
| Motor speed | int16_t | -1000 to +1000 | 0.1% | `value / 10.0` for percentage |
| Servo angle | uint16_t | 0 to 1800 | 0.1° | `value / 10.0` for degrees |
| IMU quaternion | int16_t | -16384 to +16384 | 1/16384 | `value / 16384.0` (BNO055 raw) |
| IMU accel | int16_t | -32768 to +32767 | 1 milli-g | `value / 1000.0` for m/s² |
| IMU gyro | int16_t | -32768 to +32767 | 0.1°/s | `value / 10.0` for °/s |
| Battery voltage | uint16_t | 0 to 65535 | 1 mV | `value / 1000.0` for V |
| Battery current | uint16_t | 0 to 65535 | 1 mA | `value / 1000.0` for A |
| Encoder ticks | int32_t | ±2 billion | 1 tick | Direct use |

This approach:
- Eliminates all `float→string→float` conversions from EA-12
- Keeps ESP32 math integer-only (faster, deterministic timing)
- Matches BNO055 raw output format (no conversion needed on ESP32)
- Jetson (ARM Cortex-A78 with FPU) handles the float conversion trivially

---

## 6. Message Catalogue

### 6.1 Jetson → ESP32 Commands (0x01-0x7F)

| MSG_ID | Name | Data Struct | Data Size | Rate |
|--------|------|-------------|-----------|------|
| 0x01 | MOTOR_CMD | 6× int16_t wheel speeds (-1000 to +1000) | 12 | 50 Hz |
| 0x02 | SERVO_CMD | 4× uint16_t servo angles (0-1800 = 0.0-180.0°) | 8 | 50 Hz |
| 0x03 | LED_CMD | uint8_t mode, uint8_t r, uint8_t g, uint8_t b, uint8_t brightness | 5 | On demand |
| 0x04 | BUZZER_CMD | uint16_t freq_hz, uint16_t duration_ms, uint8_t pattern | 5 | On demand |
| 0x05 | SENSOR_REQ | uint8_t sensor_mask (bit flags) | 1 | On demand |
| 0x0E | E_STOP | uint8_t reason_code | 1 | Immediate (3× send) |
| 0x0F | HEARTBEAT_CMD | uint8_t system_state | 1 | 1 Hz |

**Wheel order**: front-left, front-right, mid-left, mid-right, rear-left, rear-right

**Servo order**: front-left, front-right, rear-left, rear-right

**Sensor mask bits**: Bit 0 = Encoders, Bit 1 = IMU, Bit 2 = Battery, Bits 3-7 = Reserved

### 6.2 ESP32 → Jetson Telemetry (0x80-0xFF)

| MSG_ID | Name | Data Struct | Data Size | Rate |
|--------|------|-------------|-----------|------|
| 0x81 | ENCODER_DATA | 6× int32_t cumulative tick counts | 24 | 50 Hz |
| 0x82 | IMU_DATA | 4× int16_t quat + 3× int16_t accel + 3× int16_t gyro | 20 | 50 Hz |
| 0x83 | BATTERY_DATA | uint16_t voltage_mv, uint16_t current_ma, uint8_t percent | 5 | 2 Hz |
| 0x84 | STATUS | uint8_t state, uint8_t error_flags, uint16_t loop_time_us, uint8_t cpu_temp | 5 | 1 Hz |
| 0x85 | ACK | uint8_t acked_msg_id, uint8_t acked_seq, uint8_t result_code | 3 | On demand |
| 0x8E | ERROR | uint8_t error_code, uint8_t severity, uint16_t detail | 4 | On demand |
| 0x8F | HEARTBEAT_RSP | uint8_t system_state, uint8_t fw_major, uint8_t fw_minor | 3 | 1 Hz |

**ACK result codes**: 0x00 = OK, 0x01 = Invalid parameter, 0x02 = Busy, 0x03 = Not supported

**System states**: 0 = Boot, 1 = OK, 2 = E-Stop, 3 = Error, 4 = Low Battery

**Error flags (bitmask)**: Bit 0 = Motor fault, Bit 1 = IMU fault, Bit 2 = Encoder fault, Bit 3 = Servo fault, Bit 4 = Battery critical

### 6.3 Comparison with EA-12 Message Sizes

| Message | EA-12 Text (bytes) | EA-18 Binary (wire bytes) | Savings |
|---------|--------------------|--------------------------| --------|
| Motor command | ~35 | ~18 | 49% |
| Steering command | ~30 | ~14 | 53% |
| Encoder data | ~45 | ~30 | 33% |
| IMU data | ~55 | ~26 | 53% |
| Battery data | ~22 | ~11 | 50% |
| E-Stop | ~8 | ~7 | 13% |

---

## 7. Bandwidth Analysis

### 7.1 Per-Second Traffic

**Jetson → ESP32:**

| Message | Wire Bytes | Messages/s | Bytes/s |
|---------|-----------|------------|---------|
| MOTOR_CMD | ~18 | 50 | 900 |
| SERVO_CMD | ~14 | 50 | 700 |
| HEARTBEAT_CMD | ~7 | 1 | 7 |
| **Subtotal** | | | **~1,607** |

**ESP32 → Jetson:**

| Message | Wire Bytes | Messages/s | Bytes/s |
|---------|-----------|------------|---------|
| ENCODER_DATA | ~30 | 50 | 1,500 |
| IMU_DATA | ~26 | 50 | 1,300 |
| BATTERY_DATA | ~11 | 2 | 22 |
| STATUS | ~11 | 1 | 11 |
| HEARTBEAT_RSP | ~9 | 1 | 9 |
| **Subtotal** | | | **~2,842** |

**Total bidirectional: ~4,449 bytes/s**

### 7.2 Utilisation Comparison

| Metric | EA-12 (115200) | EA-18 (460800) |
|--------|----------------|----------------|
| Total traffic | ~8,310 B/s | ~4,449 B/s |
| Available bandwidth | 11,520 B/s | 46,080 B/s |
| **Utilisation** | **72%** | **12%** |
| Headroom | 3,210 B/s | 41,631 B/s |

EA-18 has **13× more headroom** than EA-12 — ample room for future message types (camera commands, arm control, lidar triggers) without a baud rate change.

### 7.3 Latency Budget

| Component | EA-12 | EA-18 |
|-----------|-------|-------|
| Motor command wire time | 3.0ms | 0.39ms |
| ESP32 parse + execute | 0.5ms | 0.5ms |
| Encoder response wire time | 3.9ms | 0.65ms |
| Jetson parse | 0.1ms | 0.1ms |
| **Total round-trip** | **~7.7ms** | **~1.6ms** |

At 50Hz (20ms cycles), EA-18 leaves 18.4ms idle per cycle vs EA-12's 12.3ms.

---

## 8. Error Recovery

### 8.1 Corrupted Messages

1. COBS decoder encounters invalid encoding → discard bytes until next `0x00` delimiter
2. CRC mismatch after successful COBS decode → discard message, increment error counter
3. LENGTH field exceeds 250 → discard, resync on next `0x00`
4. Unknown MSG_ID → discard, send ERROR response (0x8E)

### 8.2 Lost Messages

| Message Type | Retransmit? | Rationale |
|--------------|-------------|-----------|
| MOTOR_CMD | No | Next command at 50Hz supersedes |
| SERVO_CMD | No | Same as motor |
| Sensor data | No | Stale data worse than no data |
| E_STOP | Yes (3×) | Safety-critical, maximize delivery probability |
| LED/Buzzer | No | Non-critical, user will retry if needed |
| Heartbeat | No | Absence is the signal (watchdog timeout) |

### 8.3 Motor Safety Timeout

If ESP32 receives no valid MOTOR_CMD or HEARTBEAT for **500ms**:
1. Ramp all motors to zero over 200ms (not instant stop — prevents skidding)
2. Set status LED to amber blink
3. Enter safe mode (reject motor commands until heartbeat resumes)
4. Continue sending telemetry (so Jetson knows ESP32 is alive)

If no valid message at all for **2000ms**:
1. Full E-Stop (motors off immediately)
2. Status LED red
3. Wait for heartbeat to resume

### 8.4 Sequence Number Monitoring

The SEQ field wraps 0-255. Both sides track the last received SEQ:
- If `received_seq != (last_seq + 1) % 256`: one or more messages were dropped
- Log the gap count for diagnostics
- For motor/sensor data: no action needed (next message supersedes)
- For E_STOP: the triple-send covers this

---

## 9. COBS Implementation

### 9.1 Encoder

```c
// Returns encoded length. Output buffer must be at least (length + length/254 + 1) bytes.
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
```

### 9.2 Decoder

```c
// Returns decoded length, or 0 on error
size_t cobsDecode(const uint8_t* input, size_t length, uint8_t* output) {
    size_t readIdx = 0, writeIdx = 0;
    while (readIdx < length) {
        uint8_t code = input[readIdx++];
        if (code == 0) return 0; // Invalid COBS
        for (uint8_t i = 1; i < code; i++) {
            if (readIdx >= length) return 0; // Truncated
            output[writeIdx++] = input[readIdx++];
        }
        if (code < 0xFF && readIdx < length) {
            output[writeIdx++] = 0x00;
        }
    }
    // Remove trailing zero if present
    if (writeIdx > 0 && output[writeIdx - 1] == 0x00) writeIdx--;
    return writeIdx;
}
```

---

## 10. Data Structures (C++)

```cpp
#pragma once
#include <cstdint>

// --- Message IDs ---
// Commands (Jetson → ESP32): 0x01-0x7F
constexpr uint8_t MSG_MOTOR_CMD     = 0x01;
constexpr uint8_t MSG_SERVO_CMD     = 0x02;
constexpr uint8_t MSG_LED_CMD       = 0x03;
constexpr uint8_t MSG_BUZZER_CMD    = 0x04;
constexpr uint8_t MSG_SENSOR_REQ    = 0x05;
constexpr uint8_t MSG_E_STOP        = 0x0E;
constexpr uint8_t MSG_HEARTBEAT_CMD = 0x0F;

// Telemetry (ESP32 → Jetson): 0x80-0xFF
constexpr uint8_t MSG_ENCODER_DATA  = 0x81;
constexpr uint8_t MSG_IMU_DATA      = 0x82;
constexpr uint8_t MSG_BATTERY_DATA  = 0x83;
constexpr uint8_t MSG_STATUS        = 0x84;
constexpr uint8_t MSG_ACK           = 0x85;
constexpr uint8_t MSG_ERROR         = 0x8E;
constexpr uint8_t MSG_HEARTBEAT_RSP = 0x8F;

// --- Payload Limits ---
constexpr uint8_t MAX_PAYLOAD = 250;
constexpr size_t  MAX_FRAME   = 255; // Header(3) + MAX_PAYLOAD + CRC(2)

// --- Command Structs (packed, little-endian) ---

struct __attribute__((packed)) MotorCmd {
    int16_t wheels[6];   // -1000 to +1000 (0.1% resolution)
    // Order: FL, FR, ML, MR, RL, RR
};

struct __attribute__((packed)) ServoCmd {
    uint16_t angles[4];  // 0-1800 (0.1 degree resolution)
    // Order: FL, FR, RL, RR
};

struct __attribute__((packed)) LedCmd {
    uint8_t mode;        // 0=off, 1=solid, 2=blink, 3=chase
    uint8_t r, g, b;
    uint8_t brightness;  // 0-255
};

struct __attribute__((packed)) BuzzerCmd {
    uint16_t freq_hz;
    uint16_t duration_ms;
    uint8_t  pattern;    // 0=single, 1=double, 2=triple, 3=continuous
};

// --- Telemetry Structs ---

struct __attribute__((packed)) EncoderData {
    int32_t ticks[6];    // Cumulative encoder counts
};

struct __attribute__((packed)) ImuData {
    int16_t quat[4];     // w,x,y,z — raw BNO055 (divide by 16384.0 for unit quat)
    int16_t accel[3];    // x,y,z in milli-g
    int16_t gyro[3];     // x,y,z in 0.1 deg/s
};

struct __attribute__((packed)) BatteryData {
    uint16_t voltage_mv;
    uint16_t current_ma;
    uint8_t  percent;    // 0-100
};

struct __attribute__((packed)) StatusData {
    uint8_t  state;      // 0=boot, 1=ok, 2=estop, 3=error, 4=low_batt
    uint8_t  error_flags; // Bitmask: motor|imu|encoder|servo|battery
    uint16_t loop_time_us;
    uint8_t  cpu_temp;   // Celsius
};

struct __attribute__((packed)) AckData {
    uint8_t acked_msg_id;
    uint8_t acked_seq;
    uint8_t result_code; // 0=OK, 1=invalid, 2=busy, 3=unsupported
};

struct __attribute__((packed)) ErrorData {
    uint8_t  error_code;
    uint8_t  severity;   // 0=info, 1=warning, 2=critical
    uint16_t detail;     // Error-specific detail value
};

struct __attribute__((packed)) HeartbeatRsp {
    uint8_t system_state;
    uint8_t fw_major;
    uint8_t fw_minor;
};
```

---

## 11. Protocol Handler Class (ESP32)

```cpp
class UartProtocol {
public:
    using MessageCallback = void(*)(uint8_t msgId, uint8_t seq,
                                     const uint8_t* data, uint8_t len);

    void begin(HardwareSerial& serial, uint32_t baud, MessageCallback cb) {
        _serial = &serial;
        _callback = cb;
        _serial->begin(baud, SERIAL_8N1, /*rx=*/44, /*tx=*/43);
        _serial->setRxBufferSize(512);
    }

    bool send(uint8_t msgId, const uint8_t* data, uint8_t dataLen) {
        if (dataLen > MAX_PAYLOAD) return false;

        uint8_t raw[MAX_FRAME];
        raw[0] = msgId;
        raw[1] = _txSeq++;
        raw[2] = dataLen;
        if (dataLen > 0) memcpy(&raw[3], data, dataLen);

        uint16_t crc = crc16(raw, 3 + dataLen);
        raw[3 + dataLen] = (uint8_t)(crc >> 8);
        raw[4 + dataLen] = (uint8_t)(crc & 0xFF);

        uint8_t encoded[MAX_FRAME + 2];
        size_t encLen = cobsEncode(raw, 5 + dataLen, encoded);

        _serial->write((uint8_t)0x00);
        _serial->write(encoded, encLen);
        _serial->write((uint8_t)0x00);
        return true;
    }

    void update() {
        while (_serial->available()) {
            uint8_t b = _serial->read();
            if (b == 0x00) {
                if (_rxLen > 0) {
                    processFrame(_rxBuf, _rxLen);
                    _rxLen = 0;
                }
            } else {
                if (_rxLen < sizeof(_rxBuf)) {
                    _rxBuf[_rxLen++] = b;
                } else {
                    _rxLen = 0;
                    _errCount++;
                }
            }
        }
    }

    uint32_t getErrorCount() const { return _errCount; }
    uint32_t getDroppedCount() const { return _dropCount; }

private:
    void processFrame(const uint8_t* cobsData, size_t cobsLen) {
        uint8_t decoded[MAX_FRAME];
        size_t decLen = cobsDecode(cobsData, cobsLen, decoded);
        if (decLen < 5) { _errCount++; return; }

        uint8_t msgId   = decoded[0];
        uint8_t seq     = decoded[1];
        uint8_t dataLen = decoded[2];

        if ((size_t)(dataLen + 5) != decLen) { _errCount++; return; }

        uint16_t rxCrc   = ((uint16_t)decoded[decLen - 2] << 8) | decoded[decLen - 1];
        uint16_t calcCrc = crc16(decoded, decLen - 2);
        if (rxCrc != calcCrc) { _errCount++; return; }

        // Track sequence gaps
        if (seq != (uint8_t)(_lastRxSeq + 1) && _lastRxSeq != -1) {
            _dropCount++;
        }
        _lastRxSeq = seq;

        if (_callback) {
            _callback(msgId, seq, &decoded[3], dataLen);
        }
    }

    HardwareSerial* _serial = nullptr;
    MessageCallback _callback = nullptr;
    uint8_t  _txSeq = 0;
    int16_t  _lastRxSeq = -1;
    uint8_t  _rxBuf[MAX_FRAME + 2];
    size_t   _rxLen = 0;
    uint32_t _errCount = 0;
    uint32_t _dropCount = 0;
};
```

---

## 12. Python Implementation (Jetson ROS2 Node)

```python
import struct
import serial
import threading
from cobs import cobs  # pip install cobs

# CRC-16/CCITT lookup table (generated from polynomial 0x1021)
_CRC_TABLE = []
for _i in range(256):
    _crc = _i << 8
    for _ in range(8):
        _crc = ((_crc << 1) ^ 0x1021) if (_crc & 0x8000) else (_crc << 1)
    _CRC_TABLE.append(_crc & 0xFFFF)

def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc = ((crc << 8) & 0xFFFF) ^ _CRC_TABLE[((crc >> 8) ^ b) & 0xFF]
    return crc


class RoverProtocol:
    def __init__(self, port='/dev/ttyTHS1', baud=460800):
        self.ser = serial.Serial(port, baud, timeout=0.001)
        self.tx_seq = 0
        self.callbacks = {}
        self.rx_buffer = bytearray()
        self.error_count = 0
        self.drop_count = 0
        self._last_rx_seq = -1
        self._running = False

    def register_callback(self, msg_id, callback):
        """Register handler: callback(msg_id, seq, data_bytes)"""
        self.callbacks[msg_id] = callback

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join(timeout=1.0)
        self.ser.close()

    def send(self, msg_id: int, data: bytes = b''):
        raw = bytes([msg_id, self.tx_seq & 0xFF, len(data)]) + data
        self.tx_seq = (self.tx_seq + 1) & 0xFF
        crc = crc16(raw)
        raw += struct.pack('>H', crc)
        encoded = cobs.encode(raw)
        self.ser.write(b'\x00' + encoded + b'\x00')

    def send_motor_cmd(self, wheels: list[int]):
        """wheels: 6× int16 values (-1000 to 1000)"""
        self.send(0x01, struct.pack('<6h', *wheels))

    def send_servo_cmd(self, angles: list[int]):
        """angles: 4× uint16 values (0-1800, in 0.1 deg)"""
        self.send(0x02, struct.pack('<4H', *angles))

    def send_estop(self, reason: int = 0):
        for _ in range(3):  # Triple-send for reliability
            self.send(0x0E, bytes([reason]))

    def send_heartbeat(self, state: int = 1):
        self.send(0x0F, bytes([state]))

    def _reader_loop(self):
        while self._running:
            chunk = self.ser.read(256)
            if not chunk:
                continue
            self.rx_buffer.extend(chunk)
            while b'\x00' in self.rx_buffer:
                idx = self.rx_buffer.index(b'\x00')
                frame = bytes(self.rx_buffer[:idx])
                self.rx_buffer = self.rx_buffer[idx + 1:]
                if frame:
                    self._process_frame(frame)

    def _process_frame(self, cobs_data: bytes):
        try:
            decoded = cobs.decode(cobs_data)
        except Exception:
            self.error_count += 1
            return

        if len(decoded) < 5:
            self.error_count += 1
            return

        msg_id, seq, data_len = decoded[0], decoded[1], decoded[2]

        if data_len + 5 != len(decoded):
            self.error_count += 1
            return

        rx_crc = struct.unpack('>H', decoded[-2:])[0]
        if crc16(decoded[:-2]) != rx_crc:
            self.error_count += 1
            return

        # Track sequence gaps
        if self._last_rx_seq >= 0 and seq != (self._last_rx_seq + 1) & 0xFF:
            self.drop_count += 1
        self._last_rx_seq = seq

        data = bytes(decoded[3:-2])
        cb = self.callbacks.get(msg_id)
        if cb:
            cb(msg_id, seq, data)
```

---

## 13. Debug Mode

Binary protocols need a debug layer. The approach: debug output on a **separate channel** while the protocol stays binary on the main UART.

**ESP32**: Debug prints go to `Serial` (USB) while the protocol runs on `Serial1` (GPIO43/44):

```cpp
if (debugEnabled) {
    Serial.printf("[RX] ID=0x%02X SEQ=%d LEN=%d\n", msgId, seq, dataLen);
}
```

**Jetson**: Python logging module with configurable verbosity:

```python
import logging
log = logging.getLogger('rover_protocol')
# In _process_frame:
log.debug(f"[RX] ID=0x{msg_id:02X} SEQ={seq} LEN={data_len} DATA={data.hex()}")
```

For field debugging without a laptop, the PWA can display protocol health stats (error count, drop count, message rates) fetched from the Jetson over WebSocket.

---

## 14. Timing Architecture

### 14.1 50Hz Interleaved Schedule

```
Time 0ms:    Jetson sends MOTOR_CMD + SERVO_CMD (~0.7ms wire time)
Time 1ms:    ESP32 receives, applies motor/servo commands
Time 1.5ms:  ESP32 sends ENCODER_DATA (~0.65ms wire time)
Time 2.5ms:  ESP32 sends IMU_DATA (~0.56ms wire time)
Time 3.5ms:  Idle — ESP32 runs PID loops, sensor reads
Time 20ms:   Next cycle
```

Every 500ms: ESP32 appends BATTERY_DATA to telemetry burst.
Every 1000ms: Both sides exchange heartbeats.

### 14.2 Fire-and-Forget vs ACK

| Command Type | ACK Required? | Rationale |
|--------------|---------------|-----------|
| MOTOR_CMD | No | Next command at 50Hz supersedes |
| SERVO_CMD | No | Same reasoning |
| LED_CMD | Yes | Infrequent, user expects confirmation |
| BUZZER_CMD | Yes | Infrequent |
| E_STOP | No (triple-send instead) | Don't wait for ACK in emergency |
| HEARTBEAT | No | Absence = alarm |
| Sensor data | No | Real-time, goes stale |

### 14.3 Buffer Sizes

| Side | RX Buffer | TX Buffer | Holds |
|------|-----------|-----------|-------|
| ESP32-S3 | 512 bytes | 512 bytes | ~28 max-length messages |
| Jetson | 4096 bytes (OS) | 4096 bytes | ~227 max-length messages |

At 12% utilisation, buffer overflow is not a realistic concern.

---

## 15. Migration Path: EA-12 → EA-18

Phase 1 firmware uses WiFi/WebSocket (no UART). Phase 2 adds the Jetson and switches to UART. The firmware architecture supports this cleanly:

```
Phase 1 (EA-12 style, if UART debugging needed):
  Input:  Text NMEA commands from serial monitor
  Core:   updateMotors(), updateSteering(), readSensors()
  Output: Text NMEA responses to serial monitor

Phase 2 (EA-18 binary):
  Input:  Binary COBS commands from Jetson UART
  Core:   updateMotors(), updateSteering(), readSensors()  ← IDENTICAL
  Output: Binary COBS telemetry to Jetson UART
```

The motor control, sensor reading, and PID loop code is shared between phases. Only the communication layer is swapped. A compile-time `#define PHASE2_BINARY_PROTOCOL` selects the active protocol.

For debugging Phase 2 issues, a `#define UART_DEBUG_TEXT` flag can temporarily switch back to NMEA text output on Serial1 for serial monitor inspection, while the binary protocol runs on a second UART if available.

---

## 16. Summary

| Parameter | EA-12 (Phase 1/Debug) | EA-18 (Phase 2) |
|-----------|----------------------|-----------------|
| Baud rate | 115200 | 460800 |
| Format | Text NMEA `$CMD,data*XOR\n` | Binary COBS `[0x00][payload][0x00]` |
| Checksum | XOR (8-bit) | CRC-16/CCITT (16-bit) |
| Framing | `$` start, `\n` end | `0x00` delimiters |
| Float on ESP32 | Yes (string conversion) | No (scaled integers) |
| Bandwidth utilisation | 72% | 12% |
| Round-trip latency | ~7.7ms | ~1.6ms |
| Motor cmd size | ~35 bytes | ~18 bytes |
| Sync recovery | Scan for `$` | Scan for `0x00` (instant) |
| Motor safety timeout | 200ms | 500ms (with 200ms ramp-down) |
| E-Stop reliability | Single send | Triple send |
| Debug readability | Excellent (serial monitor) | Requires debug channel (USB serial or logging) |
| Message types | 18 (11 cmd + 7 rsp) | 14 (7 cmd + 7 rsp) — consolidated |

**Bottom line**: EA-12's text protocol is ideal for Phase 1 development and debugging. EA-18's binary protocol is the production choice for Phase 2 when real-time performance, reliability, and bandwidth headroom matter.

---

*Document EA-18 v1.0 — 2026-03-15*

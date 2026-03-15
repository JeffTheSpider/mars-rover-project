# Engineering Analysis 12: UART Communication Protocol Specification

**Document**: EA-12
**Date**: 2026-03-15
**Purpose**: Define the serial communication protocol between the Jetson Orin Nano (main brain) and ESP32-S3 (motor controller), including message format, framing, error detection, timing, and bandwidth analysis.
**Depends on**: EA-04 (Compute), EA-09 (GPIO Pin Map)

---

## 1. Physical Layer

### 1.1 Connection

| Parameter | Value | Notes |
|-----------|-------|-------|
| Interface | UART (TTL-level, 3.3V) | Both devices are 3.3V — no level shifter needed |
| Jetson UART | /dev/ttyTHS1 (UART1) | 40-pin header pins 8 (TX) + 10 (RX) |
| ESP32 UART | UART1 (GPIO43 TX, GPIO44 RX) | See EA-09 |
| Baud rate | **115200** | Reliable, well-tested, standard |
| Data bits | 8 | Standard |
| Parity | None | CRC provides error detection |
| Stop bits | 1 | Standard |
| Flow control | **None** | Hardware RTS/CTS not needed at this baud rate |
| Wire | 3-wire (TX, RX, GND) | Shared ground essential |
| Max cable length | ~30cm | Within rover body — well under limits |

### 1.2 Baud Rate Selection

| Baud Rate | Throughput | Latency (64 byte msg) | Verdict |
|-----------|-----------|----------------------|---------|
| 9600 | 960 B/s | 66.7 ms | Too slow |
| 115200 | 11,520 B/s | 5.6 ms | **Selected** — fast enough, universally reliable |
| 230400 | 23,040 B/s | 2.8 ms | Possible but no benefit for our data rate |
| 460800 | 46,080 B/s | 1.4 ms | Risk of errors on long wires |
| 921600 | 92,160 B/s | 0.7 ms | Unreliable without flow control |

**115200 baud** is selected because:
- Round-trip for a 64-byte command + 64-byte response ≈ 11ms — well under our 20ms target
- Universally supported by all UART libraries (Arduino Serial, Python pyserial)
- No flow control needed at this speed with short wires
- Proven reliable in thousands of embedded projects

---

## 2. Protocol Design

### 2.1 Approach Selection

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **A: Text-based (NMEA-style)** | Human-readable for debugging, simple parsing, `minicom`/`screen` compatible | Larger messages, slower parsing on MCU | **Selected** |
| B: Binary + COBS | Compact, fast parsing | Not debuggable with serial monitor, complex framing | Overkill |
| C: MAVLink | Industry standard, well-tested | Heavy dependency, complex, designed for drones | Too complex |
| D: ROSSerial | Native ROS integration | Deprecated in ROS2, replaced by micro-ROS | Not compatible |

**Rationale for text-based**: The data rate is low enough (~5 KB/s total) that text overhead is negligible. The massive advantage of being able to debug with a serial terminal (`minicom`, Arduino Serial Monitor) outweighs the ~2× size increase.

### 2.2 Message Format

```
$<CMD>,<data1>,<data2>,...,<dataN>*<XOR checksum>\n

Where:
  $         Start delimiter (0x24)
  CMD       2-3 character command ID (uppercase)
  data      Comma-separated values (integers or fixed-point decimal)
  *         Checksum delimiter (0x2A)
  XOR       2-character hex XOR checksum of all bytes between $ and * (exclusive)
  \n        End delimiter (0x0A, newline)
```

**Example**: `$MOT,50,-50,50,-50,50,-50*7A\n`

### 2.3 Checksum Calculation

XOR of all characters between `$` and `*` (exclusive of both delimiters):

```c
uint8_t calculateChecksum(const char* msg) {
    uint8_t xor_val = 0;
    // Skip the leading '$', stop at '*'
    for (int i = 1; msg[i] != '*' && msg[i] != '\0'; i++) {
        xor_val ^= msg[i];
    }
    return xor_val;
}
```

**Example**:
```
$MOT,50,-50*XX

XOR = 'M' ^ 'O' ^ 'T' ^ ',' ^ '5' ^ '0' ^ ',' ^ '-' ^ '5' ^ '0'
    = 0x4D ^ 0x4F ^ 0x54 ^ 0x2C ^ 0x35 ^ 0x30 ^ 0x2C ^ 0x2D ^ 0x35 ^ 0x30
    = 0x7A

Result: $MOT,50,-50*7A
```

---

## 3. Message Catalogue

### 3.1 Jetson → ESP32 Commands

| CMD | Name | Format | Fields | Rate | Example |
|-----|------|--------|--------|------|---------|
| MOT | Motor speeds | `$MOT,w1,w2,w3,w4,w5,w6*XX` | 6× speed (-100 to +100, %) | 50 Hz | `$MOT,50,50,50,-50,-50,-50*7A` |
| STR | Steering angles | `$STR,fl,fr,rl,rr*XX` | 4× angle (-35.0 to +35.0, degrees, 1 decimal) | 50 Hz | `$STR,15.3,10.8,-15.3,-10.8*4B` |
| LED | LED control | `$LED,mode,r,g,b*XX` | mode(0=off,1=solid,2=blink,3=chase), RGB (0-255) | On change | `$LED,1,255,0,0*2F` |
| BUZ | Buzzer | `$BUZ,freq,duration*XX` | freq (Hz), duration (ms, 0=off) | On change | `$BUZ,1000,500*3C` |
| STP | Emergency stop | `$STP*XX` | No data | Immediate | `$STP*1C` |
| RSM | Resume from E-stop | `$RSM*XX` | No data | Once | `$RSM*0A` |
| REQ | Request sensor data | `$REQ,type*XX` | type: ALL/ENC/IMU/BAT/STS | 10-50 Hz | `$REQ,ALL*2B` |
| CFG | Configuration | `$CFG,key,value*XX` | key=value pair | On change | `$CFG,PID_KP,1.5*4E` |
| SVO | Direct servo | `$SVO,ch,us*XX` | PCA9685 channel, microseconds | On change | `$SVO,4,1500*33` |
| MOD | Steering mode | `$MOD,mode,param*XX` | mode(0-3), param (see EA-10) | On change | `$MOD,0,2000*5A` |
| PNG | Ping | `$PNG*XX` | No data | 1 Hz | `$PNG*19` |

### 3.2 ESP32 → Jetson Responses

| CMD | Name | Format | Fields | Rate | Example |
|-----|------|--------|--------|------|---------|
| ENC | Encoder counts | `$ENC,t1,t2,t3,t4,t5,t6*XX` | 6× tick count (32-bit signed) | 50 Hz | `$ENC,1234,1230,1228,-1240,-1238,-1235*5D` |
| IMU | IMU data | `$IMU,qw,qx,qy,qz,ax,ay,az*XX` | Quaternion (4× float, 3 decimal) + accel (3× float, m/s², 2 decimal) | 50 Hz | `$IMU,0.998,0.012,-0.005,0.001,0.15,-0.08,9.79*3B` |
| BAT | Battery status | `$BAT,voltage,current,pct*XX` | voltage (V, 2 dec), current (A, 2 dec), percent (0-100) | 1 Hz | `$BAT,22.45,3.21,78*6C` |
| STS | System status | `$STS,state,uptime,temp*XX` | state(0=boot,1=ok,2=estop,3=error), uptime(s), temp(°C) | 1 Hz | `$STS,1,3600,42*5E` |
| ACK | Command acknowledge | `$ACK,cmd*XX` | Original command ID | Per cmd | `$ACK,MOT*2A` |
| ERR | Error report | `$ERR,code,msg*XX` | Error code, human-readable message | On error | `$ERR,3,motor_overcurrent*4F` |
| PON | Pong (ping response) | `$PON*XX` | No data | Per ping | `$PON*08` |

### 3.3 Error Codes

| Code | Meaning | Severity |
|------|---------|----------|
| 1 | Checksum mismatch | Warning (message ignored) |
| 2 | Unknown command | Warning |
| 3 | Motor overcurrent | Critical (motors stopped) |
| 4 | Battery undervoltage | Critical (motors stopped) |
| 5 | IMU communication failure | Warning |
| 6 | Encoder reading invalid | Warning |
| 7 | Servo out of range | Warning (clamped) |
| 8 | Watchdog timeout | Critical (motors stopped) |
| 9 | E-stop activated | Info |
| 10 | PCA9685 communication failure | Critical (servos frozen) |

---

## 4. Timing & Scheduling

### 4.1 Communication Timeline

The protocol uses a **request-response** pattern for sensor data and **fire-and-forget** for motor commands (with periodic ACK).

```
Timeline (20ms window = 50Hz cycle):

Time  Direction   Message            Size    Duration
0ms   J→E        $MOT,50,50,...*XX   ~35B    3.0ms
3ms   J→E        $STR,15.3,...*XX    ~30B    2.6ms
5.6ms E→J        $ENC,1234,...*XX    ~45B    3.9ms
9.5ms E→J        $IMU,0.998,...*XX   ~55B    4.8ms
14.3ms            --- idle ---
─────── 20ms window ───────
```

### 4.2 Message Scheduling

| Priority | Message | Rate | Initiator | Notes |
|----------|---------|------|-----------|-------|
| 1 (highest) | STP (E-stop) | Immediate | Jetson or ESP32 | Bypasses queue |
| 2 | MOT (motor speeds) | 50 Hz | Jetson | Every 20ms cycle |
| 3 | STR (steering) | 50 Hz | Jetson | Every 20ms cycle (after MOT) |
| 4 | ENC (encoders) | 50 Hz | ESP32 | Sent after MOT received |
| 5 | IMU (orientation) | 50 Hz | ESP32 | Sent after ENC |
| 6 | BAT (battery) | 1 Hz | ESP32 | Every 50th cycle |
| 7 | STS (status) | 1 Hz | ESP32 | Every 50th cycle (offset from BAT) |
| 8 | PNG/PON (heartbeat) | 1 Hz | Jetson | Every 50th cycle |
| 9 (lowest) | LED/BUZ/CFG | On change | Jetson | Insert into idle slots |

### 4.3 Typical 1-Second Communication Pattern

```
Cycles 1-50 (50Hz, 1 second):

Every cycle:  J→E: MOT, STR    E→J: ENC, IMU
Cycle 1:      + J→E: PNG       + E→J: PON
Cycle 10:                      + E→J: BAT
Cycle 25:                      + E→J: STS
Cycle 35:     + J→E: LED       (if changed)
```

---

## 5. Bandwidth Analysis

### 5.1 Per-Message Size

| Message | Typical Size (bytes) | Max Size (bytes) |
|---------|---------------------|-----------------|
| MOT | 35 | 42 |
| STR | 30 | 36 |
| ENC | 45 | 60 |
| IMU | 55 | 70 |
| BAT | 22 | 28 |
| STS | 20 | 25 |
| PNG/PON | 8 | 8 |
| LED | 20 | 24 |
| ACK | 10 | 12 |
| ERR | 30 | 50 |

### 5.2 Sustained Bandwidth

At 50 Hz:

| Direction | Messages per cycle | Bytes per cycle | Bytes per second |
|-----------|-------------------|-----------------|-----------------|
| Jetson → ESP32 | MOT(35) + STR(30) | 65 | 3,250 |
| ESP32 → Jetson | ENC(45) + IMU(55) | 100 | 5,000 |
| Overhead (1Hz msgs) | BAT+STS+PNG+PON | ~60 | 60 |
| **Total** | | **~225 B/cycle** | **~8,310 B/s** |

**Available bandwidth**: 11,520 B/s (115200 baud ÷ 10 bits/byte)
**Utilisation**: 8,310 / 11,520 = **72%**

This leaves ~28% headroom for occasional LED/BUZ/CFG commands and error messages. Sufficient but not excessive — if we need more bandwidth (e.g., camera commands), bump to 230400 baud.

### 5.3 Latency Budget

| Component | Time |
|-----------|------|
| Jetson serialises MOT message | <0.1ms |
| UART transmission (35 bytes) | 3.0ms |
| ESP32 parses + executes | <0.5ms |
| ESP32 serialises ENC response | <0.1ms |
| UART transmission (45 bytes) | 3.9ms |
| Jetson parses response | <0.1ms |
| **Total round-trip** | **~7.7ms** |

Well under our 20ms (50Hz) target.

---

## 6. Error Handling

### 6.1 Checksum Failure

If the receiver calculates a checksum that doesn't match:
1. Discard the message entirely
2. Increment error counter
3. Wait for next valid message
4. If >10 consecutive checksum failures: send ERR and assume noise/disconnect

### 6.2 Timeout

**Jetson → ESP32 timeout**: If ESP32 doesn't receive a MOT or PNG within **200ms** (10× the 20ms cycle):
- Set all motors to 0% (safe stop)
- Blink status LED amber
- Continue checking for messages
- Resume immediately when valid message arrives

**ESP32 → Jetson timeout**: If Jetson doesn't receive ENC/IMU or PON within **200ms**:
- Assume ESP32 has reset or disconnected
- Attempt to re-establish connection (send PNG every 100ms)
- Log warning in ROS2

### 6.3 Buffer Overflow

Both sides use ring buffers for UART:

| Side | RX Buffer | TX Buffer |
|------|-----------|-----------|
| ESP32 | 512 bytes | 512 bytes |
| Jetson | 4096 bytes (OS default) | 4096 bytes |

At 115200 baud, the ESP32 RX buffer holds ~44ms of data (512 / 11,520). Since we process messages every 20ms (in the main loop), overflow is unlikely. But as a safety measure:

- ESP32: Process UART in a FreeRTOS task at priority 5 (above idle, below motor control)
- Jetson: Use non-blocking reads with select() or asyncio

### 6.4 Framing Recovery

If the receiver gets out of sync (partial message, noise), recovery is simple:
1. Discard bytes until a `$` is found
2. Buffer bytes until `\n` is found
3. Validate checksum
4. If valid: process message. If invalid: discard and wait for next `$`

This self-synchronising property is a key advantage of the text-based format.

---

## 7. Implementation

### 7.1 ESP32 (Arduino C++) — Receiver

```c
#define UART_BUF_SIZE 256
char uart_buf[UART_BUF_SIZE];
int uart_idx = 0;
bool uart_receiving = false;

void processUART() {
    while (Serial1.available()) {
        char c = Serial1.read();

        if (c == '$') {
            // Start of new message
            uart_idx = 0;
            uart_receiving = true;
            uart_buf[uart_idx++] = c;
        } else if (uart_receiving) {
            uart_buf[uart_idx++] = c;

            if (c == '\n' || uart_idx >= UART_BUF_SIZE - 1) {
                uart_buf[uart_idx] = '\0';

                if (c == '\n' && validateChecksum(uart_buf)) {
                    parseCommand(uart_buf);
                }

                uart_receiving = false;
                uart_idx = 0;
            }
        }
    }
}

void parseCommand(const char* msg) {
    // Extract command ID (3 chars after $)
    char cmd[4];
    strncpy(cmd, msg + 1, 3);
    cmd[3] = '\0';

    // Find first comma (start of data)
    const char* data = strchr(msg + 1, ',');

    if (strcmp(cmd, "MOT") == 0) {
        parseMotorCommand(data);
    } else if (strcmp(cmd, "STR") == 0) {
        parseSteeringCommand(data);
    } else if (strcmp(cmd, "STP") == 0) {
        emergencyStop();
    } else if (strcmp(cmd, "PNG") == 0) {
        sendPong();
    }
    // ... etc
}
```

### 7.2 Jetson (Python) — Sender

```python
import serial
import struct
import time

class RoverUART:
    def __init__(self, port='/dev/ttyTHS1', baud=115200):
        self.ser = serial.Serial(port, baud, timeout=0.1)
        self.last_rx_time = time.time()

    def _checksum(self, msg: str) -> str:
        """Calculate XOR checksum of message between $ and *"""
        xor = 0
        for c in msg[1:]:  # Skip $, stop at *
            if c == '*':
                break
            xor ^= ord(c)
        return f'{xor:02X}'

    def send(self, cmd: str, *args):
        """Send a command with arguments"""
        if args:
            data = ','.join(str(a) for a in args)
            body = f'{cmd},{data}'
        else:
            body = cmd

        msg = f'${body}*'
        msg += self._checksum(msg) + '\n'
        self.ser.write(msg.encode('ascii'))

    def send_motors(self, speeds: list):
        """Send motor speed command (6 values, -100 to +100)"""
        self.send('MOT', *[int(s) for s in speeds])

    def send_steering(self, angles: list):
        """Send steering angle command (4 values, degrees)"""
        self.send('STR', *[f'{a:.1f}' for a in angles])

    def send_estop(self):
        """Send emergency stop"""
        self.send('STP')

    def read_message(self) -> dict:
        """Read and parse one message from ESP32"""
        line = self.ser.readline().decode('ascii', errors='ignore').strip()
        if not line or line[0] != '$':
            return None

        # Validate checksum
        star_idx = line.rfind('*')
        if star_idx < 0 or len(line) < star_idx + 3:
            return None

        expected = self._checksum(line[:star_idx + 1])
        actual = line[star_idx + 1:star_idx + 3]
        if expected != actual:
            return None

        # Parse
        body = line[1:star_idx]
        parts = body.split(',')
        cmd = parts[0]
        data = parts[1:] if len(parts) > 1 else []

        self.last_rx_time = time.time()
        return {'cmd': cmd, 'data': data}
```

### 7.3 ROS2 Integration (Jetson)

The UART driver runs as a ROS2 node that publishes sensor data and subscribes to motor commands:

```
ROS2 Topics:

Published by uart_node:
  /rover/encoders     sensor_msgs/JointState      50 Hz
  /rover/imu          sensor_msgs/Imu             50 Hz
  /rover/battery      sensor_msgs/BatteryState    1 Hz
  /rover/status       std_msgs/String             1 Hz

Subscribed by uart_node:
  /rover/cmd_vel      geometry_msgs/Twist         50 Hz → converted to MOT+STR
  /rover/led          std_msgs/ColorRGBA          on change → LED
  /rover/estop        std_msgs/Bool               immediate → STP
```

The uart_node converts ROS2 Twist messages (linear + angular velocity) into individual wheel speeds and Ackermann steering angles using the calculations from EA-10.

---

## 8. Phase 1 Simplification

Phase 1 doesn't have a Jetson — the ESP32-S3 operates standalone with a WiFi web server for control. The UART protocol is not used in Phase 1.

However, the ESP32 firmware should be structured so the motor control and sensor reading code is modular — when Phase 2 adds the Jetson, the web server control is replaced by UART control with minimal code changes:

```c
// Phase 1: commands come from web server
void loop() {
    handleWebServer();       // Parse HTTP requests → motor/steering values
    updateMotors();          // Apply motor speeds
    updateSteering();        // Apply steering angles
    readSensors();           // Read encoders + battery
    sendWebUpdate();         // Report to web UI via WebSocket
}

// Phase 2: commands come from UART
void loop() {
    processUART();           // Parse UART commands → motor/steering values
    updateMotors();          // Same function as Phase 1
    updateSteering();        // Same function as Phase 1
    readSensors();           // Same function as Phase 1
    sendSensorData();        // Report to Jetson via UART
}
```

The `updateMotors()`, `updateSteering()`, and `readSensors()` functions are identical in both phases — only the input/output layer changes.

---

## 9. Testing & Debugging

### 9.1 Loopback Test

Before connecting Jetson to ESP32, test each side independently:

**ESP32 loopback**: Connect TX to RX on the ESP32. Send a message, verify it's received back correctly.

**Jetson loopback**: Use a USB-to-UART adapter connected to the Jetson's UART pins. Send messages from a Python script, verify with `minicom`.

### 9.2 Serial Monitor Debugging

Since the protocol is text-based, you can monitor all traffic with:

```bash
# On Jetson
minicom -D /dev/ttyTHS1 -b 115200

# Or with screen
screen /dev/ttyTHS1 115200
```

You'll see human-readable messages like:
```
$MOT,50,50,50,-50,-50,-50*7A
$ENC,1234,1230,1228,-1240,-1238,-1235*5D
$IMU,0.998,0.012,-0.005,0.001,0.15,-0.08,9.79*3B
$BAT,22.45,3.21,78*6C
```

### 9.3 Protocol Analyser

A simple Python script to log and analyse protocol health:

```python
# Log all messages with timestamps, flag errors
import serial, time

ser = serial.Serial('/dev/ttyTHS1', 115200)
error_count = 0
msg_count = 0

while True:
    line = ser.readline().decode('ascii', errors='ignore').strip()
    if line:
        msg_count += 1
        # Validate checksum
        if not validate(line):
            error_count += 1
            print(f"[ERR] {line}")
        else:
            print(f"[{time.time():.3f}] {line}")

        if msg_count % 100 == 0:
            print(f"--- Stats: {msg_count} msgs, {error_count} errors "
                  f"({100*error_count/msg_count:.1f}%) ---")
```

---

## 10. Summary

| Parameter | Value |
|-----------|-------|
| Physical | 3.3V UART, 115200 8N1, 3-wire |
| Format | Text-based NMEA-style: `$CMD,data*XOR\n` |
| Checksum | XOR (1 byte, 2 hex chars) |
| Motor update rate | 50 Hz |
| Sensor feedback rate | 50 Hz |
| Heartbeat rate | 1 Hz |
| Round-trip latency | ~7.7 ms |
| Bandwidth utilisation | 72% at 115200 |
| Timeout (safety stop) | 200 ms |
| Message types | 11 commands + 7 responses = 18 total |
| Error recovery | Self-synchronising (scan for `$`, validate checksum) |
| Phase 1 | Not used (ESP32 standalone with WiFi) |
| Phase 2 | Full protocol, ROS2 integration |

---

*Document EA-12 v1.0 — 2026-03-15*

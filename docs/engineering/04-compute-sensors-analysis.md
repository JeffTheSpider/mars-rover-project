# Engineering Analysis 04: Compute Platform & Sensor Suite

**Document**: EA-04
**Date**: 2026-03-15
**Purpose**: Select the compute platform, camera system, LIDAR, GPS, IMU, and all sensors. Define the system integration architecture.

---

## 1. Compute Platform Selection

### 1.1 Candidate Comparison

| Parameter | Jetson Orin Nano 8GB | Jetson Orin Nano Super | Raspberry Pi 5 (8GB) | Pi 5 + Coral USB TPU |
|-----------|---------------------|----------------------|---------------------|---------------------|
| **AI Performance (TOPS)** | 40 | 67 | ~2 (CPU only) | ~6 (with Coral) |
| **GPU** | 1024 CUDA + 32 Tensor | 1024 CUDA + 32 Tensor | VideoCore VII | None (Coral is TPU) |
| **CPU** | 6-core ARM A78AE | 6-core ARM A78AE | 4-core Cortex-A76 | 4-core Cortex-A76 |
| **RAM** | 8GB LPDDR5 | 8GB LPDDR5 | 8GB LPDDR4X | 8GB LPDDR4X |
| **YOLO v8 (640px)** | 20-40 FPS | 30-60 FPS | 2-5 FPS | 10-15 FPS |
| **Camera interfaces** | 2× CSI + USB 3.0 | 2× CSI + USB 3.0 | 2× CSI + USB 3.0 | 2× CSI + USB 3.0 |
| **Power draw** | 7-15W | 7-25W | 5-10W | 7-12W |
| **ROS2 support** | Excellent (NVIDIA Isaac) | Excellent | Good (community) | Good |
| **Price** | ~$200 | ~$249 | ~$80 | ~$150 ($80+$70) |
| **Storage** | microSD / NVMe | microSD / NVMe | microSD | microSD |
| **OS** | JetPack (Ubuntu-based) | JetPack (Ubuntu-based) | Raspberry Pi OS / Ubuntu | Raspberry Pi OS / Ubuntu |

### 1.2 Analysis

**AI Vision is the rover's flagship feature** — real-time object detection, depth processing, SLAM, and path planning running simultaneously. This rules out the Pi 5 alone (2-5 FPS on YOLO is unusable for real-time driving).

Pi 5 + Coral TPU improves to 10-15 FPS but:
- Coral USB TPU is limited to TensorFlow Lite models (no native YOLO v8)
- No CUDA means no GPU-accelerated ROS2 (Isaac ROS)
- Two separate systems (CPU + TPU) with data transfer overhead

**The Jetson Orin Nano Super ($249) is the clear winner** for our use case:
- 67 TOPS handles YOLO v8 at 30-60 FPS (real-time driving)
- NVIDIA Isaac ROS2 packages are purpose-built for robotics
- Single unified platform (no external accelerators)
- The $169 price premium over Pi 5 is justified by 10-30× AI performance

### 1.3 Decision

**Jetson Orin Nano Super Developer Kit ($249)** — the AI brain of the rover.

The ESP32-S3 handles all real-time motor/sensor control (as designed in EA-02), so the Jetson only needs to run the "smart" tasks: vision, navigation, web server.

### 1.4 TensorRT Deployment

**WARNING**: TensorRT engines MUST be exported ON the Jetson — engines are GPU-architecture-specific. Never export on a PC and copy to Jetson.

Export pipeline (run on the Jetson Orin Nano Super):

```bash
# On Jetson Orin Nano Super:
yolo export model=yolov8n.pt format=onnx imgsz=640 simplify=True opset=18
/usr/src/tensorrt/bin/trtexec --onnx=yolov8n.onnx --saveEngine=yolov8n_fp16.engine --fp16
```

**Gotcha**: FP16 + dynamic shapes are incompatible — always use static input size (640x640). Dynamic batch/resolution triggers TensorRT builder failures or severe performance regression on Orin.

**Performance benchmarks on Orin Nano Super**:
- FP16 (640×640): ~25-35 FPS — good balance of accuracy and speed for real-time driving
- INT8 (640×640): ~50-65 FPS — reduced precision but sufficient for obstacle detection; requires calibration dataset

---

## 2. Camera System

### 2.1 Requirements by Position

| Position | FOV Needed | Resolution | Framerate | Special Needs |
|----------|-----------|------------|-----------|---------------|
| Front body | Wide (120°+) | 1080p | 30 FPS | AI detection, primary driving view |
| Rear body | Wide (120°+) | 720p | 15 FPS | Reversing, obstacle detection |
| Left body | Wide (120°+) | 720p | 15 FPS | 360° coverage |
| Right body | Wide (120°+) | 720p | 15 FPS | 360° coverage |
| Mast zoom | Narrow (5-60°) | 1080p | 30 FPS | 30× optical zoom, pan-tilt |
| Depth | Standard (86°) | 640×480 depth | 30 FPS | Stereo depth, min 0.2m range |
| Night vision | Standard (60°+) | 720p | 15 FPS | IR sensitive, 850nm |

### 2.2 Body Camera Selection

For the 4 body cameras, we need small, wide-angle, USB cameras:

| Camera | FOV | Resolution | Interface | Price | Notes |
|--------|-----|-----------|-----------|-------|-------|
| ELP USB 170° Fisheye | 170° | 1080p | USB 2.0 | ~$20 | Very wide, some distortion |
| Arducam B0205 120° | 120° | 1080p | USB 2.0 | ~$15 | Good balance |
| Logitech C270 (modded) | 60° | 720p | USB 2.0 | ~$15 | Narrow, not ideal |
| Generic 120° USB | 120° | 1080p | USB 2.0 | ~$8 | AliExpress, variable quality |

**Recommendation**: 4× **Arducam 120° wide-angle USB cameras** or similar (~$15 each, $60 total). 120° provides good 360° coverage with 4 cameras (90° overlap between adjacent cameras aids stitching).

### 2.3 Mast Zoom Camera

| Camera | Zoom | Resolution | Interface | Price | Notes |
|--------|------|-----------|-----------|-------|-------|
| ELP 10× optical zoom USB | 10× | 1080p | USB 2.0 | ~$50 | Good budget option |
| HikVision module 20× | 20× | 1080p | IP/USB | ~$80 | Network camera module |
| PTZ USB camera 30× | 30× | 1080p | USB | ~$100+ | Full PTZ built-in |
| Raspberry Pi Camera v3 + telephoto lens | 2× digital + 3× lens | 12MP | CSI | ~$45 | Limited zoom range |

**Recommendation**: **ELP 10× optical zoom USB camera** (~$50) for Phase 2. 10× is realistic at this budget. 30× requires expensive optics. We can use digital zoom on the Jetson for additional magnification.

### 2.4 Depth Camera

| Camera | Depth Range | FOV | Method | On-Device AI | Price |
|--------|-------------|-----|--------|-------------|-------|
| **OAK-D Lite** | 0.2-19.1m | 73° | Stereo passive | Yes (Myriad X VPU) | ~$89 |
| **Intel RealSense D435i** | 0.1-10m | 87° | Stereo + IR projector | No | ~$260 |
| **OAK-D Pro** | 0.2-35m | 71° | Stereo + IR | Yes (Myriad X) | ~$200 |
| **Stereolabs ZED 2i** | 0.3-20m | 110° | Stereo passive | No | ~$450 |

**Analysis**:
- **OAK-D Lite ($89)**: Best value. On-device AI processing offloads the Jetson. Passive stereo works well outdoors (textured environments).
- **RealSense D435i ($260)**: Better depth accuracy indoors (IR projector), but outdoor IR performance degrades in sunlight. 3× the price.
- The OAK-D Lite's on-device Myriad X VPU can run MobileNet-SSD independently, freeing the Jetson for other tasks.

**Recommendation**: **OAK-D Lite** ($89) — best performance-per-pound for outdoor robotics. The passive stereo works well in natural environments (grass, trees, paths are highly textured).

### 2.5 Night Vision Camera

| Camera | Sensor | IR Sensitivity | Resolution | Price |
|--------|--------|---------------|-----------|-------|
| Raspberry Pi NoIR Camera v3 | IMX708 (no IR filter) | Good (850nm) | 12MP | ~$25 |
| Generic NoIR USB camera | OV5647 or similar | Moderate | 5MP | ~$15 |
| Arducam NoIR USB | IMX219 | Good | 8MP | ~$20 |

**Recommendation**: **Raspberry Pi NoIR Camera v3** ($25) via CSI interface on the Jetson. Excellent low-light performance, well-supported. Paired with 4× 850nm IR LED illuminators (~$5 total).

### 2.6 Camera Bandwidth Analysis

```
Simultaneous camera streams:
  4× body 720p30: 4 × (1280×720×3 × 30) = 316 MB/s raw (compressed: ~20 MB/s)
  1× front 1080p30: 1 × (1920×1080×3 × 30) = 186 MB/s raw (compressed: ~8 MB/s)
  1× zoom 1080p30: ~8 MB/s compressed
  1× depth 640×480×30: ~5 MB/s
  1× IR 720p15: ~5 MB/s

Total compressed bandwidth: ~46 MB/s
USB 3.0 bandwidth: 5 Gbps = 625 MB/s → more than sufficient
Jetson USB hub: can handle 4-5 USB cameras via hub

Note: Not all cameras need to stream simultaneously at full quality.
  AI detection: front camera only at full quality → 8 MB/s
  360° stitching: 4 cameras at lower quality → 10 MB/s
  Others: on-demand
```

---

## 3. LIDAR Selection

### 3.1 Candidate Comparison

| LIDAR | Range | Angular Resolution | Scan Rate | Sample Rate | Interface | Price |
|-------|-------|-------------------|-----------|-------------|-----------|-------|
| **RPLidar A1** | 12m | 1° | 5.5 Hz | 8,000/sec | UART | ~$73 |
| **RPLidar A2** | 16m (practical ~8m) | 0.45° | 10 Hz | 16,000/sec | UART | ~$229 |
| **YDLIDAR X4** | 10m | 0.5° | 6-12 Hz | 5,000/sec | UART | ~$60 |
| **YDLIDAR G4** | 16m | 0.28° | 5-12 Hz | 9,000/sec | UART | ~$135 |

### 3.2 Analysis

- **RPLidar A1**: Best documented, most community support, ROS2 driver available. 12m range is sufficient for outdoor navigation. 8K samples/sec is adequate for 2D SLAM.
- **YDLIDAR X4**: Slightly cheaper but less community support, fewer ROS2 resources.
- **RPLidar A2**: Double the price for marginal range improvement. Not justified at our budget.

### 3.3 Decision

**RPLidar A1** ($73) — proven in robotics, excellent ROS2 support, 12m range covers all outdoor navigation needs for our use case.

---

## 4. Navigation Sensors

### 4.1 GPS Module

| Module | Accuracy | Update Rate | Interface | SBAS | Price |
|--------|----------|-------------|-----------|------|-------|
| **u-blox NEO-M8N** | 2.5m CEP | 10 Hz | UART | Yes | ~$15 |
| **u-blox NEO-M9N** | 1.5m CEP | 25 Hz | UART/I2C/SPI | Yes | ~$30 |
| **BN-220** (u-blox M8) | 2.5m CEP | 10 Hz | UART | Yes | ~$12 |
| RTK module | 1cm | 10 Hz | UART | N/A | ~$200+ |

**Recommendation**: **BN-220 (u-blox M8 based)** ($12) — cheapest option with adequate accuracy. 2.5m CEP is sufficient for park navigation (paths are >2m wide). The sensor fusion with IMU + LIDAR + wheel odometry will improve this to ~10cm.

RTK GPS would give centimetre accuracy but costs more than the rest of the sensor suite combined. Not justified for Phase 2.

### 4.2 IMU Selection

| IMU | DOF | Sensor Fusion | Interface | Accuracy (heading) | Price |
|-----|-----|---------------|-----------|-------------------|-------|
| **BNO055** | 9 (accel + gyro + mag) | On-chip fusion | I2C | ±1-2° | ~$15 |
| **MPU6050** | 6 (accel + gyro) | Software only | I2C | Requires external mag | ~$3 |
| **ICM-20948** | 9 | Software (DMP) | I2C/SPI | ±2-3° | ~$8 |
| **LSM9DS1** | 9 | Software only | I2C/SPI | ±3-5° | ~$10 |

**Recommendation**: **BNO055** ($15) — on-chip sensor fusion saves significant software development time. Outputs quaternions directly. Used extensively in robotics, well-documented with ROS2 drivers.

---

## 5. Proximity / Safety Sensors

### 5.1 Ultrasonic Sensors

**HC-SR04** — $1.50 each, 6 units ($9 total)
- Range: 2cm - 4m
- Accuracy: ±3mm
- Beam angle: ~15°
- Trigger/echo interface: 2 GPIO pins per sensor (or 1 with combined mode)
- Connected to: ESP32-S3 (handled in real-time)

Placement:
```
          [Front L] [Front R]
              \       /
    [Left]    [ROVER]    [Right]
              /       \
          [Rear L]  [Rear R]
```

6 sensors provide 360° close-range obstacle detection. These are the safety backup — if LIDAR or cameras fail, ultrasonics still prevent collisions.

### 5.2 Wheel Encoders

Covered in EA-02 (built into motor, hall effect, 1,980 counts per wheel revolution).

### 5.3 Current Sensors

**INA219** I2C current/power monitors — $2 each, 4 units ($8 total)
- Monitor: battery bus, 12V rail, 5V rail, motor total
- I2C interface: all 4 share one bus (different addresses)
- Connected to: ESP32-S3 (for real-time monitoring)

---

## 6. Sensor Fusion Architecture

### 6.1 Extended Kalman Filter (EKF)

```
Inputs:
  [GPS]         → position (lat, lon), velocity    @ 10 Hz
  [IMU BNO055]  → orientation (quaternion), accel  @ 100 Hz
  [Wheel Odom]  → velocity, distance               @ 50 Hz
  [LIDAR SLAM]  → position (x, y), heading          @ 5 Hz

EKF combines these into:
  → Fused position (x, y, z)       accuracy: ~10cm
  → Fused orientation (roll, pitch, yaw)  accuracy: ~1°
  → Fused velocity                  accuracy: ~0.1 m/s

ROS2 package: robot_localization (ekf_node)
  - Standard, well-tested, drop-in configuration
  - Handles different update rates and sensor models
  - Outputs /odom_fused topic for navigation stack
```

### 6.2 Confidence Scoring

```
High confidence (all sensors agree, recent updates):
  → Full autonomous navigation enabled
  → Max speed allowed

Medium confidence (some sensor disagreement or stale data):
  → Autonomous with caution (reduced speed)
  → Phone notification

Low confidence (sensor failure or major disagreement):
  → Stop autonomous navigation
  → Manual control only
  → Alert user
```

---

## 7. System Integration Diagram

```
                        JETSON ORIN NANO SUPER
                    ┌─────────────────────────────┐
                    │                             │
  USB 3.0 Hub ─────┤  USB 3.0 Host               │
    ├── Front cam   │    ├── Camera capture       │
    ├── Rear cam    │    ├── AI inference (YOLO)  │
    ├── Left cam    │    ├── ROS2 nodes           │
    ├── Right cam   │    ├── Web server           │
    ├── Zoom cam    │    └── SLAM / Nav2          │
    ├── OAK-D Lite  │                             │
    ├── RPLidar A1  │  CSI ── NoIR camera (IR)   │
    └── 4G dongle   │                             │
                    │  I2C ── BNO055 (IMU)        │
                    │  UART ── GPS (BN-220)       │
                    │                             │
                    │  UART ── ESP32-S3           │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────┴──────────────────┐
                    │       ESP32-S3              │
                    │                             │
                    │  GPIO ── 6× Ultrasonic      │
                    │  PWM ── 6× Motor drivers    │
                    │  PWM ── 4× Steering servos  │
                    │  PWM ── 8× Arm servos       │
                    │  PWM ── 2× Mast servos      │
                    │  ADC ── Battery voltage      │
                    │  I2C ── 4× INA219 (current) │
                    │  I2C ── BME280 (weather)     │
                    │  OneWire ── 3× DS18B20 (temp)│
                    │  GPIO ── 6× Wheel encoders  │
                    │  GPIO ── WS2812B LEDs       │
                    │  GPIO ── E-stop input        │
                    │  I2C ── BH1750 (light)      │
                    │  I2C ── VEML6075 (UV)       │
                    │  SPI ── Dashboard LCD        │
                    │  I2S ── MAX98357A (speaker)  │
                    │  I2S ── SPH0645 (mic)       │
                    └─────────────────────────────┘
```

### GPIO Count Check (ESP32-S3)

The ESP32-S3 has ~36 usable GPIO pins:

| Function | Pins Required | Notes |
|----------|--------------|-------|
| Motor PWM (6 motors × 2 pins) | 12 | DIR + PWM per motor driver channel |
| Steering servos (4×) | 4 | PWM signal |
| Arm servos (8×) | 8 | PWM via PCA9685 I2C servo driver (uses 2 I2C pins) |
| Mast servos (2×) | 2 | Or on PCA9685 as well |
| Ultrasonic (6× trig+echo) | 6 | Combined trig/echo mode (1 pin each) |
| Wheel encoders (6× 2-channel) | 12 | Quadrature A+B per encoder |
| I2C bus | 2 | SDA + SCL (shared: INA219, BME280, BH1750, VEML6075, PCA9685) |
| SPI (LCD) | 4 | MOSI, SCK, CS, DC |
| UART (Jetson) | 2 | TX, RX |
| WS2812B LEDs | 1 | Data pin |
| E-stop | 1 | Digital input |
| OneWire (DS18B20) | 1 | Shared bus, 3 sensors |
| I2S (speaker) | 3 | BCLK, LRCLK, DIN |
| I2S (mic) | 3 | BCLK, LRCLK, DOUT (can share clock with speaker) |
| ADC (battery voltage) | 1 | Via voltage divider |
| **Total** | **~50** | **Exceeds 36 GPIO!** |

### GPIO Solution: PCA9685 + Multiplexing

Use a **PCA9685 16-channel PWM driver** (I2C, $3) for all servos:
- All 14 servos (4 steering + 8 arm + 2 mast) on one PCA9685 board
- Frees 14 GPIO pins, only uses 2 I2C pins (shared bus)

Use **PCF8574 I2C GPIO expander** ($2) for ultrasonic sensors if needed.

Revised pin count with PCA9685:
| Function | Pins | Notes |
|----------|------|-------|
| Motor PWM | 12 | 6× (DIR + PWM) |
| I2C bus | 2 | Shared (PCA9685, INA219×4, BME280, BH1750, VEML6075, PCF8574) |
| SPI (LCD) | 4 | |
| UART (Jetson) | 2 | |
| WS2812B | 1 | |
| Wheel encoders | 12 | |
| OneWire | 1 | |
| ADC | 1 | |
| E-stop | 1 | |
| **Total** | **36** | **Fits!** |

I2S for audio can share pins with less-critical functions or use a second I2C audio codec.

---

## 8. 4G Connectivity

For operation at Markeaton Park (out of home WiFi range):

| Option | Type | Monthly Cost | Speed | Jetson Compatible |
|--------|------|-------------|-------|-------------------|
| Huawei E3372 USB dongle | 4G LTE | PAYG SIM (~$5/month) | 150 Mbps | Yes (Linux supported) |
| Phone hotspot | WiFi tethering | Free (uses phone data) | Variable | Yes |
| SIM7600 HAT/module | 4G LTE | PAYG SIM | 150 Mbps | Yes (UART/USB) |

**Recommendation**: Start with **phone hotspot** (free, no hardware needed). If that proves unreliable, add a **Huawei E3372 USB 4G dongle** (~$25) with a PAYG data SIM.

---

## 9. Decision Summary

| Component | Selected | Price | Justification |
|-----------|----------|-------|---------------|
| Compute | Jetson Orin Nano Super | $249 | 67 TOPS, YOLO 30-60 FPS, Isaac ROS2 |
| Body cameras (×4) | Arducam 120° USB | $60 | Wide FOV, USB, adequate quality |
| Zoom camera | ELP 10× optical zoom USB | $50 | Budget-friendly, mast mount |
| Depth camera | OAK-D Lite | $89 | On-device AI, outdoor passive stereo |
| Night camera | Pi NoIR v3 (CSI) | $25 | Excellent low-light, Jetson CSI |
| IR LEDs | 4× 850nm high-power | $5 | Night illumination |
| LIDAR | RPLidar A1 | $73 | Best documented, ROS2 native |
| GPS | BN-220 (u-blox M8) | $12 | 2.5m accuracy, adequate for fusion |
| IMU | BNO055 | $15 | On-chip fusion, quaternion output |
| Ultrasonic (×6) | HC-SR04 | $9 | Safety backup, close range |
| Current sensors (×4) | INA219 | $8 | I2C, power monitoring |
| Temp sensors (×3) | DS18B20 | $4 | Battery/electronics/ambient |
| Servo driver | PCA9685 | $3 | 16-channel I2C PWM, GPIO saver |
| **Sensor Suite Total** | | **$602** | |

---

## 10. References

- [Jetson Orin Nano Super — NVIDIA](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/)
- [YOLO v8 Jetson Benchmarks — Medium](https://medium.com/@MaroJEON/yolov8-jetson-deepstream-benchmark-test-orin-nano-4gb-8gb-nx-tx2-f3993f9c8d2f)
- [OAK-D Lite vs RealSense — Luxonis](https://docs.luxonis.com/hardware/platform/comparison/vs-realsense/)
- [RPLidar A1 — Slamtec](https://www.slamtec.com/en/Lidar/A1/)
- [BNO055 — Bosch Sensortec](https://www.bosch-sensortec.com/products/smart-sensors/bno055/)
- [Raspberry Pi vs Jetson 2025 — MonRaspberry](https://monraspberry.com/en/raspberry-pi-vs-nvidia-jetson-the-ultimate-2025-comparison/)
- [PCA9685 16-Channel PWM Driver — Adafruit](https://www.adafruit.com/product/815)

---

*Document EA-04 v1.0 — 2026-03-15*

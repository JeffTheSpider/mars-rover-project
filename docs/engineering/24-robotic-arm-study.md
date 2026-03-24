# EA-24: Robotic Arm Feasibility Study

Version 1.0, Date 2026-03-23

## 1. Executive Summary
The robotic arm is a Phase 2 feature. Phase 1 provides only the mounting interface (4× M3 heat-set insert bosses on the FL body quadrant front wall). This document captures the concept design, feasibility analysis, and Phase 1 preparation steps.

## 2. Decision: Phase 2 Feature
Rationale for deferring:
- Arm adds ~350g (28% of Phase 1 rover weight) — significant CoG impact
- Requires 3 additional servo PWM channels (Phase 1 ESP32-S3 has only 2 spare LEDC channels)
- Power budget: 3× MG996R servos draw up to 4.5A peak — exceeds Phase 1 2S LiPo capacity
- Mechanical complexity: arm loads create bending moments at mount point requiring reinforced structure
- Phase 1 learning objectives (LEARN-01 through LEARN-12) should inform arm design decisions

## 3. Arm Concept (Phase 2)

### 3.1 Kinematics
- 3-DOF: shoulder pitch, elbow pitch, wrist roll
- All revolute joints, planar arm (pitch-pitch-roll)
- Shoulder axis: horizontal, mounted on front body wall at 60% height
- Elbow axis: horizontal, at end of upper arm
- Wrist axis: along forearm axis (roll only)

### 3.2 Dimensions (0.4 Scale)
| Parameter | Value |
|-----------|-------|
| Upper arm length | 80mm |
| Forearm length | 70mm |
| Total reach (extended) | ~150mm |
| Stowed length | ~100mm (folded back) |
| Shoulder height (from ground) | ~130mm |
| Max payload at full extension | 50g |

### 3.3 Full Scale Dimensions
| Parameter | Value |
|-----------|-------|
| Upper arm length | 200mm |
| Forearm length | 175mm |
| Total reach (extended) | ~375mm |
| Max payload at full extension | 200g |

### 3.4 Actuators
| Joint | Servo | Torque Required | Servo Torque |
|-------|-------|----------------|-------------|
| Shoulder pitch | MG996R | 5 kg·cm (arm weight × reach) | 10 kg·cm |
| Elbow pitch | MG996R | 2 kg·cm (forearm + payload) | 10 kg·cm |
| Wrist roll | SG90 | 0.3 kg·cm (camera only) | 1.8 kg·cm |

### 3.5 End Effector Options
1. **Camera mount** (primary): USB webcam or ESP32-CAM module for close-up inspection
2. **Simple gripper** (future): 1-DOF servo gripper for picking up small objects
3. **Sensor probe** (future): Temperature/humidity sensor on arm tip

## 4. Weight and CoG Impact

### 4.1 Weight Budget
| Component | Weight |
|-----------|--------|
| Upper arm (printed) | 40g |
| Forearm (printed) | 30g |
| Wrist bracket | 15g |
| 2× MG996R servo | 110g (55g each) |
| 1× SG90 servo | 9g |
| Camera module | 30g |
| Wiring | 20g |
| Fasteners | 10g |
| **Total** | **~264g** |

### 4.2 CoG Shift
- Current Phase 1 CoG: approximately centred (220mm from front)
- With arm stowed: CoG shifts forward ~10mm
- With arm extended: CoG shifts forward ~25mm
- Stability impact: tilt angle reduces from ~56° to ~50° (still safe)
- Phase 2 chassis is wider (650mm vs 260mm), partially compensates

## 5. Electrical Requirements
| Parameter | Value |
|-----------|-------|
| Servo channels | 3 additional PWM (need Jetson or PCA9685) |
| Peak current | 4.5A (all 3 servos stalling simultaneously) |
| Typical current | 1.2A (normal motion) |
| Power source | Phase 2 6S LiPo via dedicated BEC |
| Control bus | I2C PCA9685 (16-channel PWM) or direct Jetson GPIO |

Phase 1 ESP32-S3 cannot support the arm: only 2 spare LEDC channels, and 2S LiPo insufficient for MG996R servos.

## 6. Phase 1 Preparation

### 6.1 Mechanical
- 4× M3 heat-set insert bosses on FL body quadrant front wall
- Pattern: 40mm × 40mm square, centred on front wall, at 60% wall height
- Insert spec: 4.8mm OD × 5.5mm deep (same as all other inserts)
- Wall reinforcement: FL front wall is 4mm thick (adequate for M3 bolts)

### 6.2 Electrical
- Reserve GPIO 3 and GPIO 17 as potential arm servo pins (comment in config.h)
- These won't be used in Phase 1 but are noted for forward compatibility
- Phase 2 will likely use Jetson GPIO or I2C servo driver instead

### 6.3 Software
- Define arm joint message types in rover_msgs (placeholder):
  - ArmJointAngles.msg: shoulder_pitch, elbow_pitch, wrist_roll (float32 each)
  - ArmCommand.msg: mode (stow, extend, track, manual), target_position (Point)
- Arm control node would be a new ROS2 package: `rover_arm`
- Inverse kinematics: analytical solution for 2-DOF planar arm (shoulder + elbow)

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Arm weight destabilises rover | Medium | High | CoG analysis shows acceptable. Add counterweight if needed. |
| MG996R servos overheat | Low | Medium | Duty cycle limit in software. Heat sinks on servo housings. |
| PLA mount point fails under load | Medium | High | Reinforce with aluminium bracket in Phase 2. Phase 1 mount is proof-of-concept. |
| Arm catches on obstacles | Medium | Medium | Software workspace limits. Stow command before driving. |
| Insufficient reach for useful tasks | Low | Low | 150mm reach adequate for camera inspection at 0.4 scale. |

## 8. Recommendations

1. **Phase 1**: Install mount bosses only. No arm hardware.
2. **Phase 2**: Design arm as separate printed sub-assembly. Attach to mount bosses.
3. Start with camera-only end effector. Add gripper later.
4. Use PCA9685 I2C servo driver (not direct GPIO) for arm servos — allows 16 servos from 2 pins.
5. Implement arm stow interlock: arm must be stowed before drive commands accepted.

## Revision History
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-23 | Initial feasibility study |

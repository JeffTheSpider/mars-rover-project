#ifndef STEERING_H
#define STEERING_H

// ============================================================
// Steering control — SG90 servos on LEDC PWM
// 4 steered wheels: FL, FR, RL, RR
// Ackermann geometry from EA-10
// ============================================================

// Servo trim offsets (calibrated per servo, in microseconds)
int16_t servoTrim[4] = {0, 0, 0, 0};  // FL, FR, RL, RR

// Current steering angles (degrees, 0 = straight)
float steerAngle[4] = {0, 0, 0, 0};

// Target steering angles for rate limiting
float steerTarget[4] = {0, 0, 0, 0};

// Last steering update timestamp
unsigned long lastSteerUpdate = 0;

// Servo pin and channel arrays
const uint8_t servoPin[] = {SERVO_FL_PIN, SERVO_FR_PIN, SERVO_RL_PIN, SERVO_RR_PIN};
const uint8_t servoLEDC[] = {SERVO_LEDC_CH_FL, SERVO_LEDC_CH_FR, SERVO_LEDC_CH_RL, SERVO_LEDC_CH_RR};

// Forward declarations
void setServoUS(uint8_t idx, float us);

// Steering modes
enum SteeringMode {
  STEER_ACKERMANN = 0,
  STEER_POINT_TURN = 1,
  STEER_CRAB_WALK = 2,
  STEER_STRAIGHT = 3
};

SteeringMode currentSteerMode = STEER_STRAIGHT;

// Convert microseconds to LEDC duty at 16-bit resolution, 50Hz
// 50Hz period = 20000μs, 16-bit = 65536 steps
// duty = (us / 20000) * 65536
uint16_t usToDuty(float us) {
  return (uint16_t)((us / 20000.0f) * 65536.0f);
}

void setupSteering() {
  // Attach servos to LEDC channels
  ledcAttach(SERVO_FL_PIN, SERVO_PWM_FREQ, SERVO_PWM_RES);
  ledcAttach(SERVO_FR_PIN, SERVO_PWM_FREQ, SERVO_PWM_RES);
  ledcAttach(SERVO_RL_PIN, SERVO_PWM_FREQ, SERVO_PWM_RES);
  ledcAttach(SERVO_RR_PIN, SERVO_PWM_FREQ, SERVO_PWM_RES);

  // Centre all servos
  for (int i = 0; i < 4; i++) {
    setServoUS(i, SERVO_CENTER_US);
  }

  Serial.println("[STEER] Initialised 4 servos (centred)");
}

void setServoUS(uint8_t idx, float us) {
  if (idx >= 4) return;
  us += servoTrim[idx];  // Apply trim first
  us = constrain(us, SERVO_MIN_US, SERVO_MAX_US);  // Then constrain
  uint16_t duty = usToDuty(us);
  ledcWrite(servoPin[idx], duty);
}

void setServoAngle(uint8_t idx, float angleDeg) {
  if (idx >= 4) return;

  // Clamp angle
  angleDeg = constrain(angleDeg, -STEER_MAX_ANGLE, STEER_MAX_ANGLE);

  // Apply dead band
  if (fabsf(angleDeg) < STEER_DEADBAND) angleDeg = 0;

  // Rear servos are mounted inverted (see EA-10 §7.3)
  float servoAngle = angleDeg;
  if (idx == 2 || idx == 3) {  // RL, RR
    servoAngle = -angleDeg;
  }

  // Convert to microseconds
  float us = SERVO_CENTER_US + (servoAngle * SERVO_US_PER_DEG);
  setServoUS(idx, us);

  steerAngle[idx] = angleDeg;
}

// ---- Ackermann Steering (EA-10 §8.1) ----

void applyAckermann(float turnRadiusMM) {
  // Positive = right turn, negative = left turn
  if (fabsf(turnRadiusMM) < MIN_TURN_RADIUS) {
    turnRadiusMM = (turnRadiusMM > 0) ? MIN_TURN_RADIUS : -MIN_TURN_RADIUS;
  }

  float R = fabsf(turnRadiusMM);
  float sign = (turnRadiusMM > 0) ? 1.0f : -1.0f;

  // Inner and outer wheel angles
  float deltaInner = atan2f(L_FM_MM, R - HALF_TRACK_MM) * RAD_TO_DEG;
  float deltaOuter = atan2f(L_FM_MM, R + HALF_TRACK_MM) * RAD_TO_DEG;

  if (sign > 0) {
    // Right turn: right side is inner
    setServoAngle(0, deltaOuter * sign);   // FL (outer front)
    setServoAngle(1, deltaInner * sign);   // FR (inner front)
    setServoAngle(2, -deltaOuter * sign);  // RL (outer rear, opposite)
    setServoAngle(3, -deltaInner * sign);  // RR (inner rear, opposite)
  } else {
    // Left turn: left side is inner
    setServoAngle(0, deltaInner * sign);   // FL (inner front)
    setServoAngle(1, deltaOuter * sign);   // FR (outer front)
    setServoAngle(2, -deltaInner * sign);  // RL (inner rear, opposite)
    setServoAngle(3, -deltaOuter * sign);  // RR (outer rear, opposite)
  }
}

void applyPointTurn(float rotSpeed) {
  // rotSpeed: -100 to +100, positive = clockwise
  // Steer all wheels to max angle for tightest turn
  float angle = STEER_MAX_ANGLE;

  // Front wheels point inward, rear wheels point outward
  if (rotSpeed > 0) {
    // Clockwise
    setServoAngle(0, angle);    // FL right
    setServoAngle(1, angle);    // FR right
    setServoAngle(2, angle);    // RL left (inverted in setServoAngle)
    setServoAngle(3, angle);    // RR left (inverted in setServoAngle)
  } else {
    setServoAngle(0, -angle);
    setServoAngle(1, -angle);
    setServoAngle(2, -angle);
    setServoAngle(3, -angle);
  }

  // Drive left and right sides in opposite directions
  int8_t speed = (int8_t)constrain(abs((int)rotSpeed), 0, 100);
  if (rotSpeed > 0) {
    setDrive(-speed, speed);  // Left back, right forward = clockwise
  } else {
    setDrive(speed, -speed);
  }
}

void applyCrabWalk(float angleDeg) {
  // All steered wheels to same angle
  angleDeg = constrain(angleDeg, -STEER_MAX_ANGLE, STEER_MAX_ANGLE);
  setServoAngle(0, angleDeg);   // FL
  setServoAngle(1, angleDeg);   // FR
  setServoAngle(2, angleDeg);   // RL (rear same direction = crab)
  setServoAngle(3, angleDeg);   // RR
}

void applyStraight() {
  for (int i = 0; i < 4; i++) {
    steerTarget[i] = 0;
    setServoAngle(i, 0);
  }
}

// --- Rate-Limited Steering Update (EA-22 safety) ---
// Call from main loop at MOTOR_UPDATE_MS interval.
// Smoothly interpolates current angles toward targets at STEER_MAX_RATE deg/s.
void updateSteering() {
  unsigned long now = millis();
  if (lastSteerUpdate == 0) {
    lastSteerUpdate = now;
    return;
  }

  float dt = (now - lastSteerUpdate) / 1000.0f;  // seconds
  lastSteerUpdate = now;

  if (dt <= 0 || dt > 0.5f) return;  // Skip if bogus delta

  float maxStep = STEER_MAX_RATE * dt;  // Max degrees this tick

  for (int i = 0; i < 4; i++) {
    float diff = steerTarget[i] - steerAngle[i];
    if (fabsf(diff) > maxStep) {
      // Rate limit: move toward target by maxStep
      diff = (diff > 0) ? maxStep : -maxStep;
    }
    setServoAngle(i, steerAngle[i] + diff);
  }
}

// Set steering target (rate-limited version of setServoAngle)
void setSteerTarget(uint8_t idx, float angleDeg) {
  if (idx >= 4) return;
  angleDeg = constrain(angleDeg, -STEER_MAX_ANGLE, STEER_MAX_ANGLE);
  if (fabsf(angleDeg) < STEER_DEADBAND) angleDeg = 0;
  steerTarget[idx] = angleDeg;
}

#endif // STEERING_H

#ifndef MOTORS_H
#define MOTORS_H

// ============================================================
// Motor control — L298N dual H-bridge driver
// Phase 1: 4 channels (LF, LR, RF, RR)
// LR = left mid+rear in parallel, RR = right mid+rear in parallel
// ============================================================

// Current motor speeds (-100 to +100)
int8_t motorSpeed[4] = {0, 0, 0, 0};  // LF, LR, RF, RR
int8_t motorTarget[4] = {0, 0, 0, 0}; // Target speeds (ramped towards)

// Motor pin arrays for easy iteration
const uint8_t motorPWM[] = {MOTOR_LF_PWM, MOTOR_LR_PWM, MOTOR_RF_PWM, MOTOR_RR_PWM};
const uint8_t motorIN1[] = {MOTOR_LF_IN1, MOTOR_LR_IN1, MOTOR_RF_IN1, MOTOR_RR_IN1};
const uint8_t motorIN2[] = {MOTOR_LF_IN2, MOTOR_LR_IN2, MOTOR_RF_IN2, MOTOR_RR_IN2};
const uint8_t motorLEDC[] = {MOTOR_LEDC_CH_LF, MOTOR_LEDC_CH_LR, MOTOR_LEDC_CH_RF, MOTOR_LEDC_CH_RR};
const int8_t motorTrim[] = {MOTOR_TRIM_LF, MOTOR_TRIM_LR, MOTOR_TRIM_RF, MOTOR_TRIM_RR};

void setupMotors() {
  // Configure LEDC timer for motors
  ledcAttach(MOTOR_LF_PWM, MOTOR_PWM_FREQ, MOTOR_PWM_RES);
  ledcAttach(MOTOR_LR_PWM, MOTOR_PWM_FREQ, MOTOR_PWM_RES);
  ledcAttach(MOTOR_RF_PWM, MOTOR_PWM_FREQ, MOTOR_PWM_RES);
  ledcAttach(MOTOR_RR_PWM, MOTOR_PWM_FREQ, MOTOR_PWM_RES);

  // Configure direction pins
  for (int i = 0; i < 4; i++) {
    pinMode(motorIN1[i], OUTPUT);
    pinMode(motorIN2[i], OUTPUT);
    digitalWrite(motorIN1[i], LOW);
    digitalWrite(motorIN2[i], LOW);
  }

  Serial.println("[MOTOR] Initialised 4 channels");
}

void setMotor(uint8_t idx, int8_t speed) {
  if (idx >= 4) return;

  // Apply per-motor trim for straight-line calibration
  int trimmed = (int)speed + motorTrim[idx];
  speed = (int8_t)constrain(trimmed, -SPEED_LIMIT_PCT, SPEED_LIMIT_PCT);

  // Set direction
  if (speed > 0) {
    digitalWrite(motorIN1[idx], HIGH);
    digitalWrite(motorIN2[idx], LOW);
  } else if (speed < 0) {
    digitalWrite(motorIN1[idx], LOW);
    digitalWrite(motorIN2[idx], HIGH);
  } else {
    // Brake (both LOW = coast, both HIGH = brake)
    digitalWrite(motorIN1[idx], LOW);
    digitalWrite(motorIN2[idx], LOW);
  }

  // Set PWM duty (0-255)
  uint8_t duty = map(abs(speed), 0, 100, 0, 255);
  ledcWrite(motorPWM[idx], duty);

  motorSpeed[idx] = speed;
}

void stopAllMotors() {
  for (int i = 0; i < 4; i++) {
    setMotor(i, 0);
    motorTarget[i] = 0;
  }
}

// Ramp motor speeds towards targets (call at MOTOR_UPDATE_MS rate)
void updateMotors() {
  for (int i = 0; i < 4; i++) {
    if (motorSpeed[i] < motorTarget[i]) {
      int newSpeed = (int)motorSpeed[i] + RAMP_RATE;
      if (newSpeed > motorTarget[i]) newSpeed = motorTarget[i];
      setMotor(i, (int8_t)newSpeed);
    } else if (motorSpeed[i] > motorTarget[i]) {
      int newSpeed = (int)motorSpeed[i] - RAMP_RATE;
      if (newSpeed < motorTarget[i]) newSpeed = motorTarget[i];
      setMotor(i, (int8_t)newSpeed);
    }
  }
}

// Set all motors for driving (speed = -100 to +100)
// Positive = forward
void setDrive(int8_t leftSpeed, int8_t rightSpeed) {
  motorTarget[0] = leftSpeed;   // LF
  motorTarget[1] = leftSpeed;   // LR (mid+rear)
  motorTarget[2] = rightSpeed;  // RF
  motorTarget[3] = rightSpeed;  // RR (mid+rear)
}

// Differential drive from linear + angular velocity
// linear: -100 to +100 (forward/back)
// angular: -100 to +100 (left/right turn)
void setDriveVelocity(int8_t linear, int8_t angular) {
  int left  = linear + angular;
  int right = linear - angular;

  // Normalise if either exceeds ±100
  int maxVal = max(abs(left), abs(right));
  if (maxVal > 100) {
    left  = left * 100 / maxVal;
    right = right * 100 / maxVal;
  }

  setDrive((int8_t)left, (int8_t)right);
}

#endif // MOTORS_H

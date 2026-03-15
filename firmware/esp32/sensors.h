#ifndef SENSORS_H
#define SENSORS_H

// ============================================================
// Sensor reading — battery voltage, encoders (optional)
// Phase 1: ADC battery monitor + 2 wheel encoders
// ============================================================

// Forward declarations
float readBatteryRaw();

// --- Battery ---
float batteryVoltage = 0;
uint8_t batteryPercent = 100;
bool batteryWarning = false;
bool batteryCritical = false;

// ADC smoothing
#define BATT_SAMPLES 10
float battSamples[BATT_SAMPLES];
uint8_t battSampleIdx = 0;
bool battSamplesFull = false;

// --- Encoders ---
volatile int32_t encoderCount[2] = {0, 0};  // W1, W6

void IRAM_ATTR encoderISR_W1() {
  // Simple counting — direction from channel B
  if (digitalRead(ENC_W1_CHB)) {
    encoderCount[0]++;
  } else {
    encoderCount[0]--;
  }
}

void IRAM_ATTR encoderISR_W6() {
  if (digitalRead(ENC_W6_CHB)) {
    encoderCount[1]++;
  } else {
    encoderCount[1]--;
  }
}

void setupSensors() {
  // Battery ADC
  analogReadResolution(12);  // 12-bit ADC (0-4095)
  analogSetAttenuation(ADC_11db);  // Full 0-3.3V range
  pinMode(BATT_ADC_PIN, INPUT);

  // Fill battery samples with initial reading
  float initial = readBatteryRaw();
  for (int i = 0; i < BATT_SAMPLES; i++) {
    battSamples[i] = initial;
  }
  battSamplesFull = true;

  // Encoders (optional — skip if pins not connected)
  pinMode(ENC_W1_CHA, INPUT_PULLUP);
  pinMode(ENC_W1_CHB, INPUT_PULLUP);
  pinMode(ENC_W6_CHA, INPUT_PULLUP);
  pinMode(ENC_W6_CHB, INPUT_PULLUP);

  attachInterrupt(ENC_W1_CHA, encoderISR_W1, RISING);
  attachInterrupt(ENC_W6_CHA, encoderISR_W6, RISING);

  // E-stop button
  pinMode(ESTOP_PIN, INPUT);  // GPIO46 has internal pull-down

  Serial.println("[SENSOR] Initialised (ADC + 2 encoders + E-stop)");
}

float readBatteryRaw() {
  int raw = analogRead(BATT_ADC_PIN);
  float voltage = (raw / 4095.0f) * 3.3f;  // ADC to voltage
  return voltage * BATT_DIVIDER_RATIO;       // Scale up through divider
}

void updateBattery() {
  // Moving average filter
  battSamples[battSampleIdx] = readBatteryRaw();
  battSampleIdx = (battSampleIdx + 1) % BATT_SAMPLES;

  // Calculate average
  float sum = 0;
  for (int i = 0; i < BATT_SAMPLES; i++) {
    sum += battSamples[i];
  }
  batteryVoltage = sum / BATT_SAMPLES;

  // Calculate percentage (linear approximation: 6.4V=0%, 8.4V=100%)
  batteryPercent = constrain(
    (uint8_t)((batteryVoltage - BATT_CUTOFF_V) / (BATT_FULL_V - BATT_CUTOFF_V) * 100),
    0, 100
  );

  // Warnings
  batteryWarning = (batteryVoltage <= BATT_WARN_V);
  batteryCritical = (batteryVoltage <= BATT_CUTOFF_V);

  if (batteryCritical) {
    stopAllMotors();
    Serial.println("[BATT] CRITICAL — motors stopped!");
  } else if (batteryWarning) {
    Serial.println("[BATT] Warning — low voltage");
  }
}

bool isEStopPressed() {
  return digitalRead(ESTOP_PIN) == HIGH;
}

// Get encoder counts and reset (for odometry)
void getAndResetEncoders(int32_t* w1, int32_t* w6) {
  noInterrupts();
  *w1 = encoderCount[0];
  *w6 = encoderCount[1];
  encoderCount[0] = 0;
  encoderCount[1] = 0;
  interrupts();
}

#endif // SENSORS_H

#ifndef LEDS_H
#define LEDS_H

// ============================================================
// LED Status Patterns — Mars Rover Phase 1
//
// Single status LED (GPIO 0) with 5 distinct patterns:
//   1. Idle (not armed):     Slow pulse (1Hz)
//   2. Armed (ready):        Double blink (2 quick flashes + pause)
//   3. Driving (active):     Solid on
//   4. Warning (battery):    Fast blink (4Hz)
//   5. Error (E-stop/stall): SOS pattern
//
// Phase 2 expansion: LED underglow (4× 5mm LEDs through body floor)
// uses separate GPIO pins via body_quadrant.py underglow holes.
//
// Main LED logic is in esp32.ino updateStatusLED() for single
// translation unit pattern. This header provides helper constants
// and the arm/disarm interface.
// ============================================================

// LED pattern IDs (for status reporting over WebSocket)
enum LedPattern {
  LED_IDLE      = 0,  // Slow pulse — not armed
  LED_ARMED     = 1,  // Double blink — armed, no drive command
  LED_DRIVING   = 2,  // Solid on — motors active
  LED_WARNING   = 3,  // Fast blink — battery low or stall
  LED_ERROR     = 4   // SOS — E-stop or critical battery
};

// Get current LED pattern for status reporting
LedPattern getCurrentLedPattern() {
  extern bool estopActive;
  extern bool batteryCritical;
  extern bool batteryWarning;
  extern bool stallDetected;
  extern bool wifiConnected;
  extern bool roverArmed;
  extern int8_t motorTarget[];

  if (estopActive || batteryCritical)  return LED_ERROR;
  if (batteryWarning || stallDetected) return LED_WARNING;
  if (!wifiConnected || !roverArmed)   return LED_IDLE;

  bool motorsActive = (motorTarget[0] != 0 || motorTarget[1] != 0 ||
                        motorTarget[2] != 0 || motorTarget[3] != 0);
  return motorsActive ? LED_DRIVING : LED_ARMED;
}

// Arm/disarm the rover (called from WebSocket command handler)
void armRover() {
  extern bool roverArmed;
  extern bool estopActive;
  extern bool batteryCritical;

  if (estopActive) {
    Serial.println("[ARM] Cannot arm — E-stop active");
    return;
  }
  if (batteryCritical) {
    Serial.println("[ARM] Cannot arm — battery critical");
    return;
  }
  roverArmed = true;
  Serial.println("[ARM] Rover ARMED — motors enabled");
}

void disarmRover() {
  extern bool roverArmed;
  roverArmed = false;
  stopAllMotors();
  Serial.println("[ARM] Rover DISARMED — motors disabled");
}

bool isRoverArmed() {
  extern bool roverArmed;
  return roverArmed;
}

#endif // LEDS_H

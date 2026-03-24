#ifndef OTA_H
#define OTA_H

// ============================================================
// OTA (Over-The-Air) Firmware Update
// Uses ArduinoOTA library for WiFi-based firmware uploads
// Upload: espota.py or arduino-cli upload --port <IP>
// ============================================================

#include <ArduinoOTA.h>

void setupOTA() {
  ArduinoOTA.setHostname(WIFI_HOSTNAME);  // "rover"
  ArduinoOTA.setPort(OTA_PORT);  // From config.h

  ArduinoOTA.onStart([]() {
    String type = (ArduinoOTA.getCommand() == U_FLASH)
      ? "firmware" : "filesystem";
    Serial.printf("[OTA] Start updating %s\n", type.c_str());

    // Stop motors during update
    stopAllMotors();
  });

  ArduinoOTA.onEnd([]() {
    Serial.println("\n[OTA] Update complete — rebooting");
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    if (total > 0) Serial.printf("[OTA] Progress: %u%%\r", progress * 100 / total);
    esp_task_wdt_reset();  // Feed watchdog during long upload
  });

  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("[OTA] Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });

  ArduinoOTA.begin();
  Serial.println("[OTA] Ready (port 3232)");
}

void handleOTA() {
  ArduinoOTA.handle();
}

#endif // OTA_H

---
description: Compile ESP32 firmware and generate upload command
argument-hint: [--upload to attempt serial upload]
allowed-tools: Bash(arduino-cli*), Bash(python*), Bash(cd*), Bash(ls*), Read, Glob, Grep
---

# ESP32 Deploy

Compile the ESP32-S3 firmware and prepare for upload.

## Context
- Board: ESP32-S3 DevKitC-1 N16R8
- FQBN: `esp32:esp32:esp32s3`
- Firmware: `D:/Mars Rover Project/firmware/esp32/esp32.ino`
- Upload: USB (COM port) or OTA (espota.py)

## Arguments: $ARGUMENTS

## Steps

### 1. Pre-Deploy Validation
Run the firmware-validate pipeline first (abbreviated):
```bash
cd "D:/Mars Rover Project"
# Compile
arduino-cli compile --fqbn esp32:esp32:esp32s3 firmware/esp32/esp32.ino
# Quick test
python -m pytest firmware/tests/ -v --tb=short -q
```
- **STOP** if compile fails or tests fail — fix issues first

### 2. Check Version
- Read current version from firmware
- Show what version will be deployed
- Warn if version hasn't been bumped

### 3. Identify Upload Port
```bash
arduino-cli board list
```
- Look for ESP32-S3 on a COM port
- If no board found: remind user to connect via USB and hold BOOT button if needed

### 4. Generate Upload Command
```bash
arduino-cli upload --fqbn esp32:esp32:esp32s3 --port <PORT> firmware/esp32/esp32.ino
```

If `--upload` argument was passed AND a port was found, attempt the upload.
Otherwise, just print the command for the user to run.

### 5. OTA Alternative
If the ESP32 is already running and on WiFi:
```bash
python espota.py -i <ESP32_IP> -p 3232 -f firmware/esp32/build/esp32.esp32.esp32s3/esp32.ino.bin
```
Note: OTA binary is in the build directory after successful compile.

### 6. Post-Deploy Verification
If upload was attempted:
- Monitor serial output for 10 seconds: `arduino-cli monitor --port <PORT> --config baudrate=115200`
- Check for successful boot message
- Verify firmware version in serial output

### 7. Summary
```
=== ESP32 Deploy Report ===
Compile:  PASS (flash: XX%, RAM: XX%)
Tests:    PASS (42/42)
Version:  vX.Y.Z
Port:     COMX / not connected
Upload:   [command to run] / completed successfully
```

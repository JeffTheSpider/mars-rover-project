#ifndef ROVER_WEBSERVER_H
#define ROVER_WEBSERVER_H

#include <WebServer.h>
#include <WebSocketsServer.h>

// Forward declarations
void processCommand(String cmd, int speed, int mode);
extern unsigned long lastCommandTime;
extern bool roverArmed;
extern uint8_t batterySpeedLimit;
extern bool stallDetected;

// ============================================================
// WiFi Web Server + WebSocket for Phase 1 control
// Phone connects to rover's WiFi web UI for manual driving
// ============================================================

WebServer server(WEB_SERVER_PORT);
WebSocketsServer ws(WS_PORT);

bool wsConnected = false;
unsigned long lastWsUpdate = 0;

// --- Web UI (embedded HTML) ---

const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<title>Mars Rover</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, sans-serif; background: #1e1e2e; color: #cdd6f4;
       display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 16px; }
h1 { font-size: 1.5rem; margin-bottom: 12px; color: #f5c2e7; }
.status { display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; justify-content: center; }
.stat { background: #313244; padding: 8px 16px; border-radius: 8px; text-align: center; }
.stat .label { font-size: 0.7rem; color: #6c7086; text-transform: uppercase; }
.stat .value { font-size: 1.2rem; font-weight: bold; }
.controls { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; max-width: 280px; margin-bottom: 16px; }
.btn { background: #45475a; border: none; color: #cdd6f4; font-size: 1.5rem; padding: 24px;
       border-radius: 12px; cursor: pointer; touch-action: manipulation; user-select: none; }
.btn:active { background: #f5c2e7; color: #1e1e2e; }
.btn.stop { background: #f38ba8; color: #1e1e2e; font-size: 1rem; font-weight: bold; }
.btn.stop:active { background: #eba0ac; }
.mode-btns { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; justify-content: center; }
.mode-btn { background: #313244; border: 2px solid #45475a; color: #cdd6f4; padding: 8px 16px;
            border-radius: 8px; cursor: pointer; font-size: 0.9rem; }
.mode-btn.active { border-color: #f5c2e7; background: #45475a; }
.arm-row { display: flex; gap: 8px; margin-bottom: 16px; justify-content: center; }
.arm-btn { padding: 10px 28px; border-radius: 8px; border: 2px solid #45475a; font-size: 1rem;
           font-weight: bold; cursor: pointer; }
.arm-btn.arm { background: #a6e3a1; color: #1e1e2e; border-color: #a6e3a1; }
.arm-btn.disarm { background: #f38ba8; color: #1e1e2e; border-color: #f38ba8; }
#armState { font-size: 0.85rem; align-self: center; padding: 4px 12px; border-radius: 6px; }
#armState.armed { background: #a6e3a1; color: #1e1e2e; }
#armState.disarmed { background: #f38ba8; color: #1e1e2e; }
.slider-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; width: 100%; max-width: 300px; }
.slider-row label { width: 60px; font-size: 0.85rem; }
.slider-row input { flex: 1; }
.slider-row span { width: 40px; text-align: right; font-size: 0.85rem; }
#log { background: #181825; padding: 8px; border-radius: 8px; font-family: monospace;
       font-size: 0.75rem; max-height: 120px; overflow-y: auto; width: 100%; max-width: 400px;
       margin-top: 8px; }
</style>
</head>
<body>
<h1>Mars Rover P1</h1>

<div class="status">
  <div class="stat"><div class="label">Battery</div><div class="value" id="batt">--V</div></div>
  <div class="stat"><div class="label">Percent</div><div class="value" id="pct">--%</div></div>
  <div class="stat"><div class="label">Speed L</div><div class="value" id="spdL">0</div></div>
  <div class="stat"><div class="label">Speed R</div><div class="value" id="spdR">0</div></div>
  <div class="stat"><div class="label">Limit</div><div class="value" id="limit">100%</div></div>
  <div class="stat"><div class="label">Stall</div><div class="value" id="stall">--</div></div>
</div>

<div class="mode-btns">
  <button class="mode-btn active" onclick="setMode(0)">Ackermann</button>
  <button class="mode-btn" onclick="setMode(1)">Point Turn</button>
  <button class="mode-btn" onclick="setMode(2)">Crab Walk</button>
</div>

<div class="arm-row">
  <button class="arm-btn arm" onclick="sendArm('arm')">ARM</button>
  <span id="armState" class="disarmed">DISARMED</span>
  <button class="arm-btn disarm" onclick="sendArm('disarm')">DISARM</button>
</div>

<div class="slider-row">
  <label>Speed</label>
  <input type="range" id="speedSlider" min="10" max="100" value="50">
  <span id="speedVal">50%</span>
</div>

<div class="controls">
  <button class="btn" ontouchstart="drive('fl')" ontouchend="drive('stop')"
          onmousedown="drive('fl')" onmouseup="drive('stop')">&#8598;</button>
  <button class="btn" ontouchstart="drive('fwd')" ontouchend="drive('stop')"
          onmousedown="drive('fwd')" onmouseup="drive('stop')">&#8593;</button>
  <button class="btn" ontouchstart="drive('fr')" ontouchend="drive('stop')"
          onmousedown="drive('fr')" onmouseup="drive('stop')">&#8599;</button>
  <button class="btn" ontouchstart="drive('left')" ontouchend="drive('stop')"
          onmousedown="drive('left')" onmouseup="drive('stop')">&#8592;</button>
  <button class="btn stop" onclick="drive('stop')">STOP</button>
  <button class="btn" ontouchstart="drive('right')" ontouchend="drive('stop')"
          onmousedown="drive('right')" onmouseup="drive('stop')">&#8594;</button>
  <button class="btn" ontouchstart="drive('bl')" ontouchend="drive('stop')"
          onmousedown="drive('bl')" onmouseup="drive('stop')">&#8601;</button>
  <button class="btn" ontouchstart="drive('rev')" ontouchend="drive('stop')"
          onmousedown="drive('rev')" onmouseup="drive('stop')">&#8595;</button>
  <button class="btn" ontouchstart="drive('br')" ontouchend="drive('stop')"
          onmousedown="drive('br')" onmouseup="drive('stop')">&#8600;</button>
</div>

<div id="log"></div>

<script>
let ws;
let mode = 0;
let speed = 50;

function connect() {
  ws = new WebSocket('ws://' + location.hostname + ':81');
  ws.onopen = () => log('Connected');
  ws.onclose = () => { log('Disconnected'); setTimeout(connect, 2000); };
  ws.onmessage = (e) => {
    try {
      const d = JSON.parse(e.data);
      if (d.batt !== undefined) {
        document.getElementById('batt').textContent = d.batt.toFixed(1) + 'V';
        document.getElementById('pct').textContent = d.pct + '%';
        document.getElementById('spdL').textContent = d.ml;
        document.getElementById('spdR').textContent = d.mr;
        if (d.armed !== undefined) {
          var el = document.getElementById('armState');
          el.textContent = d.armed ? 'ARMED' : 'DISARMED';
          el.className = d.armed ? 'armed' : 'disarmed';
        }
        if (d.limit !== undefined) {
          document.getElementById('limit').textContent = d.limit + '%';
        }
        if (d.stall !== undefined) {
          var s = document.getElementById('stall');
          s.textContent = d.stall ? 'YES' : 'OK';
          s.style.color = d.stall ? '#f38ba8' : '#a6e3a1';
        }
      }
    } catch(ex) {}
  };
}

function drive(dir) {
  if (ws && ws.readyState === 1) {
    ws.send(JSON.stringify({cmd: dir, speed: speed, mode: mode}));
  }
}

function sendArm(action) {
  if (ws && ws.readyState === 1) {
    ws.send(JSON.stringify({cmd: action}));
  }
}

function setMode(m) {
  mode = m;
  document.querySelectorAll('.mode-btn').forEach((b, i) => {
    b.classList.toggle('active', i === m);
  });
  drive('stop');
}

document.getElementById('speedSlider').oninput = function() {
  speed = parseInt(this.value);
  document.getElementById('speedVal').textContent = speed + '%';
};

function log(msg) {
  var el = document.getElementById('log');
  var t = new Date().toLocaleTimeString();
  var line = document.createElement('div');
  line.textContent = t + ' ' + msg;
  el.appendChild(line);
  if (el.children.length > 200) el.removeChild(el.firstChild);
  el.scrollTop = el.scrollHeight;
}

connect();
</script>
</body>
</html>
)rawliteral";

// --- HTTP Routes ---

void handleRoot() {
  server.send(200, "text/html", INDEX_HTML);
}

void handleStatus() {
  char buf[384];
  int len = snprintf(buf, sizeof(buf),
    "{\"version\":\"%s\",\"battery\":%.2f,\"percent\":%d,\"motors\":[%d,%d,%d,%d],"
    "\"steering\":[%.1f,%.1f,%.1f,%.1f],\"estop\":%s,\"armed\":%s,"
    "\"limit\":%d,\"stall\":%s,\"uptime\":%lu}",
    FW_VERSION, batteryVoltage, batteryPercent,
    motorSpeed[0], motorSpeed[1], motorSpeed[2], motorSpeed[3],
    steerAngle[0], steerAngle[1], steerAngle[2], steerAngle[3],
    isEStopPressed() ? "true" : "false",
    roverArmed ? "true" : "false",
    (int)batterySpeedLimit,
    stallDetected ? "true" : "false",
    millis() / 1000
  );
  if (len >= (int)sizeof(buf)) {
    server.send(500, "application/json", "{\"error\":\"buffer overflow\"}");
    return;
  }
  server.send(200, "application/json", buf);
}

void handleNotFound() {
  server.send(404, "text/plain", "Not Found");
}

// --- WebSocket Events ---

void onWebSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_CONNECTED:
      wsConnected = true;
      Serial.printf("[WS] Client %u connected\n", num);
      break;

    case WStype_DISCONNECTED:
      wsConnected = false;
      stopAllMotors();
      Serial.printf("[WS] Client %u disconnected — motors stopped\n", num);
      break;

    case WStype_TEXT: {
      // Parse JSON command: {"cmd":"fwd","speed":50,"mode":0}
      // Simple manual parsing (no ArduinoJson dependency)
      String msg = String((char*)payload);

      // Extract command
      int cmdIdx = msg.indexOf("\"cmd\":\"");
      if (cmdIdx < 0) break;
      String cmd = msg.substring(cmdIdx + 7, msg.indexOf("\"", cmdIdx + 7));

      // Extract speed
      int spdIdx = msg.indexOf("\"speed\":");
      int spd = 50;
      if (spdIdx >= 0) {
        spd = msg.substring(spdIdx + 8).toInt();
      }

      // Extract mode
      int modeIdx = msg.indexOf("\"mode\":");
      int driveMode = 0;
      if (modeIdx >= 0) {
        driveMode = msg.substring(modeIdx + 7).toInt();
      }

      processCommand(cmd, spd, driveMode);
      break;
    }

    default:
      break;
  }
}

// --- Command Processing ---

void processCommand(String cmd, int speed, int mode) {
  lastCommandTime = millis();

  // Handle ARM/DISARM commands (EA-22 safety)
  if (cmd == "arm") {
    armRover();  // from leds.h
    return;
  }
  if (cmd == "disarm") {
    disarmRover();  // from leds.h
    return;
  }

  // Motor commands require armed state
  if (ARM_REQUIRED && !roverArmed) {
    return;  // Silently ignore drive commands when not armed
  }

  speed = constrain(speed, 0, 100);

  // Apply battery-based speed limiting (EA-22 FR-06)
  speed = (int)(speed * batterySpeedLimit / 100);

  if (cmd == "stop") {
    setDrive(0, 0);
    applyStraight();
    return;
  }

  if (mode == 1) {
    // Point turn mode
    if (cmd == "left") {
      applyPointTurn(-speed);
    } else if (cmd == "right") {
      applyPointTurn(speed);
    } else {
      setDrive(0, 0);
      applyStraight();
    }
    return;
  }

  if (mode == 2) {
    // Crab walk mode
    if (cmd == "left") {
      applyCrabWalk(-STEER_MAX_ANGLE);
      setDrive(speed, speed);
    } else if (cmd == "right") {
      applyCrabWalk(STEER_MAX_ANGLE);
      setDrive(speed, speed);
    } else if (cmd == "fwd") {
      applyStraight();
      setDrive(speed, speed);
    } else if (cmd == "rev") {
      applyStraight();
      setDrive(-speed, -speed);
    } else {
      setDrive(0, 0);
    }
    return;
  }

  // Ackermann mode (default) — radii and speed ratios from config.h
  int innerWide  = (int)(speed * TURN_INNER_SPEED_WIDE);
  int innerTight = (int)(speed * TURN_INNER_SPEED_TIGHT);

  if (cmd == "fwd") {
    applyStraight();
    setDrive(speed, speed);
  } else if (cmd == "rev") {
    applyStraight();
    setDrive(-speed, -speed);
  } else if (cmd == "left") {
    applyAckermann(-TURN_RADIUS_WIDE_MM);
    setDrive(innerWide, speed);
  } else if (cmd == "right") {
    applyAckermann(TURN_RADIUS_WIDE_MM);
    setDrive(speed, innerWide);
  } else if (cmd == "fl") {
    applyAckermann(-TURN_RADIUS_TIGHT_MM);
    setDrive(innerTight, speed);
  } else if (cmd == "fr") {
    applyAckermann(TURN_RADIUS_TIGHT_MM);
    setDrive(speed, innerTight);
  } else if (cmd == "bl") {
    applyAckermann(-TURN_RADIUS_WIDE_MM);
    setDrive(-innerWide, -speed);
  } else if (cmd == "br") {
    applyAckermann(TURN_RADIUS_WIDE_MM);
    setDrive(-speed, -innerWide);
  }
}

// --- Send Status via WebSocket ---

void sendWsStatus() {
  if (!wsConnected) return;

  char buf[256];
  snprintf(buf, sizeof(buf),
    "{\"batt\":%.1f,\"pct\":%d,\"ml\":%d,\"mr\":%d,\"armed\":%s,\"limit\":%d,\"stall\":%s,\"estop\":%s}",
    batteryVoltage, batteryPercent,
    motorSpeed[0], motorSpeed[2],
    roverArmed ? "true" : "false",
    (int)batterySpeedLimit,
    stallDetected ? "true" : "false",
    isEStopPressed() ? "true" : "false"
  );
  ws.broadcastTXT(buf);
}

// --- Setup ---

void setupWebServer() {
  server.on("/", handleRoot);
  server.on("/api/status", handleStatus);
  server.onNotFound(handleNotFound);
  server.begin();

  ws.begin();
  ws.onEvent(onWebSocketEvent);

  Serial.printf("[WEB] Server on port %d, WebSocket on port %d\n",
    WEB_SERVER_PORT, WS_PORT);
}

void handleWeb() {
  server.handleClient();
  ws.loop();

  // Periodic status broadcast
  if (millis() - lastWsUpdate >= WS_UPDATE_MS) {
    sendWsStatus();
    lastWsUpdate = millis();
  }
}

#endif // ROVER_WEBSERVER_H

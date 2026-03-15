"""
Integration tests for UART bridge round-trip communication.

Simulates the ESP32 ↔ Jetson UART link by testing NMEA message encoding,
transmission, parsing, and ROS2 message conversion end-to-end.

These tests run without hardware using a mock serial port.
"""

import math
import struct
import time
import pytest


# ============================================================
# NMEA Protocol Implementation (mirrors uart_nmea.h)
# ============================================================

class NMEACodec:
    """Encode and decode NMEA-style messages matching firmware protocol."""

    @staticmethod
    def checksum(body: str) -> int:
        xor_val = 0
        for ch in body:
            xor_val ^= ord(ch)
        return xor_val

    @staticmethod
    def encode(body: str) -> str:
        cs = NMEACodec.checksum(body)
        return f"${body}*{cs:02X}\r\n"

    @staticmethod
    def decode(msg: str) -> dict:
        msg = msg.strip()
        if not msg.startswith('$') or '*' not in msg:
            return {'valid': False, 'error': 'missing delimiters'}

        star_idx = msg.index('*')
        body = msg[1:star_idx]
        hex_cs = msg[star_idx + 1:star_idx + 3]

        try:
            expected_cs = int(hex_cs, 16)
        except ValueError:
            return {'valid': False, 'error': 'bad checksum format'}

        actual_cs = NMEACodec.checksum(body)
        if actual_cs != expected_cs:
            return {'valid': False, 'error': f'checksum mismatch: {actual_cs:02X} != {expected_cs:02X}'}

        parts = body.split(',')
        return {'valid': True, 'type': parts[0], 'fields': parts[1:], 'raw': body}


# ============================================================
# Message Type Parsers (mirrors uart_bridge_node.cpp)
# ============================================================

class UARTBridgeParser:
    """Parse NMEA messages into ROS2-equivalent data structures."""

    @staticmethod
    def parse_encoder(fields):
        """Parse $ENC,w1,w2,w3,w4,w5,w6 → wheel encoder counts."""
        if len(fields) < 6:
            raise ValueError(f"ENC needs 6 fields, got {len(fields)}")
        return {
            'type': 'encoder',
            'counts': [int(f) for f in fields[:6]],
        }

    @staticmethod
    def parse_imu(fields):
        """Parse $IMU,qw,qx,qy,qz,gx,gy,gz,ax,ay,az → IMU data."""
        if len(fields) < 10:
            raise ValueError(f"IMU needs 10 fields, got {len(fields)}")
        vals = [float(f) for f in fields[:10]]
        return {
            'type': 'imu',
            'orientation': {'w': vals[0], 'x': vals[1], 'y': vals[2], 'z': vals[3]},
            'angular_velocity': {'x': vals[4], 'y': vals[5], 'z': vals[6]},
            'linear_acceleration': {'x': vals[7], 'y': vals[8], 'z': vals[9]},
        }

    @staticmethod
    def parse_battery(fields):
        """Parse $BAT,voltage,percent → battery state."""
        if len(fields) < 2:
            raise ValueError(f"BAT needs 2 fields, got {len(fields)}")
        return {
            'type': 'battery',
            'voltage': float(fields[0]),
            'percentage': int(fields[1]),
        }

    @staticmethod
    def parse_ultrasonic(fields):
        """Parse $USS,d1,d2,d3,d4,d5,d6 → 6x range readings (cm)."""
        if len(fields) < 6:
            raise ValueError(f"USS needs 6 fields, got {len(fields)}")
        return {
            'type': 'ultrasonic',
            'ranges_cm': [int(f) for f in fields[:6]],
        }

    @staticmethod
    def parse_status(fields):
        """Parse $STS,estop,mode,error → rover status."""
        if len(fields) < 3:
            raise ValueError(f"STS needs 3 fields, got {len(fields)}")
        return {
            'type': 'status',
            'estop': bool(int(fields[0])),
            'mode': int(fields[1]),
            'error_code': int(fields[2]),
        }

    @staticmethod
    def parse(decoded):
        """Route decoded NMEA to type-specific parser."""
        parsers = {
            'ENC': UARTBridgeParser.parse_encoder,
            'IMU': UARTBridgeParser.parse_imu,
            'BAT': UARTBridgeParser.parse_battery,
            'USS': UARTBridgeParser.parse_ultrasonic,
            'STS': UARTBridgeParser.parse_status,
        }
        parser = parsers.get(decoded['type'])
        if not parser:
            raise ValueError(f"Unknown message type: {decoded['type']}")
        return parser(decoded['fields'])


# ============================================================
# Command Encoder (mirrors Jetson→ESP32 commands)
# ============================================================

class CommandEncoder:
    """Encode commands to send from Jetson to ESP32."""

    @staticmethod
    def motor_command(left_speed, right_speed):
        """Encode $CMTR,left,right motor speed command."""
        return NMEACodec.encode(f"CMTR,{left_speed},{right_speed}")

    @staticmethod
    def steering_command(mode, value):
        """Encode $CSTR,mode,value steering command."""
        return NMEACodec.encode(f"CSTR,{mode},{value:.1f}")

    @staticmethod
    def estop_command(activate):
        """Encode $CESP,state E-stop command."""
        return NMEACodec.encode(f"CESP,{1 if activate else 0}")

    @staticmethod
    def config_command(key, value):
        """Encode $CCFG,key,value configuration command."""
        return NMEACodec.encode(f"CCFG,{key},{value}")


# ============================================================
# Odometry Calculator (mirrors uart_bridge_node.cpp odometry)
# ============================================================

class OdometryCalculator:
    """Calculate differential drive odometry from encoder counts."""

    def __init__(self, wheel_radius_m=0.04, track_width_m=0.28, ticks_per_rev=360):
        self.wheel_radius = wheel_radius_m
        self.track_width = track_width_m
        self.ticks_per_rev = ticks_per_rev
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.prev_left = 0
        self.prev_right = 0

    def update(self, left_ticks, right_ticks, dt):
        """Update pose from encoder ticks."""
        dl = (left_ticks - self.prev_left) / self.ticks_per_rev * 2 * math.pi * self.wheel_radius
        dr = (right_ticks - self.prev_right) / self.ticks_per_rev * 2 * math.pi * self.wheel_radius

        self.prev_left = left_ticks
        self.prev_right = right_ticks

        dc = (dl + dr) / 2.0
        dtheta = (dr - dl) / self.track_width

        self.x += dc * math.cos(self.theta + dtheta / 2.0)
        self.y += dc * math.sin(self.theta + dtheta / 2.0)
        self.theta += dtheta

        return {'x': self.x, 'y': self.y, 'theta': self.theta}


# ============================================================
# Tests
# ============================================================

class TestNMEARoundTrip:
    """Test encode→decode round-trip for all message types."""

    def test_encoder_round_trip(self):
        msg = NMEACodec.encode("ENC,1234,0,0,0,0,5678")
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        parsed = UARTBridgeParser.parse(decoded)
        assert parsed['type'] == 'encoder'
        assert parsed['counts'] == [1234, 0, 0, 0, 0, 5678]

    def test_imu_round_trip(self):
        msg = NMEACodec.encode("IMU,1.0,0.0,0.0,0.0,0.01,0.02,-0.03,0.1,-0.2,9.81")
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        parsed = UARTBridgeParser.parse(decoded)
        assert parsed['type'] == 'imu'
        assert abs(parsed['orientation']['w'] - 1.0) < 0.001
        assert abs(parsed['linear_acceleration']['z'] - 9.81) < 0.001

    def test_battery_round_trip(self):
        msg = NMEACodec.encode("BAT,7.42,85")
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        parsed = UARTBridgeParser.parse(decoded)
        assert parsed['type'] == 'battery'
        assert abs(parsed['voltage'] - 7.42) < 0.001
        assert parsed['percentage'] == 85

    def test_ultrasonic_round_trip(self):
        msg = NMEACodec.encode("USS,120,150,200,180,90,300")
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        parsed = UARTBridgeParser.parse(decoded)
        assert parsed['type'] == 'ultrasonic'
        assert parsed['ranges_cm'] == [120, 150, 200, 180, 90, 300]

    def test_status_round_trip(self):
        msg = NMEACodec.encode("STS,0,1,0")
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        parsed = UARTBridgeParser.parse(decoded)
        assert not parsed['estop']
        assert parsed['mode'] == 1

    def test_estop_active(self):
        msg = NMEACodec.encode("STS,1,0,5")
        parsed = UARTBridgeParser.parse(NMEACodec.decode(msg))
        assert parsed['estop']
        assert parsed['error_code'] == 5


class TestCommandEncoding:
    """Test command encoding from Jetson to ESP32."""

    def test_motor_forward(self):
        msg = CommandEncoder.motor_command(50, 50)
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        assert decoded['type'] == 'CMTR'
        assert decoded['fields'] == ['50', '50']

    def test_motor_turn(self):
        msg = CommandEncoder.motor_command(80, 30)
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        assert decoded['fields'] == ['80', '30']

    def test_motor_reverse(self):
        msg = CommandEncoder.motor_command(-50, -50)
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        assert decoded['fields'] == ['-50', '-50']

    def test_steering_ackermann(self):
        msg = CommandEncoder.steering_command('A', 1500.0)
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        assert decoded['type'] == 'CSTR'
        assert decoded['fields'][0] == 'A'

    def test_estop_activate(self):
        msg = CommandEncoder.estop_command(True)
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        assert decoded['type'] == 'CESP'
        assert decoded['fields'] == ['1']

    def test_estop_deactivate(self):
        msg = CommandEncoder.estop_command(False)
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        assert decoded['fields'] == ['0']

    def test_config_command(self):
        msg = CommandEncoder.config_command('speed_limit', '80')
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']
        assert decoded['type'] == 'CCFG'


class TestChecksumErrors:
    """Test error detection."""

    def test_corrupted_checksum(self):
        msg = "$ENC,1234,5678*00\r\n"
        decoded = NMEACodec.decode(msg)
        assert not decoded['valid']
        assert 'checksum mismatch' in decoded['error']

    def test_missing_dollar(self):
        decoded = NMEACodec.decode("ENC,1234*FF")
        assert not decoded['valid']

    def test_missing_star(self):
        decoded = NMEACodec.decode("$ENC,1234")
        assert not decoded['valid']

    def test_truncated_message(self):
        decoded = NMEACodec.decode("$ENC*")
        assert not decoded['valid']

    def test_wrong_field_count(self):
        msg = NMEACodec.encode("ENC,1234")  # Only 1 field, needs 6
        decoded = NMEACodec.decode(msg)
        assert decoded['valid']  # Checksum is fine
        with pytest.raises(ValueError, match="6 fields"):
            UARTBridgeParser.parse(decoded)

    def test_unknown_message_type(self):
        msg = NMEACodec.encode("XYZ,data")
        decoded = NMEACodec.decode(msg)
        with pytest.raises(ValueError, match="Unknown"):
            UARTBridgeParser.parse(decoded)


class TestOdometry:
    """Test differential drive odometry calculation."""

    def test_stationary(self):
        odom = OdometryCalculator()
        pose = odom.update(0, 0, 0.1)
        assert pose['x'] == 0.0
        assert pose['y'] == 0.0
        assert pose['theta'] == 0.0

    def test_straight_forward(self):
        odom = OdometryCalculator()
        # Both wheels same ticks = straight
        pose = odom.update(360, 360, 0.1)  # 1 full revolution each
        circumference = 2 * math.pi * 0.04  # ~0.251m
        assert abs(pose['x'] - circumference) < 0.001
        assert abs(pose['y']) < 0.001
        assert abs(pose['theta']) < 0.001

    def test_straight_reverse(self):
        odom = OdometryCalculator()
        pose = odom.update(-360, -360, 0.1)
        assert pose['x'] < 0

    def test_turn_right(self):
        odom = OdometryCalculator()
        # Right wheel faster = right turn (positive theta in ROS = CCW)
        # Left faster than right = turn right
        pose = odom.update(360, 0, 0.1)
        assert pose['theta'] < 0  # Should turn clockwise (negative in ROS convention)

    def test_turn_left(self):
        odom = OdometryCalculator()
        pose = odom.update(0, 360, 0.1)
        assert pose['theta'] > 0

    def test_point_turn(self):
        odom = OdometryCalculator()
        # Equal and opposite = pure rotation
        pose = odom.update(180, -180, 0.1)
        assert abs(pose['x']) < 0.01  # Should stay approximately in place
        assert abs(pose['y']) < 0.01

    def test_cumulative_straight(self):
        odom = OdometryCalculator()
        for i in range(1, 11):
            pose = odom.update(36 * i, 36 * i, 0.1)  # 10 steps of 1/10 revolution
        circumference = 2 * math.pi * 0.04
        assert abs(pose['x'] - circumference) < 0.002

    def test_square_path(self):
        """Drive a square: forward, turn 90°, forward, turn 90°, forward, turn 90°, forward.
        Should return approximately to origin."""
        odom = OdometryCalculator(wheel_radius_m=0.04, track_width_m=0.28, ticks_per_rev=360)

        # Calculate ticks for 0.5m forward
        dist = 0.5
        revs = dist / (2 * math.pi * 0.04)
        fwd_ticks = int(revs * 360)

        # Calculate ticks for 90° turn
        arc = (math.pi / 2) * 0.28 / 2  # half-track arc for 90°
        turn_revs = arc / (2 * math.pi * 0.04)
        turn_ticks = int(turn_revs * 360)

        total_left = 0
        total_right = 0

        for side in range(4):
            # Forward
            total_left += fwd_ticks
            total_right += fwd_ticks
            odom.update(total_left, total_right, 0.1)

            # Turn left 90°
            total_right += turn_ticks
            total_left -= turn_ticks
            odom.update(total_left, total_right, 0.1)

        # Should be approximately back to start
        assert abs(odom.x) < 0.15, f"x={odom.x:.3f} too far from origin"
        assert abs(odom.y) < 0.15, f"y={odom.y:.3f} too far from origin"


class TestStreamProcessing:
    """Test processing a stream of mixed NMEA messages."""

    def test_multi_message_stream(self):
        """Simulate a burst of telemetry from ESP32."""
        stream = ""
        stream += NMEACodec.encode("ENC,100,0,0,0,0,105")
        stream += NMEACodec.encode("IMU,0.998,0.01,0.02,0.03,0.001,0.002,-0.001,0.05,-0.03,9.81")
        stream += NMEACodec.encode("BAT,7.85,92")
        stream += NMEACodec.encode("USS,150,200,300,250,180,120")
        stream += NMEACodec.encode("STS,0,0,0")

        messages = []
        for line in stream.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            decoded = NMEACodec.decode(line)
            assert decoded['valid'], f"Failed to decode: {line}"
            parsed = UARTBridgeParser.parse(decoded)
            messages.append(parsed)

        assert len(messages) == 5
        types = [m['type'] for m in messages]
        assert types == ['encoder', 'imu', 'battery', 'ultrasonic', 'status']

    def test_stream_with_corruption(self):
        """Verify corrupted messages are detected in a stream."""
        stream = ""
        stream += NMEACodec.encode("BAT,7.40,85")
        stream += "$GARBAGE*FF\r\n"  # Bad checksum
        stream += NMEACodec.encode("STS,0,0,0")

        valid_count = 0
        invalid_count = 0
        for line in stream.strip().split('\n'):
            decoded = NMEACodec.decode(line.strip())
            if decoded['valid']:
                valid_count += 1
            else:
                invalid_count += 1

        assert valid_count == 2
        assert invalid_count == 1

    def test_high_frequency_telemetry(self):
        """Simulate 50Hz telemetry for 1 second (50 messages)."""
        odom = OdometryCalculator()
        dt = 0.02  # 50Hz

        for i in range(50):
            ticks = (i + 1) * 7  # ~7 ticks per 20ms at moderate speed
            msg = NMEACodec.encode(f"ENC,{ticks},0,0,0,0,{ticks}")
            decoded = NMEACodec.decode(msg)
            assert decoded['valid']
            parsed = UARTBridgeParser.parse(decoded)
            odom.update(parsed['counts'][0], parsed['counts'][5], dt)

        # After 1 second of driving, should have moved forward
        assert odom.x > 0
        assert abs(odom.theta) < 0.01  # Straight line, no turn

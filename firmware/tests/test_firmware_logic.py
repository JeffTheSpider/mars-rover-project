"""
Host-based unit tests for Mars Rover ESP32 firmware logic.

Tests pure math/logic functions extracted from firmware headers.
These run on the dev PC (no ESP32 needed) to catch calculation bugs
before flashing.

Covers: NMEA checksums, Ackermann geometry, battery SoC, servo math.
"""

import math
import struct
import pytest

# ============================================================
# Constants from config.h (0.4 scale prototype)
# ============================================================
WHEELBASE_MM = 360.0
TRACK_WIDTH_MM = 280.0
HALF_TRACK_MM = 140.0
L_FM_MM = 180.0  # front-to-middle axle
MIN_TURN_RADIUS = 397.0
STEER_MAX_ANGLE = 35.0
STEER_DEADBAND = 1.0

SERVO_MIN_US = 500
SERVO_MAX_US = 2400
SERVO_CENTER_US = 1500
SERVO_US_PER_DEG = 11.11

BATT_CELLS = 2
BATT_FULL_V = 8.4
BATT_NOMINAL_V = 7.4
BATT_WARN_V = 7.0
BATT_CUTOFF_V = 6.4
BATT_DIVIDER_RATIO = 3.128


# ============================================================
# NMEA Checksum (from uart_nmea.h)
# ============================================================

def nmea_checksum(msg: str) -> int:
    """XOR of all bytes between $ and * (exclusive)."""
    xor_val = 0
    # Skip the leading $
    for ch in msg[1:]:
        if ch == '*':
            break
        xor_val ^= ord(ch)
    return xor_val


def make_nmea(body: str) -> str:
    """Build a complete NMEA sentence: $body*XX"""
    msg = f"${body}*00"
    cs = nmea_checksum(msg)
    return f"${body}*{cs:02X}"


def verify_nmea(msg: str) -> bool:
    """Verify checksum of a complete NMEA sentence."""
    star_idx = msg.index('*')
    hex_str = msg[star_idx + 1:star_idx + 3]
    expected = int(hex_str, 16)
    return nmea_checksum(msg) == expected


class TestNMEAChecksum:
    def test_simple_message(self):
        msg = make_nmea("ENC,1234,5678")
        assert msg.startswith("$ENC,1234,5678*")
        assert verify_nmea(msg)

    def test_empty_body(self):
        msg = make_nmea("")
        assert verify_nmea(msg)

    def test_known_checksum(self):
        # Manually calculate: E^N^C = 0x45^0x4E^0x43 = 0x48
        msg = "$ENC*48"
        assert verify_nmea(msg)

    def test_bad_checksum(self):
        assert not verify_nmea("$ENC,1234*00")

    def test_all_command_types(self):
        """Verify round-trip for all firmware message types."""
        bodies = [
            "ENC,100,0,0,0,0,200",
            "IMU,1.0,0.0,0.0,0.0,0.01,0.02,0.03,0.1,0.2,9.8",
            "BAT,7.40,85",
            "USS,120,130,140,150,160,170",
            "STS,0,1,0",
            "CMTR,50,-50",
            "CSTR,A,1500.0",
        ]
        for body in bodies:
            msg = make_nmea(body)
            assert verify_nmea(msg), f"Checksum failed for: {body}"

    def test_checksum_is_two_hex_chars(self):
        msg = make_nmea("TEST")
        star_idx = msg.index('*')
        cs_str = msg[star_idx + 1:]
        assert len(cs_str) == 2
        int(cs_str, 16)  # Should not raise

    def test_special_chars_in_body(self):
        msg = make_nmea("DATA,-1.5,+2.3,0.0")
        assert verify_nmea(msg)


# ============================================================
# Ackermann Steering Geometry (from steering.h, EA-10)
# ============================================================

def ackermann_angles(turn_radius_mm: float):
    """
    Compute inner and outer wheel angles for Ackermann steering.
    Returns (fl_deg, fr_deg, rl_deg, rr_deg).
    Positive radius = right turn.
    """
    if abs(turn_radius_mm) < MIN_TURN_RADIUS:
        turn_radius_mm = MIN_TURN_RADIUS if turn_radius_mm > 0 else -MIN_TURN_RADIUS

    R = abs(turn_radius_mm)
    sign = 1.0 if turn_radius_mm > 0 else -1.0

    delta_inner = math.degrees(math.atan2(L_FM_MM, R - HALF_TRACK_MM))
    delta_outer = math.degrees(math.atan2(L_FM_MM, R + HALF_TRACK_MM))

    if sign > 0:
        # Right turn: right is inner
        fl = delta_outer * sign
        fr = delta_inner * sign
        rl = -delta_outer * sign
        rr = -delta_inner * sign
    else:
        # Left turn: left is inner
        fl = delta_inner * sign
        fr = delta_outer * sign
        rl = -delta_inner * sign
        rr = -delta_outer * sign

    return fl, fr, rl, rr


class TestAckermannSteering:
    def test_right_turn_inner_greater_than_outer(self):
        """Inner wheel angle must be larger than outer (Ackermann principle)."""
        fl, fr, rl, rr = ackermann_angles(1000.0)
        assert abs(fr) > abs(fl), "Inner angle (FR) must be greater for right turn"

    def test_left_turn_inner_greater_than_outer(self):
        fl, fr, rl, rr = ackermann_angles(-1000.0)
        assert abs(fl) > abs(fr), "Inner angle (FL) must be greater for left turn"

    def test_symmetry(self):
        """Left and right turns should be mirror images."""
        fl_r, fr_r, rl_r, rr_r = ackermann_angles(1000.0)
        fl_l, fr_l, rl_l, rr_l = ackermann_angles(-1000.0)
        assert abs(fl_r - (-fr_l)) < 0.01
        assert abs(fr_r - (-fl_l)) < 0.01

    def test_minimum_turn_radius_clamped(self):
        """Radius below MIN_TURN_RADIUS should be clamped."""
        angles_min = ackermann_angles(MIN_TURN_RADIUS)
        angles_small = ackermann_angles(100.0)  # Way below minimum
        assert angles_min == angles_small

    def test_large_radius_small_angles(self):
        """Very large radius should produce very small steering angles."""
        fl, fr, rl, rr = ackermann_angles(10000.0)
        for a in [fl, fr, rl, rr]:
            assert abs(a) < 5.0, f"Angle {a} too large for R=10000mm"

    def test_rear_wheels_opposite_direction(self):
        """Rear wheels steer opposite to front for 4-wheel steering."""
        fl, fr, rl, rr = ackermann_angles(1000.0)
        assert fl * rl < 0, "FL and RL should be opposite sign"
        assert fr * rr < 0, "FR and RR should be opposite sign"

    def test_angles_within_servo_limits(self):
        """All angles must be within STEER_MAX_ANGLE at min radius."""
        fl, fr, rl, rr = ackermann_angles(MIN_TURN_RADIUS)
        for a in [fl, fr, rl, rr]:
            assert abs(a) <= STEER_MAX_ANGLE + 1.0, f"Angle {a} exceeds servo limit"

    def test_minimum_radius_from_ea10(self):
        """EA-10 specifies min turn radius of 993mm at full scale (397mm at 0.4x)."""
        # At min radius, inner angle should be close to max
        fl, fr, rl, rr = ackermann_angles(MIN_TURN_RADIUS)
        inner_angle = abs(fr)  # FR is inner for right turn
        assert inner_angle > 20.0, f"Inner angle {inner_angle} too small at min radius"


# ============================================================
# Servo Microsecond Conversion (from steering.h)
# ============================================================

def angle_to_us(angle_deg: float, inverted: bool = False) -> float:
    """Convert steering angle to servo pulse width in microseconds."""
    if abs(angle_deg) < STEER_DEADBAND:
        angle_deg = 0
    angle_deg = max(-STEER_MAX_ANGLE, min(STEER_MAX_ANGLE, angle_deg))
    if inverted:
        angle_deg = -angle_deg
    return SERVO_CENTER_US + (angle_deg * SERVO_US_PER_DEG)


def us_to_duty(us: float) -> int:
    """Convert microseconds to LEDC duty at 16-bit resolution, 50Hz."""
    return int((us / 20000.0) * 65536.0)


class TestServoMath:
    def test_center_position(self):
        assert angle_to_us(0) == SERVO_CENTER_US

    def test_deadband(self):
        """Angles within deadband should snap to centre."""
        assert angle_to_us(0.5) == SERVO_CENTER_US
        assert angle_to_us(-0.5) == SERVO_CENTER_US

    def test_positive_angle(self):
        us = angle_to_us(10.0)
        assert us > SERVO_CENTER_US
        assert abs(us - (SERVO_CENTER_US + 10.0 * SERVO_US_PER_DEG)) < 0.01

    def test_negative_angle(self):
        us = angle_to_us(-10.0)
        assert us < SERVO_CENTER_US

    def test_clamped_to_max(self):
        us_max = angle_to_us(90.0)  # Way beyond max
        us_limit = angle_to_us(STEER_MAX_ANGLE)
        assert us_max == us_limit

    def test_inverted_for_rear(self):
        """Rear servos are mounted inverted."""
        us_normal = angle_to_us(15.0, inverted=False)
        us_inverted = angle_to_us(15.0, inverted=True)
        assert us_normal > SERVO_CENTER_US
        assert us_inverted < SERVO_CENTER_US

    def test_duty_at_center(self):
        duty = us_to_duty(SERVO_CENTER_US)
        # 1500/20000 * 65536 = 4915.2
        assert abs(duty - 4915) <= 1

    def test_duty_range(self):
        duty_min = us_to_duty(SERVO_MIN_US)
        duty_max = us_to_duty(SERVO_MAX_US)
        assert 0 < duty_min < duty_max < 65536


# ============================================================
# Battery Monitoring (from sensors.h)
# ============================================================

def adc_to_voltage(adc_raw: int, adc_bits: int = 12, ref_v: float = 3.3) -> float:
    """Convert ADC reading to actual battery voltage."""
    adc_voltage = (adc_raw / (2**adc_bits - 1)) * ref_v
    return adc_voltage * BATT_DIVIDER_RATIO


def voltage_to_soc(voltage: float) -> int:
    """Estimate State of Charge (%) from voltage (linear approximation)."""
    if voltage >= BATT_FULL_V:
        return 100
    if voltage <= BATT_CUTOFF_V:
        return 0
    return int(((voltage - BATT_CUTOFF_V) / (BATT_FULL_V - BATT_CUTOFF_V)) * 100)


class TestBatteryMonitoring:
    def test_full_battery(self):
        assert voltage_to_soc(BATT_FULL_V) == 100

    def test_above_full(self):
        assert voltage_to_soc(9.0) == 100

    def test_cutoff(self):
        assert voltage_to_soc(BATT_CUTOFF_V) == 0

    def test_below_cutoff(self):
        assert voltage_to_soc(5.0) == 0

    def test_nominal(self):
        soc = voltage_to_soc(BATT_NOMINAL_V)
        assert 40 < soc < 60, f"Nominal voltage should be ~50% SoC, got {soc}%"

    def test_warning_level(self):
        soc = voltage_to_soc(BATT_WARN_V)
        assert 20 < soc < 40, f"Warning voltage should be ~30% SoC, got {soc}%"

    def test_adc_full_scale(self):
        """Max ADC reading (4095) should give a reasonable battery voltage."""
        v = adc_to_voltage(4095)
        assert v > 8.0, f"Full ADC should read > 8V, got {v:.2f}V"
        assert v < 12.0, f"Full ADC should read < 12V, got {v:.2f}V"

    def test_adc_zero(self):
        assert adc_to_voltage(0) == 0.0

    def test_adc_midpoint(self):
        """Midpoint ADC should give roughly half the max voltage."""
        v = adc_to_voltage(2048)
        assert 4.0 < v < 6.0


# ============================================================
# COBS Encoding (from uart_binary.h, Phase 2)
# ============================================================

def cobs_encode(data: bytes) -> bytes:
    """
    COBS-encode a byte string (no framing zeros added).
    Standard COBS: replaces all zeros with run-length codes.
    """
    if not data:
        return b'\x01'
    output = bytearray()
    # Process data in segments between zeros
    segments = data.split(b'\x00')
    for i, seg in enumerate(segments):
        # Overhead byte = segment length + 1
        output.append(len(seg) + 1)
        output.extend(seg)
    return bytes(output)


def cobs_decode(data: bytes) -> bytes:
    """COBS-decode a byte string."""
    if not data:
        return b''
    output = bytearray()
    idx = 0
    while idx < len(data):
        code = data[idx]
        if code == 0:
            raise ValueError("COBS decode: unexpected zero byte")
        idx += 1
        for _ in range(code - 1):
            if idx >= len(data):
                raise ValueError("COBS decode: unexpected end of data")
            output.append(data[idx])
            idx += 1
        # Append implicit zero between groups (not after last)
        if idx < len(data):
            output.append(0)
    return bytes(output)


def crc16_ccitt(data: bytes, init: int = 0xFFFF) -> int:
    """CRC-16/CCITT as used in EA-18 binary protocol."""
    crc = init
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            crc &= 0xFFFF
    return crc


class TestCOBSEncoding:
    def test_no_zeros(self):
        data = b'\x01\x02\x03'
        encoded = cobs_encode(data)
        decoded = cobs_decode(encoded)
        assert decoded == data

    def test_single_zero(self):
        data = b'\x00'
        encoded = cobs_encode(data)
        decoded = cobs_decode(encoded)
        assert decoded == data

    def test_zeros_and_data(self):
        data = b'\x01\x00\x02\x00\x03'
        encoded = cobs_encode(data)
        assert b'\x00' not in encoded  # COBS eliminates all zeros
        decoded = cobs_decode(encoded)
        assert decoded == data

    def test_empty(self):
        # COBS of empty data is a single overhead byte \x01
        assert cobs_encode(b'') == b'\x01'

    def test_all_zeros(self):
        data = b'\x00\x00\x00'
        encoded = cobs_encode(data)
        assert b'\x00' not in encoded
        decoded = cobs_decode(encoded)
        assert decoded == data

    def test_round_trip_motor_command(self):
        """Simulate a motor command packet."""
        # msg_id=0x01, left_speed=50, right_speed=-30
        payload = struct.pack('<Bbb', 0x01, 50, -30)
        crc = crc16_ccitt(payload)
        packet = payload + struct.pack('<H', crc)
        encoded = cobs_encode(packet)
        assert b'\x00' not in encoded
        decoded = cobs_decode(encoded)
        assert decoded == packet
        # Verify CRC
        assert crc16_ccitt(decoded[:-2]) == struct.unpack('<H', decoded[-2:])[0]


class TestCRC16:
    def test_known_value(self):
        # CRC-16/CCITT of "123456789" = 0x29B1
        assert crc16_ccitt(b'123456789') == 0x29B1

    def test_empty(self):
        assert crc16_ccitt(b'') == 0xFFFF

    def test_single_byte(self):
        result = crc16_ccitt(b'\x00')
        assert isinstance(result, int)
        assert 0 <= result <= 0xFFFF

    def test_deterministic(self):
        data = b'\x01\x02\x03\x04'
        assert crc16_ccitt(data) == crc16_ccitt(data)

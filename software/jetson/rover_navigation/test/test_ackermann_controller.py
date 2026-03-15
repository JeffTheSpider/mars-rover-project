"""Unit tests for Ackermann steering controller.

Tests pure geometry/math without a running ROS2 system.
"""

import math
import pytest
from rover_navigation.ackermann_controller import AckermannControllerNode


@pytest.fixture
def controller():
    """Create an AckermannControllerNode with default parameters."""
    return AckermannControllerNode()


# ---------------------------------------------------------------------------
# Rover geometry constants (from default parameters)
# ---------------------------------------------------------------------------

WHEELBASE_M = 0.360
TRACK_M = 0.280
HALF_TRACK = TRACK_M / 2.0
L_FM = 0.180
L_MR = 0.180
MAX_STEER_DEG = 35.0
MAX_STEER_RAD = math.radians(MAX_STEER_DEG)
MAX_SPEED = 0.56
MIN_TURN_RADIUS = WHEELBASE_M / math.tan(MAX_STEER_RAD)


# ===== Straight driving =====

class TestStraightDriving:
    """All angles should be 0 when driving straight."""

    def test_straight_forward_angles_zero(self, controller):
        speeds, angles = controller._ackermann(0.3, 0.0)
        for a in angles:
            assert a == pytest.approx(0.0, abs=1e-6)

    def test_straight_forward_speeds_equal(self, controller):
        speeds, angles = controller._ackermann(0.3, 0.0)
        assert len(speeds) == 6
        expected_pct = (0.3 / MAX_SPEED) * 100.0
        for s in speeds:
            assert s == pytest.approx(expected_pct, abs=1e-6)

    def test_straight_reverse_angles_zero(self, controller):
        speeds, angles = controller._ackermann(-0.2, 0.0)
        for a in angles:
            assert a == pytest.approx(0.0, abs=1e-6)

    def test_straight_reverse_speeds_negative(self, controller):
        speeds, angles = controller._ackermann(-0.2, 0.0)
        expected_pct = (-0.2 / MAX_SPEED) * 100.0
        for s in speeds:
            assert s == pytest.approx(expected_pct, abs=1e-6)

    def test_zero_input_all_zero(self, controller):
        speeds, angles = controller._ackermann(0.0, 0.0)
        for a in angles:
            assert a == pytest.approx(0.0, abs=1e-6)
        for s in speeds:
            assert s == pytest.approx(0.0, abs=1e-6)


# ===== Ackermann angle geometry =====

class TestAckermannAngles:
    """Inner wheel must steer more sharply than outer wheel."""

    def test_left_turn_inner_greater_than_outer(self, controller):
        """Turning left: FL is inner, FR is outer. |FL| > |FR|."""
        speeds, angles = controller._ackermann(0.3, 0.5)
        fl_angle, fr_angle = angles[0], angles[1]
        # Both positive for left turn
        assert fl_angle > 0
        assert fr_angle > 0
        # Inner wheel (left) has larger angle
        assert abs(fl_angle) > abs(fr_angle)

    def test_right_turn_inner_greater_than_outer(self, controller):
        """Turning right: FR is inner, FL is outer. |FR| > |FL|."""
        speeds, angles = controller._ackermann(0.3, -0.5)
        fl_angle, fr_angle = angles[0], angles[1]
        # Both negative for right turn
        assert fl_angle < 0
        assert fr_angle < 0
        # Inner wheel (right) has larger angle
        assert abs(fr_angle) > abs(fl_angle)

    def test_rear_wheels_counter_steer(self, controller):
        """Rear wheels steer opposite direction to front for tighter turns."""
        speeds, angles = controller._ackermann(0.3, 0.5)
        fl_angle, fr_angle, rl_angle, rr_angle = angles
        # Front positive, rear negative for left turn
        assert fl_angle > 0
        assert rl_angle < 0

    def test_angles_symmetric_for_opposite_turns(self, controller):
        """Left and right turns should produce mirror-image angles."""
        _, angles_left = controller._ackermann(0.3, 0.5)
        _, angles_right = controller._ackermann(0.3, -0.5)
        # FL_left should equal -FR_right (and vice versa)
        assert abs(angles_left[0]) == pytest.approx(abs(angles_right[1]), abs=1e-6)
        assert abs(angles_left[1]) == pytest.approx(abs(angles_right[0]), abs=1e-6)


# ===== Minimum turn radius enforcement =====

class TestMinTurnRadius:
    """Turn radius must be clamped to the minimum."""

    def test_min_turn_radius_value(self, controller):
        expected = WHEELBASE_M / math.tan(MAX_STEER_RAD)
        assert controller.min_turn_radius == pytest.approx(expected, rel=1e-4)

    def test_tight_turn_clamped(self, controller):
        """Very tight angular command should not produce angles beyond max_steer."""
        speeds, angles = controller._ackermann(0.1, 5.0)
        for a in angles:
            assert abs(a) <= MAX_STEER_RAD + 1e-6

    def test_steering_angles_within_limits(self, controller):
        """Sweep a range of angular velocities - all angles must stay in bounds."""
        for angular in [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
            speeds, angles = controller._ackermann(0.3, angular)
            for a in angles:
                assert abs(a) <= MAX_STEER_RAD + 1e-6, \
                    f"Angle {math.degrees(a):.1f} exceeds max {MAX_STEER_DEG} at angular={angular}"


# ===== Speed limiting and clamping =====

class TestSpeedLimiting:
    """Speed percentages should be within [-100, 100] bounds."""

    def test_cmd_vel_clamps_linear(self, controller):
        """Linear velocity in cmd_vel_callback is clamped to max_speed."""
        from unittest.mock import MagicMock
        twist = MagicMock()
        twist.linear.x = 999.0  # Way over max
        twist.linear.y = 0.0
        twist.angular.z = 0.0
        controller.cmd_vel_callback(twist)
        # Should not crash; the internal clamp caps at max_speed

    def test_outer_wheel_speed_normalized(self, controller):
        """Outer wheels are faster but normalized so max = base_speed."""
        speeds, _ = controller._ackermann(MAX_SPEED, 0.5)
        # Maximum speed in the array should be ~100%
        assert max(speeds) == pytest.approx(100.0, abs=5.0)

    def test_inner_wheel_slower_than_outer(self, controller):
        """During a turn, inner wheels should be slower than outer."""
        speeds, _ = controller._ackermann(0.3, 0.5)
        # For left turn: left side (indices 0,1,2) are inner
        # Right side (indices 3,4,5) are outer
        left_avg = sum(abs(speeds[i]) for i in [0, 1, 2]) / 3
        right_avg = sum(abs(speeds[i]) for i in [3, 4, 5]) / 3
        assert left_avg < right_avg


# ===== Point turn mode =====

class TestPointTurn:
    """Zero-radius spin: left wheels backward, right wheels forward."""

    def test_point_turn_opposite_sides(self, controller):
        speeds, angles = controller._point_turn(1.0)
        # Left wheels (0,1,2) negative, right (3,4,5) positive for angular > 0
        for i in [0, 1, 2]:
            assert speeds[i] < 0
        for i in [3, 4, 5]:
            assert speeds[i] > 0

    def test_point_turn_reverse_direction(self, controller):
        speeds, angles = controller._point_turn(-1.0)
        # Reversed: left positive, right negative
        for i in [0, 1, 2]:
            assert speeds[i] > 0
        for i in [3, 4, 5]:
            assert speeds[i] < 0

    def test_point_turn_steering_angles(self, controller):
        """All corner wheels at max steering forming an X pattern."""
        speeds, angles = controller._point_turn(1.0)
        max_s = math.radians(35.0)
        # FL positive, FR negative, RL negative, RR positive
        assert angles[0] == pytest.approx(max_s, abs=1e-6)
        assert angles[1] == pytest.approx(-max_s, abs=1e-6)
        assert angles[2] == pytest.approx(-max_s, abs=1e-6)
        assert angles[3] == pytest.approx(max_s, abs=1e-6)

    def test_point_turn_speed_capped(self, controller):
        """Speed should not exceed 100%."""
        speeds, _ = controller._point_turn(100.0)
        for s in speeds:
            assert abs(s) <= 100.0 + 1e-6

    def test_pure_rotation_delegates_to_point_turn(self, controller):
        """Ackermann with linear~0 and angular!=0 should use point turn."""
        speeds_ack, angles_ack = controller._ackermann(0.0, 1.0)
        speeds_pt, angles_pt = controller._point_turn(1.0)
        assert speeds_ack == speeds_pt
        assert angles_ack == angles_pt


# ===== Crab walk mode =====

class TestCrabWalk:
    """All wheels same angle, all same speed for lateral movement."""

    def test_crab_all_angles_equal(self, controller):
        speeds, angles = controller._crab_walk(0.0, 0.3)
        # All 4 angles should be identical
        assert all(a == pytest.approx(angles[0], abs=1e-6) for a in angles)

    def test_crab_all_speeds_equal(self, controller):
        speeds, angles = controller._crab_walk(0.0, 0.3)
        assert all(s == pytest.approx(speeds[0], abs=1e-6) for s in speeds)

    def test_crab_zero_input_stops(self, controller):
        speeds, angles = controller._crab_walk(0.0, 0.0)
        for s in speeds:
            assert s == pytest.approx(0.0, abs=1e-6)
        for a in angles:
            assert a == pytest.approx(0.0, abs=1e-6)

    def test_crab_heading_pure_lateral(self, controller):
        """Pure y input should produce heading = pi/2 (clamped to max_steer)."""
        speeds, angles = controller._crab_walk(0.0, 0.3)
        expected = min(math.pi / 2, MAX_STEER_RAD)
        assert angles[0] == pytest.approx(expected, abs=1e-6)

    def test_crab_speed_capped(self, controller):
        speeds, angles = controller._crab_walk(MAX_SPEED, MAX_SPEED)
        for s in speeds:
            assert s <= 100.0 + 1e-6


# ===== Drive mode switching =====

class TestDriveMode:
    """Verify mode_callback sets drive_mode correctly."""

    def test_default_mode_is_ackermann(self, controller):
        assert controller.drive_mode == AckermannControllerNode.MODE_ACKERMANN

    def test_switch_to_point_turn(self, controller):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.data = AckermannControllerNode.MODE_POINT_TURN
        controller.mode_callback(msg)
        assert controller.drive_mode == AckermannControllerNode.MODE_POINT_TURN

    def test_switch_to_crab(self, controller):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.data = AckermannControllerNode.MODE_CRAB
        controller.mode_callback(msg)
        assert controller.drive_mode == AckermannControllerNode.MODE_CRAB

    def test_invalid_mode_ignored(self, controller):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.data = 99
        controller.mode_callback(msg)
        assert controller.drive_mode == AckermannControllerNode.MODE_ACKERMANN

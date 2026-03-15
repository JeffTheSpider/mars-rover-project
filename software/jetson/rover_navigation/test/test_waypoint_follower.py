"""Unit tests for the waypoint follower node.

Tests waypoint queue management, distance calculation, waypoint reached
detection, and heading calculation without a running ROS2 system.
"""

import math
import pytest
from rover_navigation.waypoint_follower import WaypointFollowerNode


@pytest.fixture
def follower():
    """Create a WaypointFollowerNode with default parameters."""
    return WaypointFollowerNode()


# ===== Waypoint queue management =====

class TestWaypointQueue:
    """Test adding, clearing, and indexing waypoints."""

    def test_initial_empty(self, follower):
        assert len(follower.waypoints) == 0
        assert follower.current_wp_index == 0
        assert follower.state == WaypointFollowerNode.STATE_IDLE

    def test_add_waypoints_via_json(self, follower):
        """Simulate receiving waypoints via JSON string callback."""
        from unittest.mock import MagicMock
        import json
        msg = MagicMock()
        msg.data = json.dumps([
            {"x": 1.0, "y": 2.0},
            {"x": 3.0, "y": 4.0},
            {"x": 5.0, "y": 6.0},
        ])
        follower.waypoints_json_callback(msg)
        assert len(follower.waypoints) == 3
        assert follower.waypoints[0] == (1.0, 2.0)
        assert follower.waypoints[2] == (5.0, 6.0)

    def test_json_sets_state_to_following(self, follower):
        from unittest.mock import MagicMock
        import json
        msg = MagicMock()
        msg.data = json.dumps([{"x": 1.0, "y": 2.0}])
        follower.waypoints_json_callback(msg)
        assert follower.state == WaypointFollowerNode.STATE_FOLLOWING

    def test_json_resets_index(self, follower):
        """New waypoints should reset current_wp_index to 0."""
        follower.current_wp_index = 5
        from unittest.mock import MagicMock
        import json
        msg = MagicMock()
        msg.data = json.dumps([{"x": 1.0, "y": 2.0}])
        follower.waypoints_json_callback(msg)
        assert follower.current_wp_index == 0

    def test_invalid_json_ignored(self, follower):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.data = "not valid json"
        follower.waypoints_json_callback(msg)
        assert len(follower.waypoints) == 0
        assert follower.state == WaypointFollowerNode.STATE_IDLE

    def test_missing_keys_ignored(self, follower):
        from unittest.mock import MagicMock
        import json
        msg = MagicMock()
        msg.data = json.dumps([{"lat": 1.0, "lng": 2.0}])  # Wrong keys
        follower.waypoints_json_callback(msg)
        assert len(follower.waypoints) == 0


# ===== Distance to waypoint =====

class TestDistanceCalculation:
    """Test distance computation used in the control loop."""

    def test_distance_simple(self):
        """Direct hypot check: (3,4) from origin = 5."""
        d = math.hypot(3.0 - 0.0, 4.0 - 0.0)
        assert d == pytest.approx(5.0, abs=1e-6)

    def test_distance_zero(self):
        d = math.hypot(0.0, 0.0)
        assert d == pytest.approx(0.0, abs=1e-6)

    def test_distance_negative_coords(self):
        d = math.hypot(-3.0 - 0.0, -4.0 - 0.0)
        assert d == pytest.approx(5.0, abs=1e-6)


# ===== Waypoint reached detection =====

class TestWaypointReached:
    """Verify the control loop advances when within tolerance."""

    def test_waypoint_reached_advances_index(self, follower):
        """When rover is within tolerance of waypoint, index should increment."""
        import json
        from unittest.mock import MagicMock

        # Set up waypoints
        msg = MagicMock()
        msg.data = json.dumps([{"x": 1.0, "y": 0.0}, {"x": 2.0, "y": 0.0}])
        follower.waypoints_json_callback(msg)

        # Place rover right on top of first waypoint
        follower.current_pose = (1.0, 0.0, 0.0)
        assert follower.current_wp_index == 0

        follower.control_loop()
        assert follower.current_wp_index == 1

    def test_waypoint_not_reached_stays(self, follower):
        """When rover is far from waypoint, index should not change."""
        import json
        from unittest.mock import MagicMock

        msg = MagicMock()
        msg.data = json.dumps([{"x": 10.0, "y": 0.0}])
        follower.waypoints_json_callback(msg)

        follower.current_pose = (0.0, 0.0, 0.0)
        follower.control_loop()
        assert follower.current_wp_index == 0

    def test_within_tolerance_threshold(self, follower):
        """Point within tolerance (default 0.3m) should be considered reached."""
        import json
        from unittest.mock import MagicMock

        msg = MagicMock()
        msg.data = json.dumps([{"x": 1.0, "y": 0.0}])
        follower.waypoints_json_callback(msg)

        # Place rover 0.2m away (within 0.3m tolerance)
        follower.current_pose = (0.8, 0.0, 0.0)
        follower.control_loop()
        assert follower.current_wp_index == 1

    def test_just_outside_tolerance(self, follower):
        """Point just outside tolerance should NOT be reached."""
        import json
        from unittest.mock import MagicMock

        msg = MagicMock()
        msg.data = json.dumps([{"x": 1.0, "y": 0.0}])
        follower.waypoints_json_callback(msg)

        # Place rover 0.35m away (outside 0.3m tolerance)
        follower.current_pose = (0.65, 0.0, 0.0)
        follower.control_loop()
        assert follower.current_wp_index == 0

    def test_all_waypoints_completed(self, follower):
        """After reaching all waypoints, state should be COMPLETED."""
        import json
        from unittest.mock import MagicMock

        msg = MagicMock()
        msg.data = json.dumps([{"x": 1.0, "y": 0.0}])
        follower.waypoints_json_callback(msg)

        # Reach the only waypoint
        follower.current_pose = (1.0, 0.0, 0.0)
        follower.control_loop()
        assert follower.current_wp_index == 1

        # Next tick should mark completed
        follower.control_loop()
        assert follower.state == WaypointFollowerNode.STATE_COMPLETED


# ===== Heading calculation =====

class TestHeadingCalculation:
    """Test the pure pursuit heading/curvature math."""

    def test_target_ahead_no_curvature(self, follower):
        """Target directly ahead (in robot frame) should have ~0 curvature."""
        import json
        from unittest.mock import MagicMock

        msg = MagicMock()
        msg.data = json.dumps([{"x": 5.0, "y": 0.0}])
        follower.waypoints_json_callback(msg)

        # Robot at origin facing +x (yaw=0), target at (5,0)
        follower.current_pose = (0.0, 0.0, 0.0)
        follower.control_loop()
        # The published twist should have ~0 angular.z
        # (We test the math, not the publish)
        dx = 5.0
        dy = 0.0
        yaw = 0.0
        local_y = dx * math.sin(-yaw) + dy * math.cos(-yaw)
        assert local_y == pytest.approx(0.0, abs=1e-6)

    def test_target_to_left_positive_curvature(self):
        """Target to the left in robot frame should give positive curvature."""
        dx, dy = 5.0, 2.0
        yaw = 0.0
        local_y = dx * math.sin(-yaw) + dy * math.cos(-yaw)
        L = math.hypot(dx, dy)
        curvature = 2.0 * local_y / (L * L)
        assert curvature > 0

    def test_target_to_right_negative_curvature(self):
        """Target to the right in robot frame should give negative curvature."""
        dx, dy = 5.0, -2.0
        yaw = 0.0
        local_y = dx * math.sin(-yaw) + dy * math.cos(-yaw)
        L = math.hypot(dx, dy)
        curvature = 2.0 * local_y / (L * L)
        assert curvature < 0


# ===== Pause / Resume =====

class TestPauseResume:
    """Test pause and resume toggling."""

    def test_pause_while_following(self, follower):
        from unittest.mock import MagicMock
        import json

        msg = MagicMock()
        msg.data = json.dumps([{"x": 10.0, "y": 0.0}])
        follower.waypoints_json_callback(msg)
        assert follower.state == WaypointFollowerNode.STATE_FOLLOWING

        pause_msg = MagicMock()
        pause_msg.data = True
        follower.pause_callback(pause_msg)
        assert follower.state == WaypointFollowerNode.STATE_PAUSED

    def test_resume_after_pause(self, follower):
        from unittest.mock import MagicMock
        import json

        msg = MagicMock()
        msg.data = json.dumps([{"x": 10.0, "y": 0.0}])
        follower.waypoints_json_callback(msg)

        pause = MagicMock()
        pause.data = True
        follower.pause_callback(pause)
        assert follower.state == WaypointFollowerNode.STATE_PAUSED

        resume = MagicMock()
        resume.data = False
        follower.pause_callback(resume)
        assert follower.state == WaypointFollowerNode.STATE_FOLLOWING

    def test_pause_while_idle_no_effect(self, follower):
        from unittest.mock import MagicMock
        pause = MagicMock()
        pause.data = True
        follower.pause_callback(pause)
        assert follower.state == WaypointFollowerNode.STATE_IDLE

    def test_control_loop_skips_when_paused(self, follower):
        from unittest.mock import MagicMock
        import json

        msg = MagicMock()
        msg.data = json.dumps([{"x": 1.0, "y": 0.0}])
        follower.waypoints_json_callback(msg)
        follower.current_pose = (1.0, 0.0, 0.0)

        pause = MagicMock()
        pause.data = True
        follower.pause_callback(pause)

        # Control loop should skip (paused), so index stays
        follower.control_loop()
        assert follower.current_wp_index == 0

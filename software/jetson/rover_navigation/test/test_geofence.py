"""Unit tests for the geofence safety node.

Tests haversine distance, bearing calculation, and zone classification
without a running ROS2 system.
"""

import math
import pytest
from rover_navigation.geofence_node import GeofenceNode


@pytest.fixture
def geofence():
    """Create a GeofenceNode with default parameters (25m radius, 3m warn margin)."""
    return GeofenceNode()


# ===== Haversine distance calculation =====

class TestHaversine:
    """Verify haversine formula against known reference distances."""

    def test_same_point_distance_zero(self):
        d = GeofenceNode._haversine(51.5074, -0.1278, 51.5074, -0.1278)
        assert d == pytest.approx(0.0, abs=0.01)

    def test_london_to_paris(self):
        """London (51.5074, -0.1278) to Paris (48.8566, 2.3522) ~ 343.5 km."""
        d = GeofenceNode._haversine(51.5074, -0.1278, 48.8566, 2.3522)
        assert d == pytest.approx(343_550, rel=0.01)  # Within 1%

    def test_new_york_to_los_angeles(self):
        """NYC (40.7128, -74.0060) to LA (34.0522, -118.2437) ~ 3944 km."""
        d = GeofenceNode._haversine(40.7128, -74.0060, 34.0522, -118.2437)
        assert d == pytest.approx(3_944_000, rel=0.02)  # Within 2%

    def test_short_distance_accuracy(self):
        """Two points ~111m apart (0.001 deg latitude at equator)."""
        d = GeofenceNode._haversine(0.0, 0.0, 0.001, 0.0)
        # 0.001 deg lat ~ 111.2m
        assert d == pytest.approx(111.2, rel=0.01)

    def test_symmetric(self):
        """Distance A->B should equal B->A."""
        d1 = GeofenceNode._haversine(51.5, -0.1, 48.8, 2.3)
        d2 = GeofenceNode._haversine(48.8, 2.3, 51.5, -0.1)
        assert d1 == pytest.approx(d2, abs=0.01)

    def test_antipodal_points(self):
        """North pole to south pole ~ 20015 km (half circumference)."""
        d = GeofenceNode._haversine(90.0, 0.0, -90.0, 0.0)
        assert d == pytest.approx(20_015_000, rel=0.01)


# ===== Bearing calculation =====

class TestBearing:
    """Verify bearing between two GPS points."""

    def test_due_north(self):
        """Point directly north should have bearing ~ 0."""
        b = GeofenceNode._bearing(0.0, 0.0, 1.0, 0.0)
        assert b == pytest.approx(0.0, abs=0.01)

    def test_due_east(self):
        """Point directly east should have bearing ~ pi/2."""
        b = GeofenceNode._bearing(0.0, 0.0, 0.0, 1.0)
        assert b == pytest.approx(math.pi / 2, abs=0.01)

    def test_due_south(self):
        """Point directly south should have bearing ~ pi."""
        b = GeofenceNode._bearing(1.0, 0.0, 0.0, 0.0)
        assert abs(b) == pytest.approx(math.pi, abs=0.01)

    def test_due_west(self):
        """Point directly west should have bearing ~ -pi/2."""
        b = GeofenceNode._bearing(0.0, 0.0, 0.0, -1.0)
        assert b == pytest.approx(-math.pi / 2, abs=0.01)


# ===== Geofence zone classification =====

class TestZoneClassification:
    """Test check_fence determines the correct zone."""

    def test_point_inside_safe_zone(self, geofence):
        """A point well inside the fence should be SAFE."""
        geofence.current_position = (5.0, 5.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_SAFE

    def test_point_in_warning_zone(self, geofence):
        """A point between warn_radius and fence_radius should be WARNING."""
        # fence_radius=25, warn_margin=3 -> warn_radius=22
        # Distance = 23 is between 22 and 25
        geofence.current_position = (23.0, 0.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_WARNING

    def test_point_outside_fence_is_breach(self, geofence):
        """A point beyond the fence radius should be BREACH."""
        geofence.current_position = (26.0, 0.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_BREACH

    def test_point_exactly_on_boundary_is_breach(self, geofence):
        """A point exactly at fence_radius should be BREACH (>= check)."""
        geofence.current_position = (25.0, 0.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_BREACH

    def test_point_exactly_on_warn_boundary(self, geofence):
        """A point exactly at warn_radius should be WARNING (>= check)."""
        geofence.current_position = (22.0, 0.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_WARNING

    def test_point_at_origin_is_safe(self, geofence):
        """Home position should be safe."""
        geofence.current_position = (0.0, 0.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_SAFE

    def test_diagonal_distance(self, geofence):
        """Test with 2D distance: (18, 18) -> hypot ~ 25.46 -> BREACH."""
        geofence.current_position = (18.0, 18.0)
        geofence.check_fence()
        dist = math.hypot(18.0, 18.0)
        assert dist > 25.0
        assert geofence.current_zone == GeofenceNode.ZONE_BREACH

    def test_diagonal_inside(self, geofence):
        """(10, 10) -> hypot ~ 14.14 -> SAFE."""
        geofence.current_position = (10.0, 10.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_SAFE


# ===== Geofence disabled (no position) =====

class TestGeofenceNoPosition:
    """When no position is available, fence check should be a no-op."""

    def test_no_position_stays_safe(self, geofence):
        """No position data should leave zone unchanged (default SAFE)."""
        assert geofence.current_position is None
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_SAFE

    def test_distance_stays_zero_without_position(self, geofence):
        geofence.check_fence()
        assert geofence.current_distance == pytest.approx(0.0)


# ===== Distance tracking =====

class TestDistanceTracking:
    """Verify current_distance is updated correctly."""

    def test_distance_updates(self, geofence):
        geofence.current_position = (3.0, 4.0)
        geofence.check_fence()
        assert geofence.current_distance == pytest.approx(5.0, abs=1e-6)

    def test_distance_from_nonzero_home(self, geofence):
        """Distance measured from home position, not origin."""
        geofence.home_x = 10.0
        geofence.home_y = 10.0
        geofence.current_position = (13.0, 14.0)
        geofence.check_fence()
        assert geofence.current_distance == pytest.approx(5.0, abs=1e-6)


# ===== Zone transitions =====

class TestZoneTransitions:
    """Verify zone transition from safe to warning to breach and back."""

    def test_safe_to_warning_transition(self, geofence):
        geofence.current_position = (5.0, 0.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_SAFE

        geofence.current_position = (23.0, 0.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_WARNING

    def test_warning_to_breach_transition(self, geofence):
        geofence.current_position = (23.0, 0.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_WARNING

        geofence.current_position = (26.0, 0.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_BREACH

    def test_breach_back_to_safe(self, geofence):
        geofence.current_position = (26.0, 0.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_BREACH

        geofence.current_position = (5.0, 0.0)
        geofence.check_fence()
        assert geofence.current_zone == GeofenceNode.ZONE_SAFE

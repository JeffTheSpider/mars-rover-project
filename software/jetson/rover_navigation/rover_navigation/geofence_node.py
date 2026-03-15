#!/usr/bin/env python3
"""Geofence safety node for the Mars Rover.

Monitors the rover's position and enforces a virtual fence boundary.
When the rover approaches or crosses the boundary, it triggers warnings
and can send an e-stop command.
"""

import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Bool, String
from geometry_msgs.msg import Twist
import json
from typing import Optional, Tuple


class GeofenceNode(Node):
    """Enforces a circular geofence boundary around a home position."""

    # Geofence states
    ZONE_SAFE = 'safe'
    ZONE_WARNING = 'warning'
    ZONE_BREACH = 'breach'

    def __init__(self):
        super().__init__('geofence')

        # Parameters
        self.declare_parameter('fence_radius', 25.0)  # metres
        self.declare_parameter('home_lat', 0.0)
        self.declare_parameter('home_lon', 0.0)
        self.declare_parameter('warn_margin', 3.0)  # metres before boundary
        self.declare_parameter('use_gps', False)
        self.declare_parameter('home_x', 0.0)  # For local odom mode
        self.declare_parameter('home_y', 0.0)
        self.declare_parameter('check_rate', 5.0)

        self.fence_radius = self.get_parameter('fence_radius').get_parameter_value().double_value
        self.home_lat = self.get_parameter('home_lat').get_parameter_value().double_value
        self.home_lon = self.get_parameter('home_lon').get_parameter_value().double_value
        self.warn_margin = self.get_parameter('warn_margin').get_parameter_value().double_value
        self.use_gps = self.get_parameter('use_gps').get_parameter_value().bool_value
        self.home_x = self.get_parameter('home_x').get_parameter_value().double_value
        self.home_y = self.get_parameter('home_y').get_parameter_value().double_value
        check_rate = self.get_parameter('check_rate').get_parameter_value().double_value

        self.warn_radius = self.fence_radius - self.warn_margin

        # State
        self.current_zone = self.ZONE_SAFE
        self.current_distance = 0.0
        self.current_position: Optional[Tuple[float, float]] = None

        # Subscribers
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        if self.use_gps:
            self.gps_sub = self.create_subscription(
                NavSatFix, '/gps/fix', self.gps_callback, 10)

        # Publishers
        self.estop_pub = self.create_publisher(Bool, '/estop', 10)
        self.zone_pub = self.create_publisher(String, '/geofence/zone', 10)
        self.cmd_vel_override_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Check timer
        self.check_timer = self.create_timer(1.0 / check_rate, self.check_fence)

        self.get_logger().info(
            f'Geofence active: radius={self.fence_radius}m, '
            f'warn_margin={self.warn_margin}m, '
            f'home=({self.home_x}, {self.home_y})'
        )

    def odom_callback(self, msg: Odometry):
        """Update position from odometry."""
        if not self.use_gps:
            self.current_position = (
                msg.pose.pose.position.x,
                msg.pose.pose.position.y,
            )

    def gps_callback(self, msg: NavSatFix):
        """Update position from GPS."""
        if self.use_gps and msg.status.status >= 0:
            # Convert GPS to local distance from home
            dist = self._haversine(
                self.home_lat, self.home_lon,
                msg.latitude, msg.longitude,
            )
            # For geofence we only need distance, not exact position
            bearing = self._bearing(
                self.home_lat, self.home_lon,
                msg.latitude, msg.longitude,
            )
            self.current_position = (
                dist * math.cos(bearing),
                dist * math.sin(bearing),
            )

    def check_fence(self):
        """Check if rover is within geofence boundary."""
        if self.current_position is None:
            return

        x, y = self.current_position
        dx = x - self.home_x
        dy = y - self.home_y
        self.current_distance = math.hypot(dx, dy)

        # Determine zone
        prev_zone = self.current_zone

        if self.current_distance >= self.fence_radius:
            self.current_zone = self.ZONE_BREACH
        elif self.current_distance >= self.warn_radius:
            self.current_zone = self.ZONE_WARNING
        else:
            self.current_zone = self.ZONE_SAFE

        # Log zone transitions
        if self.current_zone != prev_zone:
            if self.current_zone == self.ZONE_BREACH:
                self.get_logger().error(
                    f'GEOFENCE BREACH! Distance: {self.current_distance:.1f}m '
                    f'(limit: {self.fence_radius:.1f}m)'
                )
                # Send e-stop
                estop = Bool()
                estop.data = True
                self.estop_pub.publish(estop)

                # Send zero velocity
                self.cmd_vel_override_pub.publish(Twist())

            elif self.current_zone == self.ZONE_WARNING:
                self.get_logger().warn(
                    f'Approaching geofence boundary: {self.current_distance:.1f}m / '
                    f'{self.fence_radius:.1f}m'
                )
            elif self.current_zone == self.ZONE_SAFE and prev_zone != self.ZONE_SAFE:
                self.get_logger().info('Returned to safe zone')
                # Release e-stop
                estop = Bool()
                estop.data = False
                self.estop_pub.publish(estop)

        # Publish zone status
        status = {
            'zone': self.current_zone,
            'distance': round(self.current_distance, 2),
            'fence_radius': self.fence_radius,
            'position': [round(x, 2), round(y, 2)],
        }
        zone_msg = String()
        zone_msg.data = json.dumps(status)
        self.zone_pub.publish(zone_msg)

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance between two GPS points in metres."""
        R = 6371000  # Earth radius in metres
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = (math.sin(dphi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    @staticmethod
    def _bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing from point 1 to point 2 in radians."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dlambda = math.radians(lon2 - lon1)

        x = math.sin(dlambda) * math.cos(phi2)
        y = (math.cos(phi1) * math.sin(phi2) -
             math.sin(phi1) * math.cos(phi2) * math.cos(dlambda))

        return math.atan2(x, y)


def main(args=None):
    rclpy.init(args=args)
    node = GeofenceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

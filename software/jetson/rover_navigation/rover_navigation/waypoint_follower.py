#!/usr/bin/env python3
"""Waypoint follower node for the Mars Rover.

Receives a list of GPS or local waypoints and drives the rover through
them sequentially using pure pursuit path tracking.
"""

import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import Twist, PoseStamped, PoseArray
from nav_msgs.msg import Odometry, Path
from std_msgs.msg import Bool, String
import json
from typing import List, Optional, Tuple


class WaypointFollowerNode(Node):
    """Follows a sequence of waypoints using pure pursuit."""

    # States
    STATE_IDLE = 'idle'
    STATE_FOLLOWING = 'following'
    STATE_PAUSED = 'paused'
    STATE_COMPLETED = 'completed'

    def __init__(self):
        super().__init__('waypoint_follower')

        # Parameters
        self.declare_parameter('waypoint_tolerance', 0.3)
        self.declare_parameter('lookahead_distance', 0.5)
        self.declare_parameter('max_linear_speed', 0.4)
        self.declare_parameter('max_angular_speed', 1.0)
        self.declare_parameter('control_rate', 20.0)
        self.declare_parameter('patrol_mode', False)

        self.waypoint_tolerance = self.get_parameter('waypoint_tolerance').get_parameter_value().double_value
        self.lookahead = self.get_parameter('lookahead_distance').get_parameter_value().double_value
        self.max_linear = self.get_parameter('max_linear_speed').get_parameter_value().double_value
        self.max_angular = self.get_parameter('max_angular_speed').get_parameter_value().double_value
        control_rate = self.get_parameter('control_rate').get_parameter_value().double_value
        self.patrol_mode = self.get_parameter('patrol_mode').get_parameter_value().bool_value

        # State
        self.state = self.STATE_IDLE
        self.waypoints: List[Tuple[float, float]] = []
        self.current_wp_index = 0
        self.direction = 1  # 1 = forward through list, -1 = reverse (patrol only)
        self.current_pose: Optional[Tuple[float, float, float]] = None  # x, y, yaw

        # Subscribers
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.waypoints_sub = self.create_subscription(
            PoseArray, '/waypoints', self.waypoints_callback, 10)
        self.waypoints_json_sub = self.create_subscription(
            String, '/waypoints_json', self.waypoints_json_callback, 10)
        self.pause_sub = self.create_subscription(
            Bool, '/waypoint_follower/pause', self.pause_callback, 10)

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(String, '/waypoint_follower/status', 10)
        self.path_pub = self.create_publisher(Path, '/waypoint_follower/path', 10)

        # Control loop timer
        self.control_timer = self.create_timer(1.0 / control_rate, self.control_loop)

        # Status timer
        self.status_timer = self.create_timer(1.0, self.publish_status)

        self.get_logger().info(
            f'Waypoint follower ready: tolerance={self.waypoint_tolerance}m, '
            f'lookahead={self.lookahead}m'
        )

    def odom_callback(self, msg: Odometry):
        """Update current pose from odometry."""
        pos = msg.pose.pose.position
        orient = msg.pose.pose.orientation

        # Extract yaw from quaternion
        siny_cosp = 2.0 * (orient.w * orient.z + orient.x * orient.y)
        cosy_cosp = 1.0 - 2.0 * (orient.y * orient.y + orient.z * orient.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        self.current_pose = (pos.x, pos.y, yaw)

    def waypoints_callback(self, msg: PoseArray):
        """Receive waypoints as PoseArray."""
        self.waypoints = [
            (pose.position.x, pose.position.y)
            for pose in msg.poses
        ]
        self.current_wp_index = 0
        self.direction = 1
        self.state = self.STATE_FOLLOWING
        self.get_logger().info(f'Received {len(self.waypoints)} waypoints, starting navigation')
        self._publish_path()

    def waypoints_json_callback(self, msg: String):
        """Receive waypoints as JSON string: [{"x": 1.0, "y": 2.0}, ...]."""
        try:
            data = json.loads(msg.data)
            self.waypoints = [(wp['x'], wp['y']) for wp in data]
            self.current_wp_index = 0
            self.direction = 1
            self.state = self.STATE_FOLLOWING
            self.get_logger().info(f'Received {len(self.waypoints)} waypoints from JSON')
            self._publish_path()
        except (json.JSONDecodeError, KeyError) as e:
            self.get_logger().error(f'Invalid waypoint JSON: {e}')

    def pause_callback(self, msg: Bool):
        """Pause or resume waypoint following."""
        if msg.data and self.state == self.STATE_FOLLOWING:
            self.state = self.STATE_PAUSED
            self._stop()
            self.get_logger().info('Waypoint following paused')
        elif not msg.data and self.state == self.STATE_PAUSED:
            self.state = self.STATE_FOLLOWING
            self.get_logger().info('Waypoint following resumed')

    def control_loop(self):
        """Main control loop - pure pursuit path tracking."""
        if self.state != self.STATE_FOLLOWING:
            return

        if self.current_pose is None:
            self.get_logger().warn_once('Waiting for odometry...')
            return

        if self.current_wp_index >= len(self.waypoints) or self.current_wp_index < 0:
            if self.patrol_mode:
                # Reverse direction and clamp to valid range
                self.direction *= -1
                if self.current_wp_index >= len(self.waypoints):
                    self.current_wp_index = len(self.waypoints) - 1
                elif self.current_wp_index < 0:
                    self.current_wp_index = 0
                self.get_logger().info(
                    f'Patrol: reversing direction at waypoint boundary'
                )
                return
            else:
                # Single-run mission: stop at the last waypoint
                self.state = self.STATE_COMPLETED
                self._stop()
                self.get_logger().info('All waypoints reached!')
                return

        x, y, yaw = self.current_pose
        wp_x, wp_y = self.waypoints[self.current_wp_index]

        # Distance to current waypoint
        dx = wp_x - x
        dy = wp_y - y
        distance = math.hypot(dx, dy)

        # Check if waypoint reached
        if distance < self.waypoint_tolerance:
            self.get_logger().info(
                f'Reached waypoint {self.current_wp_index + 1}/{len(self.waypoints)}'
            )
            self.current_wp_index += self.direction
            return

        # Pure pursuit: compute steering towards lookahead point
        # Transform target to robot frame
        local_x = dx * math.cos(-yaw) - dy * math.sin(-yaw)
        local_y = dx * math.sin(-yaw) + dy * math.cos(-yaw)

        # Curvature: kappa = 2 * y / L^2
        L = max(self.lookahead, distance)
        if L < 0.01:
            self._stop()
            return

        curvature = 2.0 * local_y / (L * L)

        # Convert to Twist command
        twist = Twist()

        # Linear speed: proportional to distance, slowing near waypoint
        speed_factor = min(1.0, distance / (self.lookahead * 2))
        twist.linear.x = self.max_linear * speed_factor

        # If target is behind us, reverse
        if local_x < 0:
            twist.linear.x = -twist.linear.x * 0.5  # Slower in reverse

        # Angular speed from curvature
        twist.angular.z = curvature * abs(twist.linear.x)
        twist.angular.z = max(-self.max_angular, min(self.max_angular, twist.angular.z))

        self.cmd_vel_pub.publish(twist)

    def _stop(self):
        """Publish zero velocity."""
        self.cmd_vel_pub.publish(Twist())

    def _publish_path(self):
        """Publish waypoints as a nav_msgs/Path for visualization."""
        path = Path()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = 'odom'

        for wx, wy in self.waypoints:
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = wx
            pose.pose.position.y = wy
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)

        self.path_pub.publish(path)

    def publish_status(self):
        """Publish current status as JSON."""
        status = {
            'state': self.state,
            'total_waypoints': len(self.waypoints),
            'current_index': self.current_wp_index,
            'position': list(self.current_pose) if self.current_pose else None,
        }

        msg = String()
        msg.data = json.dumps(status)
        self.status_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = WaypointFollowerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

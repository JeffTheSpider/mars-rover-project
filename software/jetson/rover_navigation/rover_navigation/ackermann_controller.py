#!/usr/bin/env python3
"""Ackermann steering controller for the Mars Rover.

Converts geometry_msgs/Twist (from teleop or Nav2) into wheel speed and
steering angle commands for the 6-wheel rocker-bogie drivetrain.

Supports 3 drive modes:
  0 = Ackermann (default) - car-like steering with 4-corner wheel articulation
  1 = Point turn - zero-radius spin (opposite wheel directions)
  2 = Crab walk - all wheels same angle, translate sideways

Rover dimensions (0.4 scale):
  Wheelbase: 360mm (front-rear axle distance)
  Track width: 280mm (left-right wheel spacing)
  L_fm: 180mm (front-to-mid axle)
  L_mr: 180mm (mid-to-rear axle)
  Max steering: +/-35 degrees
  Min turn radius: 397mm
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32
from rover_msgs.msg import WheelSpeeds, SteeringAngles


class AckermannControllerNode(Node):
    """Converts Twist commands to wheel speeds and steering angles."""

    # Drive modes
    MODE_ACKERMANN = 0
    MODE_POINT_TURN = 1
    MODE_CRAB = 2

    def __init__(self):
        super().__init__('ackermann_controller')

        # Rover geometry parameters (mm)
        self.declare_parameter('wheelbase_mm', 360.0)
        self.declare_parameter('track_width_mm', 280.0)
        self.declare_parameter('l_fm_mm', 180.0)
        self.declare_parameter('l_mr_mm', 180.0)
        self.declare_parameter('max_steering_deg', 35.0)
        self.declare_parameter('max_speed_mps', 0.56)
        self.declare_parameter('wheel_diameter_mm', 120.0)

        self.wheelbase = self.get_parameter('wheelbase_mm').get_parameter_value().double_value / 1000.0
        self.track = self.get_parameter('track_width_mm').get_parameter_value().double_value / 1000.0
        self.l_fm = self.get_parameter('l_fm_mm').get_parameter_value().double_value / 1000.0
        self.l_mr = self.get_parameter('l_mr_mm').get_parameter_value().double_value / 1000.0
        self.max_steer = math.radians(
            self.get_parameter('max_steering_deg').get_parameter_value().double_value
        )
        self.max_speed = self.get_parameter('max_speed_mps').get_parameter_value().double_value
        self.wheel_radius = self.get_parameter('wheel_diameter_mm').get_parameter_value().double_value / 2000.0

        self.half_track = self.track / 2.0

        # Minimum turn radius from max steering angle
        self.min_turn_radius = self.wheelbase / math.tan(self.max_steer)
        self.get_logger().info(f'Min turn radius: {self.min_turn_radius*1000:.0f}mm')

        # Current drive mode
        self.drive_mode = self.MODE_ACKERMANN

        # Subscribers
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.mode_sub = self.create_subscription(
            Int32, '/drive_mode', self.mode_callback, 10)

        # Publishers
        self.wheel_speeds_pub = self.create_publisher(
            WheelSpeeds, '/wheel_speeds', 10)
        self.steering_pub = self.create_publisher(
            SteeringAngles, '/steering_angles', 10)

        self.get_logger().info(
            f'Ackermann controller started: wheelbase={self.wheelbase*1000:.0f}mm, '
            f'track={self.track*1000:.0f}mm, max_steer={math.degrees(self.max_steer):.0f}deg, '
            f'max_speed={self.max_speed:.2f}m/s'
        )

    def mode_callback(self, msg: Int32):
        """Switch drive mode."""
        if msg.data in (self.MODE_ACKERMANN, self.MODE_POINT_TURN, self.MODE_CRAB):
            self.drive_mode = msg.data
            mode_names = {0: 'Ackermann', 1: 'Point Turn', 2: 'Crab Walk'}
            self.get_logger().info(f'Drive mode: {mode_names[self.drive_mode]}')

    def cmd_vel_callback(self, twist: Twist):
        """Convert Twist to wheel speeds and steering angles."""
        linear_x = max(-self.max_speed, min(self.max_speed, twist.linear.x))
        angular_z = twist.angular.z
        linear_y = twist.linear.y  # Used for crab walk

        if self.drive_mode == self.MODE_POINT_TURN:
            speeds, angles = self._point_turn(angular_z)
        elif self.drive_mode == self.MODE_CRAB:
            speeds, angles = self._crab_walk(linear_x, linear_y)
        else:
            speeds, angles = self._ackermann(linear_x, angular_z)

        # Publish wheel speeds
        ws = WheelSpeeds()
        ws.speeds = [float(s) for s in speeds]
        self.wheel_speeds_pub.publish(ws)

        # Publish steering angles (in degrees)
        sa = SteeringAngles()
        sa.angles = [float(math.degrees(a)) for a in angles]
        self.steering_pub.publish(sa)

    def _ackermann(self, linear: float, angular: float):
        """Standard Ackermann steering geometry.

        For a 6-wheel rover:
        - Front and rear wheels steer (4-wheel steering)
        - Middle wheels are fixed (0 deg steering)
        - Inner wheels turn more than outer (Ackermann principle)

        Returns:
            speeds: [FL, ML, RL, RR, MR, FR] as percentages
            angles: [FL, FR, RL, RR] as radians
        """
        max_steer = self.max_steer

        if abs(angular) < 0.001:
            # Straight line - no steering needed
            speed_pct = (linear / self.max_speed) * 100.0
            speeds = [speed_pct] * 6
            angles = [0.0, 0.0, 0.0, 0.0]
            return speeds, angles

        if abs(linear) < 0.001:
            # Pure rotation at low speed - use point turn
            return self._point_turn(angular)

        # Calculate turn radius from linear and angular velocity
        turn_radius = linear / angular  # Can be negative (turn direction)

        # Clamp to minimum turn radius
        if abs(turn_radius) < self.min_turn_radius:
            turn_radius = math.copysign(self.min_turn_radius, turn_radius)

        # Ackermann steering angles
        # Front wheels: steer towards turn centre
        # Rear wheels: steer opposite direction (counter-steer for tighter turns)
        front_centre_angle = math.atan2(self.l_fm, abs(turn_radius))
        rear_centre_angle = math.atan2(self.l_mr, abs(turn_radius))

        # Inner and outer wheel angles (Ackermann differentiation)
        if turn_radius > 0:  # Turning left
            fl_angle = math.atan2(self.l_fm, turn_radius - self.half_track)
            fr_angle = math.atan2(self.l_fm, turn_radius + self.half_track)
            rl_angle = -math.atan2(self.l_mr, turn_radius - self.half_track)
            rr_angle = -math.atan2(self.l_mr, turn_radius + self.half_track)
        else:  # Turning right
            r = abs(turn_radius)
            fl_angle = -math.atan2(self.l_fm, r + self.half_track)
            fr_angle = -math.atan2(self.l_fm, r - self.half_track)
            rl_angle = math.atan2(self.l_mr, r + self.half_track)
            rr_angle = math.atan2(self.l_mr, r - self.half_track)

        # Clamp steering angles
        fl_angle = max(-max_steer, min(max_steer, fl_angle))
        fr_angle = max(-max_steer, min(max_steer, fr_angle))
        rl_angle = max(-max_steer, min(max_steer, rl_angle))
        rr_angle = max(-max_steer, min(max_steer, rr_angle))

        angles = [fl_angle, fr_angle, rl_angle, rr_angle]

        # Calculate wheel speeds (outer wheels faster than inner)
        r = abs(turn_radius)
        base_speed = (linear / self.max_speed) * 100.0

        # Distance from ICR (instantaneous centre of rotation) for each wheel
        if turn_radius > 0:  # Left turn
            d_fl = math.hypot(self.l_fm, r - self.half_track)
            d_ml = r - self.half_track
            d_rl = math.hypot(self.l_mr, r - self.half_track)
            d_rr = math.hypot(self.l_mr, r + self.half_track)
            d_mr = r + self.half_track
            d_fr = math.hypot(self.l_fm, r + self.half_track)
        else:
            d_fl = math.hypot(self.l_fm, r + self.half_track)
            d_ml = r + self.half_track
            d_rl = math.hypot(self.l_mr, r + self.half_track)
            d_rr = math.hypot(self.l_mr, r - self.half_track)
            d_mr = r - self.half_track
            d_fr = math.hypot(self.l_fm, r - self.half_track)

        distances = [d_fl, d_ml, d_rl, d_rr, d_mr, d_fr]
        d_max = max(distances)

        # Normalize speeds so maximum is the commanded speed
        if d_max > 0:
            speeds = [(d / d_max) * base_speed for d in distances]
        else:
            speeds = [base_speed] * 6

        return speeds, angles

    def _point_turn(self, angular: float):
        """Zero-radius point turn. Left wheels backward, right forward (or vice versa).

        All 4 corner wheels angle at 45 degrees to form a circle.
        """
        speed_pct = (abs(angular) / 3.0) * 100.0  # Scale angular to percentage
        speed_pct = min(speed_pct, 100.0)

        if angular > 0:  # Turn left: right forward, left backward
            speeds = [-speed_pct, -speed_pct, -speed_pct,
                       speed_pct,  speed_pct,  speed_pct]
        else:  # Turn right: left forward, right backward
            speeds = [ speed_pct,  speed_pct,  speed_pct,
                      -speed_pct, -speed_pct, -speed_pct]

        # Point all steerable wheels at ~45 degrees towards centre
        angle = math.radians(35.0)  # Use max steering
        angles = [angle, -angle, -angle, angle]  # FL, FR, RL, RR

        return speeds, angles

    def _crab_walk(self, linear_x: float, linear_y: float):
        """Crab walk mode. All wheels point in the same direction.

        Useful for parallel parking or lateral movement.
        """
        # Calculate desired heading from x and y components
        if abs(linear_x) < 0.001 and abs(linear_y) < 0.001:
            speeds = [0.0] * 6
            angles = [0.0] * 4
            return speeds, angles

        heading = math.atan2(linear_y, linear_x)
        speed = math.hypot(linear_x, linear_y)
        speed_pct = (speed / self.max_speed) * 100.0
        speed_pct = min(speed_pct, 100.0)

        # Clamp heading to max steering angle
        heading = max(-self.max_steer, min(self.max_steer, heading))

        # All wheels same angle, all same speed
        speeds = [speed_pct] * 6
        angles = [heading, heading, heading, heading]

        return speeds, angles


def main(args=None):
    rclpy.init(args=args)
    node = AckermannControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

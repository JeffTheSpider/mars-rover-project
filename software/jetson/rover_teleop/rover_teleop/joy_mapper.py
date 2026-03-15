#!/usr/bin/env python3
"""Joystick/gamepad mapper node for the Mars Rover.

Maps gamepad inputs (sensor_msgs/Joy) to Twist commands for rover control.
Supports Xbox-style gamepads with dead-man switch safety.

Button mapping (Xbox controller):
  Left stick Y  -> linear.x (forward/backward)
  Right stick X -> angular.z (turn left/right)
  LB (button 4) -> dead-man switch (must hold to drive)
  RB (button 5) -> boost (2x speed)
  A (button 0)  -> toggle drive mode
  B (button 1)  -> e-stop
  X (button 2)  -> crab walk mode while held
  Y (button 3)  -> return to ackermann mode
  Start (7)     -> release e-stop
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, Int32


class JoyMapperNode(Node):
    """Maps joystick input to rover commands."""

    def __init__(self):
        super().__init__('joy_mapper')

        # Parameters
        self.declare_parameter('max_linear_speed', 0.56)
        self.declare_parameter('max_angular_speed', 1.5)
        self.declare_parameter('boost_multiplier', 1.5)
        self.declare_parameter('deadzone', 0.1)
        self.declare_parameter('linear_axis', 1)   # Left stick Y
        self.declare_parameter('angular_axis', 3)   # Right stick X
        self.declare_parameter('crab_axis', 0)      # Left stick X (for crab mode)
        self.declare_parameter('deadman_button', 4)  # LB
        self.declare_parameter('boost_button', 5)    # RB
        self.declare_parameter('mode_button', 0)     # A
        self.declare_parameter('estop_button', 1)    # B
        self.declare_parameter('crab_button', 2)     # X
        self.declare_parameter('reset_button', 3)    # Y
        self.declare_parameter('release_estop_button', 7)  # Start

        self.max_linear = self.get_parameter('max_linear_speed').get_parameter_value().double_value
        self.max_angular = self.get_parameter('max_angular_speed').get_parameter_value().double_value
        self.boost_mult = self.get_parameter('boost_multiplier').get_parameter_value().double_value
        self.deadzone = self.get_parameter('deadzone').get_parameter_value().double_value
        self.linear_axis = self.get_parameter('linear_axis').get_parameter_value().integer_value
        self.angular_axis = self.get_parameter('angular_axis').get_parameter_value().integer_value
        self.crab_axis = self.get_parameter('crab_axis').get_parameter_value().integer_value
        self.deadman_btn = self.get_parameter('deadman_button').get_parameter_value().integer_value
        self.boost_btn = self.get_parameter('boost_button').get_parameter_value().integer_value
        self.mode_btn = self.get_parameter('mode_button').get_parameter_value().integer_value
        self.estop_btn = self.get_parameter('estop_button').get_parameter_value().integer_value
        self.crab_btn = self.get_parameter('crab_button').get_parameter_value().integer_value
        self.reset_btn = self.get_parameter('reset_button').get_parameter_value().integer_value
        self.release_estop_btn = self.get_parameter('release_estop_button').get_parameter_value().integer_value

        # State
        self.current_mode = 0  # 0=ackermann, 1=point_turn, 2=crab
        self.prev_mode_btn = False
        self.estop_active = False

        # Subscribers
        self.joy_sub = self.create_subscription(
            Joy, '/joy', self.joy_callback, 10)

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.estop_pub = self.create_publisher(Bool, '/estop', 10)
        self.mode_pub = self.create_publisher(Int32, '/drive_mode', 10)

        self.get_logger().info('Joy mapper started, waiting for joystick input...')

    def _apply_deadzone(self, value: float) -> float:
        """Apply deadzone to axis value."""
        if abs(value) < self.deadzone:
            return 0.0
        # Rescale to 0-1 range after deadzone
        sign = 1.0 if value > 0 else -1.0
        return sign * (abs(value) - self.deadzone) / (1.0 - self.deadzone)

    def _get_button(self, msg: Joy, index: int) -> bool:
        """Safely get button state."""
        if index < len(msg.buttons):
            return msg.buttons[index] == 1
        return False

    def _get_axis(self, msg: Joy, index: int) -> float:
        """Safely get axis value."""
        if index < len(msg.axes):
            return msg.axes[index]
        return 0.0

    def joy_callback(self, msg: Joy):
        """Process joystick input."""
        # E-stop handling
        if self._get_button(msg, self.estop_btn):
            if not self.estop_active:
                self.estop_active = True
                estop = Bool()
                estop.data = True
                self.estop_pub.publish(estop)
                self.get_logger().warn('E-STOP activated via gamepad')
            return

        if self._get_button(msg, self.release_estop_btn) and self.estop_active:
            self.estop_active = False
            estop = Bool()
            estop.data = False
            self.estop_pub.publish(estop)
            self.get_logger().info('E-stop released via gamepad')
            return

        if self.estop_active:
            return

        # Mode toggle (A button - rising edge only)
        mode_pressed = self._get_button(msg, self.mode_btn)
        if mode_pressed and not self.prev_mode_btn:
            self.current_mode = (self.current_mode + 1) % 3
            mode_msg = Int32()
            mode_msg.data = self.current_mode
            self.mode_pub.publish(mode_msg)
            mode_names = {0: 'Ackermann', 1: 'Point Turn', 2: 'Crab Walk'}
            self.get_logger().info(f'Drive mode: {mode_names[self.current_mode]}')
        self.prev_mode_btn = mode_pressed

        # Reset to ackermann (Y button)
        if self._get_button(msg, self.reset_btn) and self.current_mode != 0:
            self.current_mode = 0
            mode_msg = Int32()
            mode_msg.data = 0
            self.mode_pub.publish(mode_msg)
            self.get_logger().info('Drive mode: Ackermann (reset)')

        # Dead-man switch required for driving
        if not self._get_button(msg, self.deadman_btn):
            self.cmd_vel_pub.publish(Twist())
            return

        # Temporary crab mode while X held
        if self._get_button(msg, self.crab_btn) and self.current_mode != 2:
            mode_msg = Int32()
            mode_msg.data = 2
            self.mode_pub.publish(mode_msg)

        # Build Twist
        twist = Twist()

        linear = self._apply_deadzone(self._get_axis(msg, self.linear_axis))
        angular = self._apply_deadzone(self._get_axis(msg, self.angular_axis))

        # Apply boost
        speed_mult = 1.0
        if self._get_button(msg, self.boost_btn):
            speed_mult = self.boost_mult

        twist.linear.x = linear * self.max_linear * speed_mult
        twist.angular.z = angular * self.max_angular * speed_mult

        # Crab walk: use left stick X for lateral
        if self._get_button(msg, self.crab_btn):
            crab = self._apply_deadzone(self._get_axis(msg, self.crab_axis))
            twist.linear.y = crab * self.max_linear * speed_mult

        # Clamp to max speeds
        twist.linear.x = max(-self.max_linear * self.boost_mult,
                             min(self.max_linear * self.boost_mult, twist.linear.x))
        twist.angular.z = max(-self.max_angular * self.boost_mult,
                              min(self.max_angular * self.boost_mult, twist.angular.z))

        self.cmd_vel_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = JoyMapperNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

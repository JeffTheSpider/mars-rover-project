#!/usr/bin/env python3
"""Mission planner node for the Mars Rover.

Manages autonomous missions using behaviour tree definitions.
Supports patrol, explore, and return-home missions with safety checks.
"""

import math
import time
import json
import xml.etree.ElementTree as ET
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool, String
from rover_msgs.msg import RoverStatus
from sensor_msgs.msg import BatteryState
from typing import Optional, List, Dict, Tuple
from enum import Enum
from ament_index_python.packages import get_package_share_directory
import os


class BTStatus(Enum):
    """Behaviour tree tick status."""
    SUCCESS = 'success'
    FAILURE = 'failure'
    RUNNING = 'running'


class BTNode:
    """Base class for behaviour tree nodes."""

    def __init__(self, name: str):
        self.name = name
        self.children: List['BTNode'] = []

    def tick(self, blackboard: dict) -> BTStatus:
        raise NotImplementedError


class SequenceNode(BTNode):
    """Ticks children in order. Fails on first failure."""

    def __init__(self, name: str):
        super().__init__(name)
        self.current_child = 0

    def tick(self, blackboard: dict) -> BTStatus:
        while self.current_child < len(self.children):
            status = self.children[self.current_child].tick(blackboard)
            if status == BTStatus.RUNNING:
                return BTStatus.RUNNING
            elif status == BTStatus.FAILURE:
                self.current_child = 0
                return BTStatus.FAILURE
            self.current_child += 1

        self.current_child = 0
        return BTStatus.SUCCESS


class FallbackNode(BTNode):
    """Ticks children in order. Succeeds on first success."""

    def __init__(self, name: str):
        super().__init__(name)
        self.current_child = 0

    def tick(self, blackboard: dict) -> BTStatus:
        while self.current_child < len(self.children):
            status = self.children[self.current_child].tick(blackboard)
            if status == BTStatus.RUNNING:
                return BTStatus.RUNNING
            elif status == BTStatus.SUCCESS:
                self.current_child = 0
                return BTStatus.SUCCESS
            self.current_child += 1

        self.current_child = 0
        return BTStatus.FAILURE


class RepeatNode(BTNode):
    """Repeats child N times (or forever if count=-1)."""

    def __init__(self, name: str, count: int = -1):
        super().__init__(name)
        self.count = count
        self.iterations = 0

    def tick(self, blackboard: dict) -> BTStatus:
        if not self.children:
            return BTStatus.FAILURE

        status = self.children[0].tick(blackboard)
        if status == BTStatus.RUNNING:
            return BTStatus.RUNNING

        self.iterations += 1
        if self.count > 0 and self.iterations >= self.count:
            self.iterations = 0
            return BTStatus.SUCCESS

        return BTStatus.RUNNING  # Keep repeating


class ConditionNode(BTNode):
    """Checks a condition in the blackboard."""

    def __init__(self, name: str, key: str, expected=True):
        super().__init__(name)
        self.key = key
        self.expected = expected

    def tick(self, blackboard: dict) -> BTStatus:
        value = blackboard.get(self.key, not self.expected)
        if value == self.expected:
            return BTStatus.SUCCESS
        return BTStatus.FAILURE


class ActionNode(BTNode):
    """Executes an action using the planner's action handlers."""

    def __init__(self, name: str, action_type: str, params: dict = None):
        super().__init__(name)
        self.action_type = action_type
        self.params = params or {}

    def tick(self, blackboard: dict) -> BTStatus:
        handler = blackboard.get(f'_action_{self.action_type}')
        if handler is None:
            return BTStatus.FAILURE
        return handler(self.params, blackboard)


class MissionPlannerNode(Node):
    """Manages autonomous missions using behaviour trees."""

    def __init__(self):
        super().__init__('mission_planner')

        # Parameters
        self.declare_parameter('default_behaviour_tree', 'patrol')
        self.declare_parameter('tick_rate', 10.0)
        self.declare_parameter('patrol_radius', 5.0)
        self.declare_parameter('patrol_points', 8)
        self.declare_parameter('safety_battery_min', 20)

        self.default_bt = self.get_parameter('default_behaviour_tree').get_parameter_value().string_value
        tick_rate = self.get_parameter('tick_rate').get_parameter_value().double_value
        self.patrol_radius = self.get_parameter('patrol_radius').get_parameter_value().double_value
        self.patrol_points = self.get_parameter('patrol_points').get_parameter_value().integer_value
        self.safety_battery_min = self.get_parameter('safety_battery_min').get_parameter_value().integer_value

        # State
        self.active = False
        self.current_bt: Optional[BTNode] = None
        self.blackboard: Dict = {}
        self.current_pose: Optional[Tuple[float, float, float]] = None
        self.rover_state: int = 0
        self.battery_pct: int = 100

        # Register action handlers in blackboard
        self.blackboard['_action_navigate_to'] = self._action_navigate_to
        self.blackboard['_action_wait'] = self._action_wait
        self.blackboard['_action_check_battery'] = self._action_check_battery
        self.blackboard['_action_return_home'] = self._action_return_home
        self.blackboard['_action_generate_patrol'] = self._action_generate_patrol
        self.blackboard['_action_explore_frontier'] = self._action_explore_frontier
        self.blackboard['_action_log'] = self._action_log

        # Subscribers
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.status_sub = self.create_subscription(
            RoverStatus, '/rover/status', self.status_callback, 10)
        self.battery_sub = self.create_subscription(
            BatteryState, '/battery', self.battery_callback, 10)
        self.activate_sub = self.create_subscription(
            Bool, '/mission/activate', self.activate_callback, 10)
        self.load_bt_sub = self.create_subscription(
            String, '/mission/load_bt', self.load_bt_callback, 10)

        # Publishers
        self.goal_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.mission_status_pub = self.create_publisher(String, '/mission/status', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Tick timer
        self.tick_timer = self.create_timer(1.0 / tick_rate, self.tick)

        # Status timer
        self.status_timer = self.create_timer(2.0, self.publish_status)

        self.get_logger().info(f'Mission planner ready, default BT: {self.default_bt}')

    def odom_callback(self, msg: Odometry):
        """Update current pose."""
        pos = msg.pose.pose.position
        orient = msg.pose.pose.orientation
        siny_cosp = 2.0 * (orient.w * orient.z + orient.x * orient.y)
        cosy_cosp = 1.0 - 2.0 * (orient.y * orient.y + orient.z * orient.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        self.current_pose = (pos.x, pos.y, yaw)
        self.blackboard['pose'] = self.current_pose

    def status_callback(self, msg: RoverStatus):
        """Update rover status (battery_pct from RoverStatus may not be populated)."""
        self.rover_state = msg.state
        self.blackboard['rover_state'] = msg.state

    def battery_callback(self, msg: BatteryState):
        """Update battery percentage from BatteryState topic."""
        self.battery_pct = int(msg.percentage * 100)
        self.blackboard['battery_pct'] = self.battery_pct
        self.blackboard['battery_ok'] = self.battery_pct > self.safety_battery_min

    def activate_callback(self, msg: Bool):
        """Activate or deactivate autonomous mode."""
        if msg.data and not self.active:
            self.active = True
            if self.current_bt is None:
                self._load_bt(self.default_bt)
            self.get_logger().info('Autonomous mode ACTIVATED')
        elif not msg.data and self.active:
            self.active = False
            self.cmd_vel_pub.publish(Twist())  # Stop
            self.get_logger().info('Autonomous mode DEACTIVATED')

    def load_bt_callback(self, msg: String):
        """Load a behaviour tree by name."""
        self._load_bt(msg.data)

    def _load_bt(self, bt_name: str):
        """Load a behaviour tree XML file."""
        try:
            bt_dir = os.path.join(
                get_package_share_directory('rover_autonomy'),
                'behaviour_trees'
            )
            bt_file = os.path.join(bt_dir, f'{bt_name}.xml')

            if not os.path.exists(bt_file):
                self.get_logger().error(f'BT file not found: {bt_file}')
                # Fall back to built-in simple patrol
                self.current_bt = self._build_simple_patrol()
                return

            tree = ET.parse(bt_file)
            root = tree.getroot()
            self.current_bt = self._parse_bt_xml(root[0])
            self.get_logger().info(f'Loaded behaviour tree: {bt_name}')

        except Exception as e:
            self.get_logger().error(f'Failed to load BT {bt_name}: {e}')
            self.current_bt = self._build_simple_patrol()

    def _parse_bt_xml(self, element) -> BTNode:
        """Parse an XML element into a BTNode."""
        tag = element.tag

        if tag == 'Sequence':
            node = SequenceNode(element.get('name', 'sequence'))
            for child in element:
                node.children.append(self._parse_bt_xml(child))
        elif tag == 'Fallback':
            node = FallbackNode(element.get('name', 'fallback'))
            for child in element:
                node.children.append(self._parse_bt_xml(child))
        elif tag == 'Repeat':
            count = int(element.get('num_cycles', '-1'))
            node = RepeatNode(element.get('name', 'repeat'), count)
            for child in element:
                node.children.append(self._parse_bt_xml(child))
        elif tag == 'Condition':
            node = ConditionNode(
                element.get('name', 'condition'),
                element.get('key', ''),
                element.get('expected', 'true').lower() == 'true'
            )
        elif tag == 'Action':
            params = {k: v for k, v in element.attrib.items()
                      if k not in ('name', 'type')}
            node = ActionNode(
                element.get('name', 'action'),
                element.get('type', ''),
                params
            )
        else:
            self.get_logger().warn(f'Unknown BT node type: {tag}')
            node = BTNode(f'unknown_{tag}')

        return node

    def _build_simple_patrol(self) -> BTNode:
        """Build a simple patrol behaviour tree programmatically."""
        root = SequenceNode('patrol_root')

        # Check battery
        battery_check = ConditionNode('check_battery', 'battery_ok')
        root.children.append(battery_check)

        # Generate patrol points
        gen_patrol = ActionNode('generate_patrol', 'generate_patrol')
        root.children.append(gen_patrol)

        # Navigate to each waypoint (repeat forever)
        patrol_loop = RepeatNode('patrol_loop', -1)
        nav = ActionNode('navigate_next', 'navigate_to', {'use_patrol_queue': 'true'})
        patrol_loop.children.append(nav)
        root.children.append(patrol_loop)

        return root

    def tick(self):
        """Tick the active behaviour tree."""
        if not self.active or self.current_bt is None:
            return

        # Safety check: abort if battery critical
        if self.battery_pct < 10:
            self.get_logger().error('CRITICAL: Battery below 10%! Returning home.')
            self.active = False
            self._action_return_home({}, self.blackboard)
            return

        status = self.current_bt.tick(self.blackboard)
        if status == BTStatus.SUCCESS:
            self.get_logger().info('Mission completed successfully')
        elif status == BTStatus.FAILURE:
            self.get_logger().warn('Mission failed, retrying...')

    def publish_status(self):
        """Publish mission planner status."""
        status = {
            'active': self.active,
            'bt_loaded': self.current_bt is not None,
            'battery_pct': self.battery_pct,
            'rover_state': self.rover_state,
            'position': list(self.current_pose) if self.current_pose else None,
        }
        msg = String()
        msg.data = json.dumps(status)
        self.mission_status_pub.publish(msg)

    # --- Action handlers ---

    def _action_navigate_to(self, params: dict, blackboard: dict) -> BTStatus:
        """Navigate to a target pose."""
        # Use patrol queue if specified
        if params.get('use_patrol_queue') == 'true':
            patrol_queue = blackboard.get('patrol_queue', [])
            if not patrol_queue:
                return BTStatus.SUCCESS  # All waypoints visited

            target = patrol_queue[0]
            x, y = target

            # Check if we've reached the target
            if self.current_pose is not None:
                dx = x - self.current_pose[0]
                dy = y - self.current_pose[1]
                if math.hypot(dx, dy) < 0.3:
                    blackboard['patrol_queue'] = patrol_queue[1:]
                    self.get_logger().info(
                        f'Reached patrol point, {len(patrol_queue) - 1} remaining'
                    )
                    return BTStatus.SUCCESS
        else:
            x = float(params.get('x', 0.0))
            y = float(params.get('y', 0.0))

        # Publish goal pose
        goal = PoseStamped()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.header.frame_id = 'map'
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.orientation.w = 1.0
        self.goal_pub.publish(goal)

        return BTStatus.RUNNING

    def _action_wait(self, params: dict, blackboard: dict) -> BTStatus:
        """Wait for a specified duration."""
        duration = float(params.get('seconds', 5.0))
        start_key = f'_wait_start_{id(params)}'

        if start_key not in blackboard:
            blackboard[start_key] = time.monotonic()

        elapsed = time.monotonic() - blackboard[start_key]
        if elapsed >= duration:
            del blackboard[start_key]
            return BTStatus.SUCCESS

        return BTStatus.RUNNING

    def _action_check_battery(self, params: dict, blackboard: dict) -> BTStatus:
        """Check if battery is above minimum threshold."""
        min_pct = int(params.get('min_pct', self.safety_battery_min))
        if blackboard.get('battery_pct', 100) >= min_pct:
            return BTStatus.SUCCESS
        return BTStatus.FAILURE

    def _action_return_home(self, params: dict, blackboard: dict) -> BTStatus:
        """Navigate back to home position (0, 0)."""
        params_copy = dict(params)
        params_copy['x'] = '0.0'
        params_copy['y'] = '0.0'
        return self._action_navigate_to(params_copy, blackboard)

    def _action_generate_patrol(self, params: dict, blackboard: dict) -> BTStatus:
        """Generate circular patrol waypoints around current position."""
        radius = float(params.get('radius', self.patrol_radius))
        num_points = int(params.get('points', self.patrol_points))

        cx, cy = 0.0, 0.0
        if self.current_pose:
            cx, cy = self.current_pose[0], self.current_pose[1]

        waypoints = []
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            waypoints.append((x, y))

        blackboard['patrol_queue'] = waypoints
        self.get_logger().info(f'Generated {num_points} patrol points, radius={radius}m')
        return BTStatus.SUCCESS

    def _action_explore_frontier(self, params: dict, blackboard: dict) -> BTStatus:
        """Explore unknown areas by navigating towards frontiers."""
        # Simplified frontier exploration: pick a random direction
        if self.current_pose is None:
            return BTStatus.FAILURE

        import random
        angle = random.uniform(0, 2 * math.pi)
        distance = float(params.get('explore_distance', 3.0))
        x = self.current_pose[0] + distance * math.cos(angle)
        y = self.current_pose[1] + distance * math.sin(angle)

        params_copy = {'x': str(x), 'y': str(y)}
        return self._action_navigate_to(params_copy, blackboard)

    def _action_log(self, params: dict, blackboard: dict) -> BTStatus:
        """Log a message."""
        message = params.get('message', 'BT action executed')
        self.get_logger().info(f'[BT] {message}')
        return BTStatus.SUCCESS


def main(args=None):
    rclpy.init(args=args)
    node = MissionPlannerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

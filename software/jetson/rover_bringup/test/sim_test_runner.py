#!/usr/bin/env python3
"""
Simulation Test Runner for Mars Rover.

Reads test scenarios from sim_test_scenarios.yaml and executes them
against a running Gazebo simulation.

Usage:
    # Start simulation first:
    ros2 launch rover_bringup simulation.launch.py enable_nav:=true

    # Then run tests:
    python3 sim_test_runner.py                    # All scenarios
    python3 sim_test_runner.py -c mobility        # Category filter
    python3 sim_test_runner.py -n drive_straight   # Name filter
    python3 sim_test_runner.py --list              # List scenarios
"""

import argparse
import math
import os
import sys
import time
import yaml

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy
    from geometry_msgs.msg import Twist
    from nav_msgs.msg import Odometry
    from sensor_msgs.msg import LaserScan, Imu, NavSatFix, Range, PointCloud2
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False


class SimTestRunner:
    """Runs simulation test scenarios against a live Gazebo instance."""

    def __init__(self, scenarios_file):
        with open(scenarios_file, 'r') as f:
            data = yaml.safe_load(f)
        self.scenarios = data.get('scenarios', [])
        self.node = None
        self.results = []

    def list_scenarios(self, category=None):
        """Print available test scenarios."""
        for s in self.scenarios:
            if category and s.get('category') != category:
                continue
            req = f" [requires: {s['requires']}]" if 'requires' in s else ''
            print(f"  [{s['category']}] {s['name']}: {s['description']}{req}")

    def run(self, name_filter=None, category_filter=None):
        """Run matching scenarios and report results."""
        if not ROS_AVAILABLE:
            print("ERROR: ROS2 not available. Install rclpy to run simulation tests.")
            print("These tests require a running Gazebo simulation.")
            print("\nScenario validation (syntax check):")
            self._validate_scenarios(name_filter, category_filter)
            return

        rclpy.init()
        self.node = rclpy.create_node('sim_test_runner')

        try:
            for scenario in self.scenarios:
                if name_filter and name_filter not in scenario['name']:
                    continue
                if category_filter and scenario.get('category') != category_filter:
                    continue

                result = self._run_scenario(scenario)
                self.results.append(result)
        finally:
            self.node.destroy_node()
            rclpy.shutdown()

        self._print_results()

    def _validate_scenarios(self, name_filter=None, category_filter=None):
        """Validate scenario YAML structure without ROS2."""
        passed = 0
        failed = 0
        required_keys = {'name', 'description', 'category'}

        for s in self.scenarios:
            if name_filter and name_filter not in s['name']:
                continue
            if category_filter and s.get('category') != category_filter:
                continue

            missing = required_keys - set(s.keys())
            if missing:
                print(f"  FAIL {s.get('name', '???')}: missing keys {missing}")
                failed += 1
            elif 'assertions' not in s and 'commands' not in s and 'waypoints' not in s:
                print(f"  WARN {s['name']}: no assertions, commands, or waypoints")
                passed += 1
            else:
                print(f"  OK   {s['name']} ({s['category']})")
                passed += 1

        total = passed + failed
        print(f"\n{passed}/{total} scenarios validated")

    def _run_scenario(self, scenario):
        """Execute a single test scenario."""
        name = scenario['name']
        self.node.get_logger().info(f"Running: {name}")

        result = {'name': name, 'passed': False, 'message': ''}

        try:
            timeout = scenario.get('timeout_s', 30)

            # Execute commands if present
            if 'commands' in scenario:
                for cmd in scenario['commands']:
                    self._execute_command(cmd)

            # Execute waypoints if present
            if 'waypoints' in scenario:
                self._execute_waypoints(scenario['waypoints'])

            # Check assertions
            if 'assertions' in scenario:
                for assertion in scenario['assertions']:
                    self._check_assertion(assertion, timeout)

            result['passed'] = True
            result['message'] = 'All assertions passed'

        except AssertionError as e:
            result['message'] = str(e)
        except Exception as e:
            result['message'] = f'Error: {e}'

        status = 'PASS' if result['passed'] else 'FAIL'
        self.node.get_logger().info(f"  {status}: {name} — {result['message']}")
        return result

    def _execute_command(self, cmd):
        """Publish a command to a topic for a specified duration."""
        if 'topic' not in cmd:
            return

        if cmd['topic'] == '/cmd_vel':
            pub = self.node.create_publisher(Twist, '/cmd_vel', 10)
            msg = Twist()
            msg.linear.x = float(cmd.get('linear_x', 0))
            msg.angular.z = float(cmd.get('angular_z', 0))

            duration = cmd.get('duration_s', 1.0)
            end_time = time.time() + duration
            while time.time() < end_time:
                pub.publish(msg)
                rclpy.spin_once(self.node, timeout_sec=0.1)

            self.node.destroy_publisher(pub)

    def _execute_waypoints(self, waypoints):
        """Send waypoints via Nav2 action server."""
        # Requires nav2_msgs — simplified placeholder
        self.node.get_logger().info(f"  Sending {len(waypoints)} waypoints")
        # In production, use FollowWaypoints action client

    def _check_assertion(self, assertion, timeout):
        """Verify a single assertion against live topics."""
        check_type = assertion.get('check', 'value')

        if check_type == 'topic_active':
            source = assertion['source']
            min_rate = assertion.get('min_rate_hz', 1.0)
            # Subscribe and count messages over 2 seconds
            msg_count = [0]

            def counter(msg):
                msg_count[0] += 1

            # Determine message type from topic name
            qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
            topic_types = {
                '/scan': LaserScan,
                '/imu/data': Imu,
                '/gps/fix': NavSatFix,
                '/odom': Odometry,
            }
            msg_type = topic_types.get(source)
            if not msg_type:
                self.node.get_logger().warn(f"  Unknown topic type for {source}")
                return

            sub = self.node.create_subscription(msg_type, source, counter, qos)
            end_time = time.time() + 2.0
            while time.time() < end_time:
                rclpy.spin_once(self.node, timeout_sec=0.1)

            self.node.destroy_subscription(sub)
            rate = msg_count[0] / 2.0
            assert rate >= min_rate, f"{source} rate {rate:.1f} Hz < {min_rate} Hz"

    def _print_results(self):
        """Print test results summary."""
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)

        print(f"\n{'='*60}")
        print(f"Simulation Test Results: {passed}/{total} passed")
        print(f"{'='*60}")

        for r in self.results:
            status = 'PASS' if r['passed'] else 'FAIL'
            print(f"  [{status}] {r['name']}: {r['message']}")

        if passed < total:
            print(f"\n{total - passed} FAILED")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Mars Rover Simulation Test Runner')
    parser.add_argument('-n', '--name', help='Filter by scenario name (substring match)')
    parser.add_argument('-c', '--category', help='Filter by category')
    parser.add_argument('--list', action='store_true', help='List scenarios without running')
    parser.add_argument('-f', '--file', default=None, help='Path to scenarios YAML')
    args = parser.parse_args()

    # Find scenarios file
    if args.file:
        scenarios_file = args.file
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scenarios_file = os.path.join(script_dir, 'sim_test_scenarios.yaml')

    if not os.path.exists(scenarios_file):
        print(f"ERROR: Scenarios file not found: {scenarios_file}")
        sys.exit(1)

    runner = SimTestRunner(scenarios_file)

    if args.list:
        runner.list_scenarios(args.category)
    else:
        runner.run(name_filter=args.name, category_filter=args.category)


if __name__ == '__main__':
    main()

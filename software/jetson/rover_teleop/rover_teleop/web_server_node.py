#!/usr/bin/env python3
"""WebSocket + HTTP server node for phone PWA teleoperation.

Serves a PWA frontend on port 8080 and accepts WebSocket control
commands on port 8081. Translates D-pad commands into ROS2 Twist
messages for rover control.

JSON protocol:
  {"cmd":"fwd","speed":50,"mode":0}
  {"cmd":"rev","speed":50,"mode":0}
  {"cmd":"left","speed":50,"mode":0}
  {"cmd":"right","speed":50,"mode":0}
  {"cmd":"stop"}
  {"cmd":"mode","mode":1}  # 0=ackermann, 1=point_turn, 2=crab
  {"cmd":"estop","active":true}

Status broadcast (1Hz):
  {"type":"status","battery":85,"state":2,"speed":0.3,"mode":0}
"""

import asyncio
import json
import threading
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, Int32, String
from sensor_msgs.msg import BatteryState
from rover_msgs.msg import RoverStatus
from typing import Set, Optional


class WebServerNode(Node):
    """WebSocket + HTTP server for PWA phone control."""

    def __init__(self):
        super().__init__('web_server')

        # Parameters
        self.declare_parameter('http_port', 8080)
        self.declare_parameter('ws_port', 8081)
        self.declare_parameter('max_linear_speed', 0.56)
        self.declare_parameter('max_angular_speed', 1.5)
        self.declare_parameter('command_timeout_ms', 500)

        self.http_port = self.get_parameter('http_port').get_parameter_value().integer_value
        self.ws_port = self.get_parameter('ws_port').get_parameter_value().integer_value
        self.max_linear = self.get_parameter('max_linear_speed').get_parameter_value().double_value
        self.max_angular = self.get_parameter('max_angular_speed').get_parameter_value().double_value
        self.cmd_timeout = self.get_parameter('command_timeout_ms').get_parameter_value().integer_value / 1000.0

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.estop_pub = self.create_publisher(Bool, '/estop', 10)
        self.mode_pub = self.create_publisher(Int32, '/drive_mode', 10)

        # Subscribers
        self.battery_sub = self.create_subscription(
            BatteryState, '/battery', self.battery_callback, 10)
        self.status_sub = self.create_subscription(
            RoverStatus, '/rover/status', self.status_callback, 10)

        # State for status broadcasts
        self.battery_pct = 100
        self.battery_voltage = 0.0
        self.rover_state = 0
        self.current_mode = 0
        self.current_speed = 0.0
        self.ws_clients: Set = set()
        self.ws_clients_lock = threading.Lock()
        self._ws_loop: Optional[asyncio.AbstractEventLoop] = None

        # Command timeout timer
        self.last_cmd_time = self.get_clock().now()
        self.timeout_timer = self.create_timer(0.1, self.check_timeout)

        # Status broadcast timer
        self.status_timer = self.create_timer(1.0, self.broadcast_status)

        # Start WebSocket server in background thread
        self.ws_thread = threading.Thread(target=self._run_ws_server, daemon=True)
        self.ws_thread.start()

        self.get_logger().info(
            f'Web server node started: HTTP={self.http_port}, WS={self.ws_port}'
        )

    def battery_callback(self, msg: BatteryState):
        """Update battery info."""
        self.battery_pct = int(msg.percentage * 100)
        self.battery_voltage = msg.voltage

    def status_callback(self, msg: RoverStatus):
        """Update rover status."""
        self.rover_state = msg.state

    def check_timeout(self):
        """Send stop if no commands received within timeout."""
        elapsed = (self.get_clock().now() - self.last_cmd_time).nanoseconds / 1e9
        if elapsed > self.cmd_timeout and self.current_speed > 0:
            self.cmd_vel_pub.publish(Twist())
            self.current_speed = 0.0

    def broadcast_status(self):
        """Broadcast status to all connected WebSocket clients."""
        with self.ws_clients_lock:
            client_count = len(self.ws_clients)
        status = {
            'type': 'status',
            'battery': self.battery_pct,
            'voltage': round(self.battery_voltage, 1),
            'state': self.rover_state,
            'speed': round(self.current_speed, 2),
            'mode': self.current_mode,
            'clients': client_count,
        }
        # Status is sent via the WebSocket event loop
        self._ws_broadcast(json.dumps(status))

    def handle_command(self, data: dict):
        """Process a command from the WebSocket client."""
        cmd = data.get('cmd', '')
        speed_pct = data.get('speed', 50) / 100.0  # 0-100 to 0-1
        mode = data.get('mode', self.current_mode)

        self.last_cmd_time = self.get_clock().now()

        if cmd == 'estop':
            estop = Bool()
            estop.data = data.get('active', True)
            self.estop_pub.publish(estop)
            self.get_logger().warn(f'E-stop: {estop.data}')
            return

        if cmd == 'mode':
            self.current_mode = mode
            mode_msg = Int32()
            mode_msg.data = mode
            self.mode_pub.publish(mode_msg)
            self.get_logger().info(f'Drive mode set to {mode}')
            return

        if cmd == 'stop':
            self.cmd_vel_pub.publish(Twist())
            self.current_speed = 0.0
            return

        twist = Twist()

        if cmd == 'fwd':
            twist.linear.x = self.max_linear * speed_pct
        elif cmd == 'rev':
            twist.linear.x = -self.max_linear * speed_pct
        elif cmd == 'left':
            twist.angular.z = self.max_angular * speed_pct
        elif cmd == 'right':
            twist.angular.z = -self.max_angular * speed_pct
        elif cmd == 'fwd_left':
            twist.linear.x = self.max_linear * speed_pct * 0.7
            twist.angular.z = self.max_angular * speed_pct * 0.5
        elif cmd == 'fwd_right':
            twist.linear.x = self.max_linear * speed_pct * 0.7
            twist.angular.z = -self.max_angular * speed_pct * 0.5
        elif cmd == 'rev_left':
            twist.linear.x = -self.max_linear * speed_pct * 0.7
            twist.angular.z = self.max_angular * speed_pct * 0.5
        elif cmd == 'rev_right':
            twist.linear.x = -self.max_linear * speed_pct * 0.7
            twist.angular.z = -self.max_angular * speed_pct * 0.5
        elif cmd == 'crab_left':
            twist.linear.y = self.max_linear * speed_pct
        elif cmd == 'crab_right':
            twist.linear.y = -self.max_linear * speed_pct
        else:
            self.get_logger().warn(f'Unknown command: {cmd}')
            return

        self.current_speed = abs(twist.linear.x) + abs(twist.angular.z)
        self.cmd_vel_pub.publish(twist)

    def _ws_broadcast(self, message: str):
        """Broadcast message to all connected WebSocket clients.

        Called from the ROS thread; schedules sends on the asyncio event loop.
        """
        loop = self._ws_loop
        if loop is None or loop.is_closed():
            return

        with self.ws_clients_lock:
            clients = list(self.ws_clients)

        for client in clients:
            try:
                asyncio.run_coroutine_threadsafe(client.send(message), loop)
            except Exception:
                pass

    def _run_ws_server(self):
        """Run the WebSocket server in a background thread."""
        try:
            import websockets
            import websockets.asyncio.server

            async def handler(websocket):
                with self.ws_clients_lock:
                    self.ws_clients.add(websocket)
                client_addr = websocket.remote_address
                self.get_logger().info(f'Client connected: {client_addr}')

                try:
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            self.handle_command(data)
                        except json.JSONDecodeError:
                            self.get_logger().warn(f'Invalid JSON: {message}')
                except Exception:
                    pass
                finally:
                    with self.ws_clients_lock:
                        self.ws_clients.discard(websocket)
                    self.get_logger().info(f'Client disconnected: {client_addr}')

            async def serve():
                self._ws_loop = asyncio.get_running_loop()
                async with websockets.asyncio.server.serve(handler, "0.0.0.0", self.ws_port):
                    self.get_logger().info(f'WebSocket server listening on port {self.ws_port}')
                    await asyncio.Future()  # Run forever

            asyncio.run(serve())

        except ImportError:
            self.get_logger().warn(
                'websockets package not installed. Install with: pip install websockets'
            )
            self.get_logger().info('WebSocket server disabled, using ROS topics only')
        except Exception as e:
            self.get_logger().error(f'WebSocket server error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = WebServerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

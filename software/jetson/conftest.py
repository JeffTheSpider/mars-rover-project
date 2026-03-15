"""Shared conftest: mock all ROS2 dependencies so tests run without ROS2 installed."""

import sys
import types
from unittest.mock import MagicMock


def _make_mock_module(name, attrs=None):
    """Create a mock module with optional attributes."""
    mod = types.ModuleType(name)
    if attrs:
        for k, v in attrs.items():
            setattr(mod, k, v)
    return mod


def _install_ros_mocks():
    """Install mock modules for rclpy and all ROS2 message packages."""
    # Skip if already real-installed
    if 'rclpy' in sys.modules and not isinstance(sys.modules['rclpy'], types.ModuleType):
        return

    # --- rclpy ---
    rclpy = _make_mock_module('rclpy')
    rclpy.init = MagicMock()
    rclpy.spin = MagicMock()
    rclpy.shutdown = MagicMock()

    # rclpy.node
    class _MockNode:
        def __init__(self, name='mock_node', **kwargs):
            self._name = name
            self._params = {}

        def get_logger(self):
            return MagicMock()

        def declare_parameter(self, name, value=None):
            self._params[name] = value

        def get_parameter(self, name):
            val = self._params.get(name)
            mock_param = MagicMock()
            pv = MagicMock()
            if isinstance(val, float):
                pv.double_value = val
            elif isinstance(val, int):
                pv.integer_value = val
                pv.double_value = float(val)
            elif isinstance(val, bool):
                pv.bool_value = val
            elif isinstance(val, str):
                pv.string_value = val
            elif isinstance(val, list):
                pv.double_array_value = val
            else:
                pv.double_value = 0.0
                pv.integer_value = 0
                pv.bool_value = False
                pv.string_value = ''
            mock_param.get_parameter_value.return_value = pv
            return mock_param

        def create_subscription(self, *args, **kwargs):
            return MagicMock()

        def create_publisher(self, *args, **kwargs):
            return MagicMock()

        def create_timer(self, *args, **kwargs):
            return MagicMock()

        def get_clock(self):
            return MagicMock()

        def destroy_node(self):
            pass

    rclpy_node = _make_mock_module('rclpy.node', {'Node': _MockNode})

    rclpy_action = _make_mock_module('rclpy.action', {'ActionClient': MagicMock})

    rclpy_qos = _make_mock_module('rclpy.qos', {
        'QoSProfile': MagicMock,
        'ReliabilityPolicy': MagicMock(),
        'HistoryPolicy': MagicMock(),
    })

    # --- geometry_msgs ---
    class _Twist:
        def __init__(self):
            self.linear = MagicMock(x=0.0, y=0.0, z=0.0)
            self.angular = MagicMock(x=0.0, y=0.0, z=0.0)

    class _PoseStamped:
        def __init__(self):
            self.header = MagicMock()
            self.pose = MagicMock()

    class _PoseArray:
        def __init__(self):
            self.poses = []

    geometry_msg = _make_mock_module('geometry_msgs')
    geometry_msgs_msg = _make_mock_module('geometry_msgs.msg', {
        'Twist': _Twist,
        'PoseStamped': _PoseStamped,
        'PoseArray': _PoseArray,
    })

    # --- std_msgs ---
    class _Bool:
        def __init__(self):
            self.data = False

    class _Int32:
        def __init__(self):
            self.data = 0

    class _String:
        def __init__(self):
            self.data = ''

    class _Header:
        def __init__(self):
            self.stamp = MagicMock()
            self.frame_id = ''

    std_msgs = _make_mock_module('std_msgs')
    std_msgs_msg = _make_mock_module('std_msgs.msg', {
        'Bool': _Bool,
        'Int32': _Int32,
        'String': _String,
        'Header': _Header,
    })

    # --- nav_msgs ---
    class _Odometry:
        def __init__(self):
            self.pose = MagicMock()

    class _Path:
        def __init__(self):
            self.header = MagicMock()
            self.poses = []

    nav_msgs = _make_mock_module('nav_msgs')
    nav_msgs_msg = _make_mock_module('nav_msgs.msg', {
        'Odometry': _Odometry,
        'Path': _Path,
    })

    # --- sensor_msgs ---
    class _Image:
        def __init__(self):
            self.header = MagicMock()
            self.height = 0
            self.width = 0
            self.encoding = 'rgb8'
            self.is_bigendian = False
            self.step = 0
            self.data = b''

    class _CameraInfo:
        def __init__(self):
            self.header = MagicMock()
            self.width = 0
            self.height = 0
            self.distortion_model = ''
            self.d = []
            self.k = []
            self.r = []
            self.p = []

    class _NavSatFix:
        def __init__(self):
            self.latitude = 0.0
            self.longitude = 0.0
            self.status = MagicMock(status=0)

    class _BatteryState:
        def __init__(self):
            self.percentage = 1.0
            self.voltage = 12.0

    sensor_msgs = _make_mock_module('sensor_msgs')
    sensor_msgs_msg = _make_mock_module('sensor_msgs.msg', {
        'Image': _Image,
        'CameraInfo': _CameraInfo,
        'NavSatFix': _NavSatFix,
        'BatteryState': _BatteryState,
    })

    # --- rover_msgs ---
    class _WheelSpeeds:
        def __init__(self):
            self.speeds = []

    class _SteeringAngles:
        def __init__(self):
            self.angles = []

    class _Detection:
        def __init__(self):
            self.class_name = ''
            self.confidence = 0.0
            self.bbox = []
            self.distance = -1.0

    class _RoverStatus:
        def __init__(self):
            self.state = 0
            self.battery_pct = 100

    rover_msgs = _make_mock_module('rover_msgs')
    rover_msgs_msg = _make_mock_module('rover_msgs.msg', {
        'WheelSpeeds': _WheelSpeeds,
        'SteeringAngles': _SteeringAngles,
        'Detection': _Detection,
        'RoverStatus': _RoverStatus,
    })

    # --- ament_index_python ---
    ament_index = _make_mock_module('ament_index_python')
    ament_index_packages = _make_mock_module('ament_index_python.packages', {
        'get_package_share_directory': MagicMock(return_value='/tmp/rover_autonomy'),
    })

    # Register all mock modules
    mock_modules = {
        'rclpy': rclpy,
        'rclpy.node': rclpy_node,
        'rclpy.action': rclpy_action,
        'rclpy.qos': rclpy_qos,
        'geometry_msgs': geometry_msg,
        'geometry_msgs.msg': geometry_msgs_msg,
        'std_msgs': std_msgs,
        'std_msgs.msg': std_msgs_msg,
        'nav_msgs': nav_msgs,
        'nav_msgs.msg': nav_msgs_msg,
        'sensor_msgs': sensor_msgs,
        'sensor_msgs.msg': sensor_msgs_msg,
        'rover_msgs': rover_msgs,
        'rover_msgs.msg': rover_msgs_msg,
        'ament_index_python': ament_index,
        'ament_index_python.packages': ament_index_packages,
    }

    for name, mod in mock_modules.items():
        sys.modules[name] = mod


# Install mocks at import time so all test files can import ROS2 node modules
_install_ros_mocks()

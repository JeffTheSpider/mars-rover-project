"""Launch file for teleoperation: hardware + web server + Ackermann controller."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    bringup_dir = get_package_share_directory('rover_bringup')

    # Launch arguments
    serial_port_arg = DeclareLaunchArgument(
        'serial_port',
        default_value='/dev/ttyTHS1',
        description='Serial port for ESP32 UART communication'
    )

    web_port_arg = DeclareLaunchArgument(
        'web_port',
        default_value='8080',
        description='HTTP port for PWA web server'
    )

    ws_port_arg = DeclareLaunchArgument(
        'ws_port',
        default_value='8081',
        description='WebSocket port for real-time control'
    )

    max_speed_arg = DeclareLaunchArgument(
        'max_speed',
        default_value='0.56',
        description='Maximum linear speed in m/s (0.56 = 2km/h at 0.4 scale)'
    )

    # Include hardware launch
    hardware_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'hardware.launch.py')
        ),
        launch_arguments={
            'serial_port': LaunchConfiguration('serial_port'),
        }.items(),
    )

    # Ackermann controller - converts Twist to wheel/steering commands
    ackermann_controller_node = Node(
        package='rover_navigation',
        executable='ackermann_controller',
        name='ackermann_controller',
        output='screen',
        parameters=[{
            'wheelbase_mm': 360.0,
            'track_width_mm': 280.0,
            'l_fm_mm': 180.0,
            'l_mr_mm': 180.0,
            'max_steering_deg': 35.0,
            'max_speed_mps': LaunchConfiguration('max_speed'),
        }],
    )

    # Web server for PWA phone control
    web_server_node = Node(
        package='rover_teleop',
        executable='web_server_node',
        name='web_server',
        output='screen',
        parameters=[{
            'http_port': LaunchConfiguration('web_port'),
            'ws_port': LaunchConfiguration('ws_port'),
        }],
    )

    # Joy mapper for gamepad control (optional)
    joy_mapper_node = Node(
        package='rover_teleop',
        executable='joy_mapper',
        name='joy_mapper',
        output='screen',
        parameters=[{
            'max_linear_speed': LaunchConfiguration('max_speed'),
            'max_angular_speed': 1.5,
        }],
    )

    return LaunchDescription([
        serial_port_arg,
        web_port_arg,
        ws_port_arg,
        max_speed_arg,
        hardware_launch,
        ackermann_controller_node,
        web_server_node,
        joy_mapper_node,
    ])

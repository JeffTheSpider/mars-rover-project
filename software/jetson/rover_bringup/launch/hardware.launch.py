"""Launch file for hardware-level nodes: UART bridge + robot state publisher."""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Launch arguments
    serial_port_arg = DeclareLaunchArgument(
        'serial_port',
        default_value='/dev/ttyTHS1',
        description='Serial port for ESP32 UART communication'
    )

    baud_rate_arg = DeclareLaunchArgument(
        'baud_rate',
        default_value='115200',
        description='UART baud rate'
    )

    use_sim_arg = DeclareLaunchArgument(
        'use_sim',
        default_value='false',
        description='Use simulated hardware (no serial port required)'
    )

    # UART bridge node - communicates with ESP32 motor controller
    uart_bridge_node = Node(
        package='rover_hardware',
        executable='uart_bridge_node',
        name='uart_bridge',
        output='screen',
        parameters=[{
            'serial_port': LaunchConfiguration('serial_port'),
            'baud_rate': LaunchConfiguration('baud_rate'),
            'command_rate_hz': 50,
            'watchdog_timeout_ms': 200,
            'ping_interval_ms': 1000,
        }],
        remappings=[
            ('/encoders', '/joint_states'),
        ],
    )

    # Robot state publisher - broadcasts URDF transforms
    # TODO: Replace with actual URDF file path once CAD model is exported
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': '<robot name="rover"><link name="base_link"/></robot>',
            'publish_frequency': 50.0,
        }],
    )

    return LaunchDescription([
        serial_port_arg,
        baud_rate_arg,
        use_sim_arg,
        uart_bridge_node,
        robot_state_publisher_node,
    ])

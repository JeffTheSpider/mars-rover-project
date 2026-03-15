"""Master launch file: brings up all rover subsystems."""

import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    GroupAction,
    LogInfo,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    bringup_dir = get_package_share_directory('rover_bringup')

    # Launch arguments
    enable_nav_arg = DeclareLaunchArgument(
        'enable_nav',
        default_value='true',
        description='Enable navigation stack (EKF + Nav2)'
    )

    enable_perception_arg = DeclareLaunchArgument(
        'enable_perception',
        default_value='true',
        description='Enable perception stack (cameras + YOLO)'
    )

    enable_autonomy_arg = DeclareLaunchArgument(
        'enable_autonomy',
        default_value='false',
        description='Enable autonomous mission planner (default off for safety)'
    )

    serial_port_arg = DeclareLaunchArgument(
        'serial_port',
        default_value='/dev/ttyTHS1',
        description='Serial port for ESP32 UART communication'
    )

    # Startup banner
    startup_log = LogInfo(
        msg='=== MARS ROVER GARDEN ROBOT - FULL SYSTEM STARTUP ==='
    )

    # Navigation stack (includes teleop which includes hardware)
    nav_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'nav.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('enable_nav')),
    )

    # Teleop only (when nav is disabled, still need hardware + teleop)
    teleop_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'teleop.launch.py')
        ),
        condition=IfCondition(
            PythonExpression(["not ", LaunchConfiguration('enable_nav')])
        ),
        launch_arguments={
            'serial_port': LaunchConfiguration('serial_port'),
        }.items(),
    )

    # Perception stack
    perception_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'perception.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('enable_perception')),
    )

    # Autonomy (mission planner)
    autonomy_node = Node(
        package='rover_autonomy',
        executable='mission_planner',
        name='mission_planner',
        output='screen',
        condition=IfCondition(LaunchConfiguration('enable_autonomy')),
        parameters=[{
            'default_behaviour_tree': 'patrol',
        }],
    )

    return LaunchDescription([
        enable_nav_arg,
        enable_perception_arg,
        enable_autonomy_arg,
        serial_port_arg,
        startup_log,
        nav_launch,
        teleop_launch,
        perception_launch,
        autonomy_node,
    ])

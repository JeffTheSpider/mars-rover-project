"""Launch file for Gazebo simulation with the Mars Rover.

Spawns the rover URDF in Gazebo, launches robot_state_publisher,
and optionally includes the navigation stack for testing.

Usage:
  ros2 launch rover_bringup simulation.launch.py
  ros2 launch rover_bringup simulation.launch.py enable_nav:=true
  ros2 launch rover_bringup simulation.launch.py world:=garden.world
"""

import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    bringup_dir = get_package_share_directory('rover_bringup')
    xacro_file = os.path.join(bringup_dir, 'urdf', 'rover.urdf.xacro')
    ekf_params_file = os.path.join(bringup_dir, 'config', 'ekf.yaml')

    # Launch arguments
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='',
        description='Path to Gazebo world file (empty = default empty world)'
    )

    enable_nav_arg = DeclareLaunchArgument(
        'enable_nav',
        default_value='false',
        description='Launch navigation stack (EKF + Nav2)'
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch rviz2 for visualization'
    )

    # Robot description from xacro
    robot_description = Command(['xacro ', xacro_file])

    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
    )

    # Launch Gazebo
    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so',
             LaunchConfiguration('world')],
        output='screen',
    )

    # Spawn rover in Gazebo
    spawn_rover = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_rover',
        output='screen',
        arguments=[
            '-topic', '/robot_description',
            '-entity', 'mars_rover',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1',  # Slightly above ground to avoid collision at spawn
        ],
    )

    # Ackermann controller (converts cmd_vel to wheel speeds + steering)
    ackermann_node = Node(
        package='rover_navigation',
        executable='ackermann_controller',
        name='ackermann_controller',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'wheelbase_mm': 360.0,
            'track_width_mm': 280.0,
            'max_speed_mps': 0.56,
            'wheel_diameter_mm': 80.0,
        }],
    )

    # Geofence (25m radius for simulation)
    geofence_node = Node(
        package='rover_navigation',
        executable='geofence_node',
        name='geofence',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'fence_radius': 25.0,
            'warn_margin': 3.0,
        }],
    )

    # Teleop keyboard (for manual testing)
    teleop_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_keyboard',
        output='screen',
        prefix='xterm -e',  # Launch in separate terminal
        parameters=[{
            'use_sim_time': True,
        }],
        remappings=[
            ('/cmd_vel', '/cmd_vel'),
        ],
    )

    # Local EKF (odom frame, no GPS)
    ekf_local_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_local',
        output='screen',
        parameters=[ekf_params_file, {'use_sim_time': True}],
        remappings=[
            ('odometry/filtered', '/odom'),
        ],
    )

    return LaunchDescription([
        world_arg,
        enable_nav_arg,
        use_rviz_arg,
        gazebo,
        robot_state_publisher_node,
        spawn_rover,
        ackermann_node,
        geofence_node,
        ekf_local_node,
    ])

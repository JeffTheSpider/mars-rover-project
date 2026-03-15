"""Launch file for navigation: teleop + EKF + SLAM + Nav2."""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    bringup_dir = get_package_share_directory('rover_bringup')
    ekf_params_file = os.path.join(bringup_dir, 'config', 'ekf.yaml')
    nav2_params_file = os.path.join(bringup_dir, 'config', 'nav2_params.yaml')

    # Launch arguments
    use_slam_arg = DeclareLaunchArgument(
        'use_slam',
        default_value='true',
        description='Use SLAM for mapping (false = use existing map)'
    )

    map_file_arg = DeclareLaunchArgument(
        'map_file',
        default_value='',
        description='Path to map file for localization mode'
    )

    # Include teleop launch (which includes hardware)
    teleop_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'teleop.launch.py')
        ),
    )

    # Dual EKF architecture (see EA-13, ros2-architecture-research.md)
    # Local EKF: odom→base_link, smooth, no GPS — used by controllers
    ekf_local_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_local',
        output='screen',
        parameters=[ekf_params_file],
        remappings=[
            ('odometry/filtered', '/odom'),
        ],
    )

    # Global EKF: map→odom, includes GPS — may jump on GPS correction
    ekf_global_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_global',
        output='screen',
        parameters=[ekf_params_file],
        remappings=[
            ('odometry/filtered', '/odom/global'),
        ],
    )

    # NavSat transform: converts GPS NavSatFix → odometry for ekf_global
    navsat_transform_node = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform',
        output='screen',
        parameters=[ekf_params_file],
        remappings=[
            ('imu', '/imu/data'),
            ('gps/fix', '/gps/fix'),
            ('odometry/filtered', '/odom/global'),
            ('odometry/gps', '/odometry/gps'),
        ],
    )

    # Geofence safety node
    geofence_node = Node(
        package='rover_navigation',
        executable='geofence_node',
        name='geofence',
        output='screen',
        parameters=[{
            'fence_radius': 25.0,
            'home_lat': 0.0,
            'home_lon': 0.0,
            'warn_margin': 3.0,
        }],
    )

    # Waypoint follower
    waypoint_follower_node = Node(
        package='rover_navigation',
        executable='waypoint_follower',
        name='waypoint_follower',
        output='screen',
        parameters=[{
            'waypoint_tolerance': 0.3,
            'lookahead_distance': 0.5,
        }],
    )

    return LaunchDescription([
        use_slam_arg,
        map_file_arg,
        teleop_launch,
        ekf_local_node,
        ekf_global_node,
        navsat_transform_node,
        geofence_node,
        waypoint_follower_node,
    ])

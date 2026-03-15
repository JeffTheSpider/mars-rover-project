"""Launch file for perception: cameras + YOLO detection + depth processing."""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    bringup_dir = get_package_share_directory('rover_bringup')
    camera_params_file = os.path.join(bringup_dir, 'config', 'camera_params.yaml')

    # Launch arguments
    yolo_model_arg = DeclareLaunchArgument(
        'yolo_model',
        default_value='yolov8n.pt',
        description='YOLO model file path (nano for Jetson performance)'
    )

    confidence_arg = DeclareLaunchArgument(
        'confidence_threshold',
        default_value='0.5',
        description='YOLO detection confidence threshold'
    )

    enable_depth_arg = DeclareLaunchArgument(
        'enable_depth',
        default_value='true',
        description='Enable depth estimation from stereo/mono cameras'
    )

    # Camera manager - handles multiple camera sources
    camera_manager_node = Node(
        package='rover_perception',
        executable='camera_manager',
        name='camera_manager',
        output='screen',
        parameters=[
            camera_params_file,
            {
                'front_camera_id': 0,
                'rear_camera_id': 1,
                'publish_rate': 15.0,
                'image_width': 640,
                'image_height': 480,
            },
        ],
    )

    # YOLO object detection node
    yolo_node = Node(
        package='rover_perception',
        executable='yolo_node',
        name='yolo_detector',
        output='screen',
        parameters=[{
            'model_path': LaunchConfiguration('yolo_model'),
            'confidence_threshold': LaunchConfiguration('confidence_threshold'),
            'device': 'cuda:0',
            'input_topic': '/camera/front/image_raw',
            'max_detections': 20,
        }],
    )

    # Depth processor
    depth_processor_node = Node(
        package='rover_perception',
        executable='depth_processor',
        name='depth_processor',
        output='screen',
        parameters=[{
            'enable': LaunchConfiguration('enable_depth'),
            'method': 'monocular',
            'max_range': 10.0,
        }],
    )

    return LaunchDescription([
        yolo_model_arg,
        confidence_arg,
        enable_depth_arg,
        camera_manager_node,
        yolo_node,
        depth_processor_node,
    ])

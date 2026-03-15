#!/usr/bin/env python3
"""Camera manager node for the Mars Rover.

Manages multiple camera sources (USB/CSI), handles frame capture,
and publishes images as ROS2 Image messages with CameraInfo.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo

import numpy as np
import time
from typing import Optional


class CameraManagerNode(Node):
    """Manages camera devices and publishes images."""

    def __init__(self):
        super().__init__('camera_manager')

        # Parameters
        self.declare_parameter('front_camera_id', 0)
        self.declare_parameter('rear_camera_id', 1)
        self.declare_parameter('publish_rate', 15.0)
        self.declare_parameter('image_width', 640)
        self.declare_parameter('image_height', 480)

        self.front_id = self.get_parameter('front_camera_id').get_parameter_value().integer_value
        self.rear_id = self.get_parameter('rear_camera_id').get_parameter_value().integer_value
        publish_rate = self.get_parameter('publish_rate').get_parameter_value().double_value
        self.width = self.get_parameter('image_width').get_parameter_value().integer_value
        self.height = self.get_parameter('image_height').get_parameter_value().integer_value

        # Camera intrinsics from parameters (loaded via camera_params.yaml)
        self.declare_parameter('front_camera.camera_matrix',
                               [500.0, 0.0, 320.0, 0.0, 500.0, 240.0, 0.0, 0.0, 1.0])
        self.declare_parameter('front_camera.distortion_coefficients',
                               [0.0, 0.0, 0.0, 0.0, 0.0])
        self.declare_parameter('front_camera.frame_id', 'front_camera_optical')

        # Publishers
        self.front_image_pub = self.create_publisher(
            Image, '/camera/front/image_raw', 5)
        self.front_info_pub = self.create_publisher(
            CameraInfo, '/camera/front/camera_info', 5)
        self.rear_image_pub = self.create_publisher(
            Image, '/camera/rear/image_raw', 5)
        self.rear_info_pub = self.create_publisher(
            CameraInfo, '/camera/rear/camera_info', 5)

        # Camera capture objects
        self.front_cap = None
        self.rear_cap = None
        self._open_cameras()

        # Build CameraInfo message
        self.front_camera_info = self._build_camera_info('front_camera')

        # Capture timer
        period = 1.0 / publish_rate
        self.capture_timer = self.create_timer(period, self.capture_and_publish)

        self.get_logger().info(
            f'Camera manager started: front={self.front_id}, rear={self.rear_id}, '
            f'rate={publish_rate}Hz, resolution={self.width}x{self.height}'
        )

    def _open_cameras(self):
        """Open camera devices using OpenCV."""
        try:
            import cv2
            # Front camera - try GStreamer pipeline for CSI on Jetson
            gst_pipeline = (
                f'nvarguscamerasrc sensor-id={self.front_id} ! '
                f'video/x-raw(memory:NVMM), width={self.width}, height={self.height}, '
                f'framerate=30/1 ! nvvidconv ! video/x-raw, format=BGRx ! '
                f'videoconvert ! video/x-raw, format=BGR ! appsink drop=1'
            )

            # Try GStreamer first, fall back to V4L2
            self.front_cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
            if not self.front_cap.isOpened():
                self.get_logger().warn('GStreamer failed, trying V4L2 for front camera')
                self.front_cap = cv2.VideoCapture(self.front_id)
                if self.front_cap.isOpened():
                    self.front_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                    self.front_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

            if self.front_cap.isOpened():
                self.get_logger().info(f'Front camera opened (id={self.front_id})')
            else:
                self.get_logger().warn('Front camera not available - publishing test pattern')
                self.front_cap = None

            # Rear camera - V4L2 (typically USB)
            self.rear_cap = cv2.VideoCapture(self.rear_id)
            if self.rear_cap.isOpened():
                self.rear_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.rear_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.get_logger().info(f'Rear camera opened (id={self.rear_id})')
            else:
                self.get_logger().warn('Rear camera not available')
                self.rear_cap = None

        except ImportError:
            self.get_logger().error('OpenCV not installed - running without cameras')
            self.front_cap = None
            self.rear_cap = None

    def _build_camera_info(self, camera_name: str) -> CameraInfo:
        """Build CameraInfo message from parameters."""
        info = CameraInfo()

        matrix = self.get_parameter(f'{camera_name}.camera_matrix').get_parameter_value().double_array_value
        dist = self.get_parameter(f'{camera_name}.distortion_coefficients').get_parameter_value().double_array_value
        frame_id = self.get_parameter(f'{camera_name}.frame_id').get_parameter_value().string_value

        info.header.frame_id = frame_id
        info.width = self.width
        info.height = self.height
        info.distortion_model = 'plumb_bob'
        info.d = list(dist)

        # 3x3 camera matrix (row-major)
        info.k = list(matrix)

        # Rectification matrix (identity for monocular)
        info.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]

        # Projection matrix (3x4)
        info.p = [
            matrix[0], matrix[1], matrix[2], 0.0,
            matrix[3], matrix[4], matrix[5], 0.0,
            matrix[6], matrix[7], matrix[8], 0.0,
        ]

        return info

    def capture_and_publish(self):
        """Capture frames from cameras and publish."""
        stamp = self.get_clock().now().to_msg()

        # Front camera
        frame = self._capture_frame(self.front_cap)
        if frame is None:
            frame = self._test_pattern(stamp)

        img_msg = self._numpy_to_ros_image(frame, 'front_camera_optical', stamp)
        self.front_image_pub.publish(img_msg)

        self.front_camera_info.header.stamp = stamp
        self.front_info_pub.publish(self.front_camera_info)

        # Rear camera
        rear_frame = self._capture_frame(self.rear_cap)
        if rear_frame is not None:
            rear_msg = self._numpy_to_ros_image(rear_frame, 'rear_camera_optical', stamp)
            self.rear_image_pub.publish(rear_msg)

    def _capture_frame(self, cap) -> Optional[np.ndarray]:
        """Capture a single frame from camera."""
        if cap is None or not cap.isOpened():
            return None

        ret, frame = cap.read()
        if not ret:
            return None

        return frame

    def _test_pattern(self, stamp) -> np.ndarray:
        """Generate a test pattern image when no camera is available."""
        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Gradient pattern
        for y in range(self.height):
            for x in range(0, self.width, 40):
                col = int((x / self.width) * 255)
                row = int((y / self.height) * 255)
                w = min(40, self.width - x)
                image[y, x:x+w] = [col, row, 128]

        return image

    def _numpy_to_ros_image(self, frame: np.ndarray, frame_id: str, stamp) -> Image:
        """Convert numpy array to ROS Image message."""
        msg = Image()
        msg.header.stamp = stamp
        msg.header.frame_id = frame_id
        msg.height = frame.shape[0]
        msg.width = frame.shape[1]
        msg.encoding = 'bgr8'
        msg.is_bigendian = False
        msg.step = frame.shape[1] * 3
        msg.data = frame.tobytes()
        return msg

    def destroy_node(self):
        """Release camera resources on shutdown."""
        if self.front_cap is not None:
            self.front_cap.release()
        if self.rear_cap is not None:
            self.rear_cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CameraManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

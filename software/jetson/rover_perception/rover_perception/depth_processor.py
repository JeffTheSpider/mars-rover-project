#!/usr/bin/env python3
"""Depth estimation processor for the Mars Rover.

Provides monocular depth estimation or stereo depth processing
to generate distance information for detected objects.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from rover_msgs.msg import Detection

import numpy as np
from typing import Optional
import time


class DepthProcessorNode(Node):
    """Processes camera images to estimate depth/distance."""

    def __init__(self):
        super().__init__('depth_processor')

        # Parameters
        self.declare_parameter('enable', True)
        self.declare_parameter('method', 'monocular')  # 'monocular', 'stereo', 'rgbd'
        self.declare_parameter('max_range', 10.0)
        self.declare_parameter('focal_length_px', 500.0)

        self.enabled = self.get_parameter('enable').get_parameter_value().bool_value
        self.method = self.get_parameter('method').get_parameter_value().string_value
        self.max_range = self.get_parameter('max_range').get_parameter_value().double_value
        self.focal_length = self.get_parameter('focal_length_px').get_parameter_value().double_value

        # Known object heights for monocular distance estimation (metres)
        self.known_heights = {
            'person': 1.7,
            'dog': 0.5,
            'cat': 0.3,
            'car': 1.5,
            'bicycle': 1.0,
            'chair': 0.8,
        }

        # Monocular depth model (MiDaS or similar)
        self.depth_model = None
        self.depth_transform = None
        if self.enabled and self.method == 'monocular':
            self._load_depth_model()

        # QoS
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/front/image_raw',
            self.image_callback,
            sensor_qos,
        )

        self.detection_sub = self.create_subscription(
            Detection,
            '/detections',
            self.detection_callback,
            10,
        )

        # Publishers
        self.depth_image_pub = self.create_publisher(
            Image, '/camera/front/depth', 1)
        self.detection_with_depth_pub = self.create_publisher(
            Detection, '/detections_with_depth', 10)

        # State
        self.latest_depth_map: Optional[np.ndarray] = None
        self.latest_image_shape = (480, 640)

        self.get_logger().info(
            f'Depth processor initialized: method={self.method}, '
            f'enabled={self.enabled}, max_range={self.max_range}m'
        )

    def _load_depth_model(self):
        """Load monocular depth estimation model."""
        try:
            import torch
            self.get_logger().info('Loading MiDaS depth model...')
            self.depth_model = torch.hub.load('intel-isl/MiDaS', 'MiDaS_small')
            # Set model to inference mode
            self.depth_model.train(False)

            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.depth_model = self.depth_model.to(device)

            # Load transforms
            midas_transforms = torch.hub.load('intel-isl/MiDaS', 'transforms')
            self.depth_transform = midas_transforms.small_transform

            self.get_logger().info(f'MiDaS model loaded on {device}')
        except Exception as e:
            self.get_logger().warn(f'Could not load depth model: {e}')
            self.get_logger().info('Using geometric depth estimation fallback')
            self.depth_model = None

    def image_callback(self, msg: Image):
        """Process image for depth estimation."""
        if not self.enabled:
            return

        self.latest_image_shape = (msg.height, msg.width)

        if self.depth_model is not None:
            try:
                self._run_depth_inference(msg)
            except Exception as e:
                self.get_logger().error(f'Depth inference failed: {e}')

    def _run_depth_inference(self, msg: Image):
        """Run monocular depth estimation on the image."""
        import torch

        # Convert ROS image to numpy
        image = np.frombuffer(msg.data, dtype=np.uint8).reshape(
            msg.height, msg.width, 3
        )
        if msg.encoding == 'bgr8':
            image = image[:, :, ::-1].copy()  # BGR to RGB

        # Run MiDaS
        input_batch = self.depth_transform(image)
        device = next(self.depth_model.parameters()).device
        input_batch = input_batch.to(device)

        with torch.no_grad():
            prediction = self.depth_model(input_batch)

        # Resize to original dimensions
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=image.shape[:2],
            mode='bicubic',
            align_corners=False,
        ).squeeze()

        depth_map = prediction.cpu().numpy()

        # Normalize to metric depth (approximate)
        depth_range = depth_map.max() - depth_map.min() + 1e-6
        depth_map = self.max_range * (depth_map - depth_map.min()) / depth_range

        self.latest_depth_map = depth_map

        # Publish depth image
        depth_msg = Image()
        depth_msg.header = msg.header
        depth_msg.height = depth_map.shape[0]
        depth_msg.width = depth_map.shape[1]
        depth_msg.encoding = '32FC1'
        depth_msg.is_bigendian = False
        depth_msg.step = depth_map.shape[1] * 4
        depth_msg.data = depth_map.astype(np.float32).tobytes()
        self.depth_image_pub.publish(depth_msg)

    def detection_callback(self, det: Detection):
        """Add depth information to incoming detections."""
        if not self.enabled:
            self.detection_with_depth_pub.publish(det)
            return

        enriched = Detection()
        enriched.class_name = det.class_name
        enriched.confidence = det.confidence
        enriched.bbox = det.bbox

        # Try depth map lookup first
        if self.latest_depth_map is not None:
            cx = det.bbox[0] + det.bbox[2] // 2
            cy = det.bbox[1] + det.bbox[3] // 2

            h, w = self.latest_depth_map.shape
            if 0 <= cx < w and 0 <= cy < h:
                # Sample a small region around centre for robustness
                x1 = max(0, cx - 5)
                x2 = min(w, cx + 5)
                y1 = max(0, cy - 5)
                y2 = min(h, cy + 5)
                region = self.latest_depth_map[y1:y2, x1:x2]
                enriched.distance = float(np.median(region))
                self.detection_with_depth_pub.publish(enriched)
                return

        # Fallback: geometric estimation using known object heights
        if det.class_name in self.known_heights and det.bbox[3] > 0:
            real_height = self.known_heights[det.class_name]
            pixel_height = det.bbox[3]
            distance = (real_height * self.focal_length) / pixel_height
            enriched.distance = min(float(distance), self.max_range)
        else:
            enriched.distance = -1.0

        self.detection_with_depth_pub.publish(enriched)


def main(args=None):
    rclpy.init(args=args)
    node = DepthProcessorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

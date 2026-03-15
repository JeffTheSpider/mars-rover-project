#!/usr/bin/env python3
"""YOLO object detection node for the Mars Rover.

Subscribes to camera images, runs YOLOv8 inference (GPU-accelerated on Jetson),
and publishes Detection messages with bounding boxes and class names.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from rover_msgs.msg import Detection
from std_msgs.msg import Header

import numpy as np
from typing import List, Optional
import time


class YoloDetectorNode(Node):
    """Runs YOLOv8 inference on camera images and publishes detections."""

    def __init__(self):
        super().__init__('yolo_detector')

        # Parameters
        self.declare_parameter('model_path', 'yolov8n.pt')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('device', 'cuda:0')
        self.declare_parameter('input_topic', '/camera/front/image_raw')
        self.declare_parameter('max_detections', 20)
        self.declare_parameter('inference_size', 640)

        self.model_path = self.get_parameter('model_path').get_parameter_value().string_value
        self.conf_threshold = self.get_parameter('confidence_threshold').get_parameter_value().double_value
        self.device = self.get_parameter('device').get_parameter_value().string_value
        input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        self.max_detections = self.get_parameter('max_detections').get_parameter_value().integer_value
        self.inference_size = self.get_parameter('inference_size').get_parameter_value().integer_value

        # Load YOLO model
        self.model = None
        self._load_model()

        # QoS for camera images - best effort to keep up with frame rate
        image_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # Subscriber
        self.image_sub = self.create_subscription(
            Image,
            input_topic,
            self.image_callback,
            image_qos,
        )

        # Publishers
        self.detection_pub = self.create_publisher(Detection, '/detections', 10)
        self.annotated_pub = self.create_publisher(Image, '/camera/front/detections_image', 1)

        # Performance tracking
        self.inference_times: List[float] = []
        self.frame_count = 0

        # Stats timer
        self.stats_timer = self.create_timer(10.0, self.log_stats)

        self.get_logger().info(
            f'YOLO detector initialized: model={self.model_path}, '
            f'device={self.device}, conf={self.conf_threshold}'
        )

    def _load_model(self):
        """Load YOLOv8 model. Falls back to CPU if CUDA unavailable."""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)

            # Warm up with a dummy image
            dummy = np.zeros((self.inference_size, self.inference_size, 3), dtype=np.uint8)
            self.model.predict(dummy, device=self.device, verbose=False)

            self.get_logger().info(f'YOLO model loaded on {self.device}')
        except ImportError:
            self.get_logger().error(
                'ultralytics not installed. Install with: pip install ultralytics'
            )
            self.get_logger().warn('Running in MOCK mode - generating fake detections')
        except Exception as e:
            self.get_logger().error(f'Failed to load model on {self.device}: {e}')
            if 'cuda' in self.device:
                self.get_logger().warn('Falling back to CPU')
                self.device = 'cpu'
                self._load_model()

    def image_callback(self, msg: Image):
        """Process incoming camera image through YOLO."""
        self.frame_count += 1

        # Convert ROS Image to numpy array
        try:
            image = self._ros_image_to_numpy(msg)
        except Exception as e:
            self.get_logger().error(f'Image conversion failed: {e}')
            return

        start_time = time.monotonic()

        if self.model is not None:
            # Real YOLO inference
            try:
                results = self.model.predict(
                    image,
                    device=self.device,
                    conf=self.conf_threshold,
                    max_det=self.max_detections,
                    verbose=False,
                )
                self._publish_results(results[0], msg.header)
            except Exception as e:
                self.get_logger().error(f'Inference failed: {e}')
        else:
            # Mock mode - publish a fake detection for testing
            if self.frame_count % 30 == 0:
                det = Detection()
                det.class_name = 'person'
                det.confidence = 0.85
                det.bbox = [100, 100, 200, 300]
                det.distance = 2.5
                self.detection_pub.publish(det)

        elapsed = time.monotonic() - start_time
        self.inference_times.append(elapsed)

    def _publish_results(self, result, header: Header):
        """Extract detections from YOLO result and publish."""
        if result.boxes is None or len(result.boxes) == 0:
            return

        for box in result.boxes:
            det = Detection()
            det.class_name = result.names[int(box.cls[0])]
            det.confidence = float(box.conf[0])

            # Bounding box as [x, y, width, height]
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            det.bbox = [int(x1), int(y1), int(x2 - x1), int(y2 - y1)]

            # Distance estimation (simple pinhole model approximation)
            # Real depth requires stereo camera or depth sensor
            det.distance = -1.0

            self.detection_pub.publish(det)

        self.get_logger().debug(f'Published {len(result.boxes)} detections')

    def _ros_image_to_numpy(self, msg: Image) -> np.ndarray:
        """Convert ROS Image message to numpy array without cv_bridge dependency."""
        if msg.encoding == 'rgb8':
            image = np.frombuffer(msg.data, dtype=np.uint8).reshape(
                msg.height, msg.width, 3
            ).copy()
        elif msg.encoding == 'bgr8':
            image = np.frombuffer(msg.data, dtype=np.uint8).reshape(
                msg.height, msg.width, 3
            ).copy()
            image = image[:, :, ::-1]  # BGR to RGB
        elif msg.encoding == 'mono8':
            grey = np.frombuffer(msg.data, dtype=np.uint8).reshape(
                msg.height, msg.width
            )
            image = np.stack([grey, grey, grey], axis=-1)
        else:
            raise ValueError(f'Unsupported image encoding: {msg.encoding}')

        return image

    def log_stats(self):
        """Log inference performance statistics."""
        if not self.inference_times:
            return

        avg_ms = np.mean(self.inference_times) * 1000
        max_ms = np.max(self.inference_times) * 1000
        fps = len(self.inference_times) / sum(self.inference_times) if sum(self.inference_times) > 0 else 0

        self.get_logger().info(
            f'YOLO stats: avg={avg_ms:.1f}ms, max={max_ms:.1f}ms, '
            f'fps={fps:.1f}, frames={self.frame_count}'
        )
        self.inference_times.clear()


def main(args=None):
    rclpy.init(args=args)
    node = YoloDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

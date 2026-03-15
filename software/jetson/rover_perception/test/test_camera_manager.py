"""Unit tests for the camera manager node.

Tests image conversion, test pattern generation, and CameraInfo building
without a running ROS2 system or real cameras.
"""

import numpy as np
import pytest
from rover_perception.camera_manager import CameraManagerNode
from rover_perception.yolo_node import YoloDetectorNode


@pytest.fixture
def camera_node():
    """Create a CameraManagerNode (cameras will fail to open, which is fine)."""
    return CameraManagerNode()


@pytest.fixture
def yolo_node():
    """Create a YoloDetectorNode (model won't load, runs in mock mode)."""
    return YoloDetectorNode()


# ===== Test pattern generation =====

class TestTestPattern:
    """Verify the fallback test pattern image."""

    def test_pattern_shape(self, camera_node):
        from unittest.mock import MagicMock
        stamp = MagicMock()
        pattern = camera_node._test_pattern(stamp)
        assert pattern.shape == (480, 640, 3)
        assert pattern.dtype == np.uint8

    def test_pattern_not_all_black(self, camera_node):
        from unittest.mock import MagicMock
        stamp = MagicMock()
        pattern = camera_node._test_pattern(stamp)
        assert pattern.sum() > 0


# ===== numpy to ROS Image conversion =====

class TestNumpyToRosImage:
    """Test the _numpy_to_ros_image helper."""

    def test_bgr8_conversion(self, camera_node):
        frame = np.zeros((100, 200, 3), dtype=np.uint8)
        frame[50, 100] = [255, 0, 0]  # Blue pixel in BGR

        from unittest.mock import MagicMock
        msg = camera_node._numpy_to_ros_image(frame, 'test_frame', MagicMock())
        assert msg.height == 100
        assert msg.width == 200
        assert msg.encoding == 'bgr8'
        assert msg.step == 200 * 3
        assert len(msg.data) == 100 * 200 * 3

    def test_frame_id_set(self, camera_node):
        frame = np.zeros((10, 10, 3), dtype=np.uint8)
        from unittest.mock import MagicMock
        msg = camera_node._numpy_to_ros_image(frame, 'my_camera', MagicMock())
        assert msg.header.frame_id == 'my_camera'


# ===== ROS Image to numpy conversion (YOLO node) =====

class TestRosImageToNumpy:
    """Test the _ros_image_to_numpy helper on the YOLO node."""

    def test_rgb8_roundtrip(self, yolo_node):
        from unittest.mock import MagicMock
        original = np.arange(48, dtype=np.uint8).reshape(4, 4, 3)
        msg = MagicMock()
        msg.encoding = 'rgb8'
        msg.height = 4
        msg.width = 4
        msg.data = original.tobytes()

        result = yolo_node._ros_image_to_numpy(msg)
        np.testing.assert_array_equal(result, original)

    def test_bgr8_converts_to_rgb(self, yolo_node):
        from unittest.mock import MagicMock
        bgr = np.zeros((2, 2, 3), dtype=np.uint8)
        bgr[0, 0] = [255, 0, 0]  # Blue in BGR -> should become [0, 0, 255] in RGB

        msg = MagicMock()
        msg.encoding = 'bgr8'
        msg.height = 2
        msg.width = 2
        msg.data = bgr.tobytes()

        result = yolo_node._ros_image_to_numpy(msg)
        np.testing.assert_array_equal(result[0, 0], [0, 0, 255])

    def test_mono8_expands_to_3_channels(self, yolo_node):
        from unittest.mock import MagicMock
        grey = np.array([[100, 200], [50, 150]], dtype=np.uint8)
        msg = MagicMock()
        msg.encoding = 'mono8'
        msg.height = 2
        msg.width = 2
        msg.data = grey.tobytes()

        result = yolo_node._ros_image_to_numpy(msg)
        assert result.shape == (2, 2, 3)
        assert result[0, 0, 0] == 100
        assert result[0, 0, 1] == 100
        assert result[0, 0, 2] == 100

    def test_unsupported_encoding_raises(self, yolo_node):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.encoding = 'rgba16'
        msg.height = 1
        msg.width = 1
        msg.data = b'\x00' * 8

        with pytest.raises(ValueError, match='Unsupported image encoding'):
            yolo_node._ros_image_to_numpy(msg)


# ===== CameraInfo building =====

class TestCameraInfo:
    """Test _build_camera_info produces valid CameraInfo."""

    def test_camera_info_dimensions(self, camera_node):
        info = camera_node.front_camera_info
        assert info.width == 640
        assert info.height == 480

    def test_camera_info_distortion_model(self, camera_node):
        info = camera_node.front_camera_info
        assert info.distortion_model == 'plumb_bob'

    def test_camera_info_has_matrix(self, camera_node):
        info = camera_node.front_camera_info
        assert len(info.k) == 9  # 3x3 camera matrix
        assert len(info.r) == 9  # 3x3 rectification matrix
        assert len(info.p) == 12  # 3x4 projection matrix

    def test_rectification_is_identity(self, camera_node):
        info = camera_node.front_camera_info
        expected = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        assert info.r == expected


# ===== YOLO inference stats =====

class TestYoloStats:
    """Test performance tracking helpers."""

    def test_inference_times_initially_empty(self, yolo_node):
        assert len(yolo_node.inference_times) == 0

    def test_frame_count_initially_zero(self, yolo_node):
        assert yolo_node.frame_count == 0

    def test_log_stats_with_empty_times(self, yolo_node):
        """log_stats should not crash with empty list."""
        yolo_node.log_stats()  # Should return early without error

    def test_log_stats_computes_averages(self, yolo_node):
        """log_stats should compute and clear times."""
        yolo_node.inference_times = [0.01, 0.02, 0.03]
        yolo_node.log_stats()
        assert len(yolo_node.inference_times) == 0  # Cleared after logging

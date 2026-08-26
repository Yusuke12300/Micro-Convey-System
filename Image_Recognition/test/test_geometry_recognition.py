from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
from xml.etree import ElementTree

import numpy as np


def _connected_components(mask, connectivity=8):
    del connectivity
    height, width = mask.shape
    labels = np.zeros_like(mask, dtype=np.int32)
    statistics = [[0, 0, width, height, int(np.count_nonzero(mask == 0))]]
    centers = [[0.0, 0.0]]
    label = 0
    for start_y in range(height):
        for start_x in range(width):
            if mask[start_y, start_x] == 0 or labels[start_y, start_x] != 0:
                continue
            label += 1
            stack = [(start_y, start_x)]
            labels[start_y, start_x] = label
            pixels = []
            while stack:
                y, x = stack.pop()
                pixels.append((y, x))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if (
                            0 <= ny < height
                            and 0 <= nx < width
                            and mask[ny, nx] != 0
                            and labels[ny, nx] == 0
                        ):
                            labels[ny, nx] = label
                            stack.append((ny, nx))
            ys = np.asarray([item[0] for item in pixels])
            xs = np.asarray([item[1] for item in pixels])
            statistics.append(
                [
                    int(xs.min()),
                    int(ys.min()),
                    int(np.ptp(xs) + 1),
                    int(np.ptp(ys) + 1),
                    len(pixels),
                ]
            )
            centers.append([float(xs.mean()), float(ys.mean())])
    return label + 1, labels, np.asarray(statistics), np.asarray(centers)


cv2 = ModuleType("cv2")
cv2.MORPH_OPEN = 1
cv2.MORPH_CLOSE = 2
cv2.CC_STAT_LEFT = 0
cv2.CC_STAT_TOP = 1
cv2.CC_STAT_WIDTH = 2
cv2.CC_STAT_HEIGHT = 3
cv2.CC_STAT_AREA = 4
cv2.COLOR_BGR2HSV = 40
cv2.COLOR_BGR2GRAY = 6
cv2.morphologyEx = lambda image, operation, kernel: image
cv2.connectedComponentsWithStats = _connected_components
cv2.minAreaRect = lambda points: (
    tuple(np.mean(points, axis=0)),
    (float(np.ptp(points[:, 0])), float(np.ptp(points[:, 1]))),
    0.0,
)


def _convert_color_for_test(image, conversion):
    if conversion == cv2.COLOR_BGR2GRAY:
        return np.mean(image, axis=2).astype(np.uint8)
    value = np.max(image, axis=2).astype(np.uint8)
    minimum = np.min(image, axis=2).astype(np.float32)
    saturation = np.zeros_like(value)
    nonzero = value > 0
    saturation[nonzero] = np.clip(
        255.0 * (value[nonzero].astype(np.float32) - minimum[nonzero])
        / value[nonzero],
        0,
        255,
    ).astype(np.uint8)
    hue = np.zeros_like(value)
    return np.dstack((hue, saturation, value))


def _canny_for_test(image, low_threshold, high_threshold):
    del high_threshold
    image = image.astype(np.int16)
    edges = np.zeros(image.shape, dtype=np.uint8)
    horizontal = np.abs(image[:, 1:] - image[:, :-1]) >= low_threshold
    vertical = np.abs(image[1:, :] - image[:-1, :]) >= low_threshold
    edges[:, 1:][horizontal] = 255
    edges[:, :-1][horizontal] = 255
    edges[1:, :][vertical] = 255
    edges[:-1, :][vertical] = 255
    return edges


cv2.cvtColor = _convert_color_for_test
cv2.GaussianBlur = lambda image, kernel_size, sigma: image
cv2.Canny = _canny_for_test
cv2.inRange = lambda image, lower, upper: (
    np.all((image >= lower) & (image <= upper), axis=2).astype(np.uint8) * 255
)
sys.modules.setdefault("cv2", cv2)
sys.modules.setdefault("yaml", SimpleNamespace(safe_load=lambda stream: {}))

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from geometry_recognition import (  # noqa: E402
    CameraIntrinsics,
    DetectionSample,
    DetectorSettings,
    camera_to_arm,
    detect_target_from_depth,
    dimension_confidence,
    depth_edge_mask,
    edge_support_ratio,
    fit_plane_ransac,
    load_arm_camera_transform,
    measure_visible_face,
    normalize_target_id,
    select_best_sample,
    select_stable_best_sample,
)


class GeometryRecognitionTests(unittest.TestCase):
    def test_rtc_builder_port_contract_is_unchanged(self):
        document = ElementTree.parse(PROJECT_ROOT / "RTC.xml")
        ports = []
        for element in document.getroot().iter():
            if element.tag.endswith("DataPorts"):
                attributes = {
                    key.split("}")[-1]: value for key, value in element.attrib.items()
                }
                ports.append(
                    (attributes["name"], attributes["type"], attributes["portType"])
                )
        self.assertEqual(
            ports,
            [
                ("Target_In1", "RTC::TimedString", "DataInPort"),
                ("Target_Coordinate_Out", "RTC::TimedPoint3D", "DataOutPort"),
            ],
        )
        source = (PROJECT_ROOT / "Image_Recognition.py").read_text(encoding="utf-8-sig")
        self.assertIn(
            'self._d_Target = OpenRTM_aist.instantiateDataType(RTC.TimedString)',
            source,
        )
        self.assertIn(
            'self._Target_In1In = OpenRTM_aist.InPort("Target_In1", self._d_Target)',
            source,
        )
        self.assertIn(
            'self._d_Coordinate = OpenRTM_aist.instantiateDataType(RTC.TimedPoint3D)',
            source,
        )
        self.assertIn(
            'OpenRTM_aist.OutPort("Target_Coordinate_Out", self._d_Coordinate)',
            source,
        )

    def test_target_id_and_best_sample(self):
        self.assertEqual(normalize_target_id("  [t1]\n"), "[T1]")
        self.assertEqual(normalize_target_id("t1"), "[T1]")
        self.assertEqual(normalize_target_id(" T4 "), "[T4]")
        samples = [
            DetectionSample(0.70, (1.0, 2.0, 3.0), 1.0),
            DetectionSample(0.92, (4.0, 5.0, 6.0), 2.0),
        ]
        self.assertEqual(select_best_sample(samples), samples[1])

    def test_stable_cluster_rejects_high_confidence_moving_outlier(self):
        samples = [
            DetectionSample(0.80, (0.000, 0.000, 0.550), 1.0),
            DetectionSample(0.88, (0.003, -0.002, 0.552), 2.0),
            DetectionSample(0.84, (-0.002, 0.001, 0.548), 3.0),
            DetectionSample(0.99, (0.120, 0.080, 0.450), 4.0),
        ]
        self.assertEqual(
            select_stable_best_sample(samples, 0.012, 3), samples[1]
        )
        self.assertIsNone(select_stable_best_sample(samples, 0.001, 3))

    def test_dimension_matching(self):
        confidence = dimension_confidence(
            [15.5, 44.0, 34.0], [15.0, 45.0, 33.0], 8.0, 0.35
        )
        self.assertIsNotNone(confidence)
        self.assertGreater(confidence, 0.9)
        self.assertIsNone(
            dimension_confidence([60, 70, 80], [15, 45, 33], 8.0, 0.35)
        )

    def test_plane_fit(self):
        yy, xx = np.mgrid[-0.2:0.2:20j, -0.2:0.2:20j]
        points = np.column_stack((xx.ravel(), yy.ravel(), np.ones(xx.size)))
        plane = fit_plane_ransac(
            points, 30, 0.001, 0.8, np.random.default_rng(1)
        )
        self.assertIsNotNone(plane)
        normal, offset = plane
        self.assertGreater(float(normal @ np.asarray([0.0, 0.0, -1.0])), 0.99)
        self.assertAlmostEqual(offset, 1.0, places=5)

    def test_synthetic_cuboid_detection(self):
        depth = np.ones((100, 100), dtype=np.float32)
        depth[36:64, 45:55] = 0.967
        settings = DetectorSettings(
            roi_xyxy=(0, 0, 100, 100),
            plane_sample_stride=2,
            plane_ransac_iterations=40,
            plane_distance_threshold_m=0.002,
            min_plane_inlier_ratio=0.8,
            object_min_height_m=0.005,
            object_max_height_m=0.08,
            min_component_area_px=20,
            morphology_kernel_px=1,
            dimension_abs_tolerance_mm=8.0,
            dimension_relative_tolerance=0.35,
        )
        detection = detect_target_from_depth(
            depth,
            CameraIntrinsics(600.0, 600.0, 49.5, 49.5),
            "[T1]",
            {"enabled": True, "dimensions_mm": [15.0, 45.0, 33.0]},
            settings,
            0.6,
            np.random.default_rng(2),
        )
        self.assertIsNotNone(detection)
        self.assertGreaterEqual(detection.confidence, 0.6)
        self.assertAlmostEqual(detection.point_camera_m[2], 0.967, places=2)
        x1, y1, x2, y2 = detection.bounding_box_xyxy
        self.assertLessEqual(x1, 50)
        self.assertLessEqual(y1, 50)
        self.assertGreaterEqual(x2, 50)
        self.assertGreaterEqual(y2, 50)

    def test_largest_visible_face_is_accepted_and_narrow_face_is_rejected(self):
        settings = DetectorSettings(
            roi_xyxy=(0, 0, 100, 100),
            plane_sample_stride=2,
            plane_ransac_iterations=50,
            plane_distance_threshold_m=0.002,
            min_plane_inlier_ratio=0.75,
            object_min_height_m=0.010,
            object_max_height_m=0.085,
            min_component_area_px=50,
            morphology_kernel_px=1,
            dimension_abs_tolerance_mm=8.0,
            dimension_relative_tolerance=0.35,
            min_rectangularity=0.40,
        )
        definition = {
            "enabled": True,
            "dimensions_mm": [15.0, 45.0, 33.0],
            "visible_face": {
                "dimensions_mm": [45.0, 33.0],
                "absolute_tolerance_mm": 8.0,
                "relative_tolerance": 0.30,
                "confidence_weight": 0.35,
            },
        }
        intrinsics = CameraIntrinsics(600.0, 600.0, 49.5, 49.5)

        broad_face_depth = np.ones((100, 100), dtype=np.float32)
        broad_face_depth[36:64, 40:60] = 0.985
        detection = detect_target_from_depth(
            broad_face_depth,
            intrinsics,
            "[T1]",
            definition,
            settings,
            0.60,
            np.random.default_rng(10),
        )
        self.assertIsNotNone(detection)
        self.assertIsNotNone(detection.visible_face_confidence)
        self.assertAlmostEqual(detection.point_camera_m[2], 0.985, places=2)

        narrow_face_depth = np.ones((100, 100), dtype=np.float32)
        narrow_face_depth[40:60, 46:55] = 0.955
        self.assertIsNone(
            detect_target_from_depth(
                narrow_face_depth,
                intrinsics,
                "[T1]",
                definition,
                settings,
                0.60,
                np.random.default_rng(11),
            )
        )

    def test_synthetic_cuboid_detection_on_inclined_plane(self):
        height, width = 120, 120
        intrinsics = CameraIntrinsics(600.0, 600.0, 59.5, 59.5)
        yy, xx = np.mgrid[0:height, 0:width]
        rays = np.dstack(
            (
                (xx - intrinsics.ppx) / intrinsics.fx,
                (yy - intrinsics.ppy) / intrinsics.fy,
                np.ones_like(xx, dtype=np.float64),
            )
        )
        angle = np.deg2rad(45.0)
        normal = np.asarray([0.0, np.sin(angle), -np.cos(angle)])
        base_center = np.asarray([0.0, 0.0, 0.55])
        plane_offset = -float(normal @ base_center)
        ray_dot_normal = rays @ normal
        base_depth = -plane_offset / ray_dot_normal

        # Put the cuboid on its largest 45 x 33 mm face, leaving 15 mm as
        # the height above the inclined work plane.
        object_height_m = 0.015
        top_depth = -(plane_offset - object_height_m) / ray_dot_normal
        top_points = rays * top_depth[..., None]
        top_center = base_center + object_height_m * normal
        plane_u = np.asarray([0.0, -np.cos(angle), -np.sin(angle)])
        plane_v = np.asarray([-1.0, 0.0, 0.0])
        relative = top_points - top_center
        object_mask = (
            (np.abs(relative @ plane_u) <= 0.0225)
            & (np.abs(relative @ plane_v) <= 0.0165)
        )
        depth = base_depth.astype(np.float32)
        depth[object_mask] = top_depth[object_mask].astype(np.float32)

        settings = DetectorSettings(
            roi_xyxy=(0, 0, width, height),
            plane_sample_stride=2,
            plane_ransac_iterations=80,
            plane_distance_threshold_m=0.003,
            min_plane_inlier_ratio=0.70,
            object_min_height_m=0.010,
            object_max_height_m=0.085,
            min_component_area_px=50,
            morphology_kernel_px=1,
            dimension_abs_tolerance_mm=8.0,
            dimension_relative_tolerance=0.35,
            min_rectangularity=0.40,
        )
        detection = detect_target_from_depth(
            depth,
            intrinsics,
            "[T1]",
            {
                "enabled": True,
                "dimensions_mm": [15.0, 45.0, 33.0],
                "visible_face": {
                    "dimensions_mm": [45.0, 33.0],
                    "absolute_tolerance_mm": 8.0,
                    "relative_tolerance": 0.30,
                    "confidence_weight": 0.35,
                },
            },
            settings,
            0.60,
            np.random.default_rng(7),
        )
        self.assertIsNotNone(detection)
        self.assertGreaterEqual(detection.confidence, 0.60)
        self.assertAlmostEqual(detection.observed_dimensions_mm[2], 45.0, delta=8.0)

    def test_dominant_visible_face_ignores_smaller_side_plane(self):
        broad_y, broad_x = np.mgrid[-0.0165:0.0165:15j, -0.0225:0.0225:21j]
        broad = np.column_stack(
            (broad_x.ravel(), broad_y.ravel(), np.full(broad_x.size, 0.50))
        )
        side_y, side_z = np.mgrid[-0.0165:0.0165:15j, 0.50:0.515:6j]
        side = np.column_stack(
            (np.full(side_y.size, 0.0225), side_y.ravel(), side_z.ravel())
        )
        measurement = measure_visible_face(
            np.vstack((broad, side)),
            np.random.default_rng(12),
            ransac_iterations=100,
            distance_threshold_m=0.001,
            min_inlier_ratio=0.50,
        )
        self.assertIsNotNone(measurement)
        dimensions_mm, center = measurement
        np.testing.assert_allclose(dimensions_mm, [33.0, 45.0], atol=1.0)
        np.testing.assert_allclose(center, [0.0, 0.0, 0.50], atol=0.002)

    def test_camera_distance_band_rejects_wrong_depth(self):
        depth = np.ones((100, 100), dtype=np.float32)
        depth[36:64, 45:55] = 0.967
        settings = DetectorSettings(
            roi_xyxy=(0, 0, 100, 100),
            plane_sample_stride=2,
            plane_ransac_iterations=40,
            plane_distance_threshold_m=0.002,
            min_plane_inlier_ratio=0.8,
            object_min_height_m=0.005,
            object_max_height_m=0.08,
            min_component_area_px=20,
            morphology_kernel_px=1,
            dimension_abs_tolerance_mm=8.0,
            dimension_relative_tolerance=0.35,
        )
        base = {
            "enabled": True,
            "dimensions_mm": [15.0, 45.0, 33.0],
            "camera_distance": {
                "expected_m": 0.967,
                "tolerance_m": 0.020,
                "confidence_weight": 0.15,
            },
        }
        self.assertIsNotNone(
            detect_target_from_depth(
                depth,
                CameraIntrinsics(600.0, 600.0, 49.5, 49.5),
                "[T1]",
                base,
                settings,
                0.6,
                np.random.default_rng(5),
            )
        )
        wrong_distance = dict(base)
        wrong_distance["camera_distance"] = {
            "expected_m": 0.550,
            "tolerance_m": 0.080,
            "confidence_weight": 0.15,
        }
        self.assertIsNone(
            detect_target_from_depth(
                depth,
                CameraIntrinsics(600.0, 600.0, 49.5, 49.5),
                "[T1]",
                wrong_distance,
                settings,
                0.6,
                np.random.default_rng(6),
            )
        )

    def test_black_t1_accepts_black_on_white_and_rejects_white(self):
        depth = np.ones((100, 100), dtype=np.float32)
        depth[36:64, 45:55] = 0.967
        settings = DetectorSettings(
            roi_xyxy=(0, 0, 100, 100),
            plane_sample_stride=2,
            plane_ransac_iterations=40,
            plane_distance_threshold_m=0.002,
            min_plane_inlier_ratio=0.8,
            object_min_height_m=0.005,
            object_max_height_m=0.08,
            min_component_area_px=20,
            morphology_kernel_px=1,
            dimension_abs_tolerance_mm=8.0,
            dimension_relative_tolerance=0.35,
            color_canny_low_threshold=40,
            color_canny_high_threshold=120,
            depth_edge_threshold_m=0.006,
            edge_search_radius_px=2,
            min_color_edge_ratio=0.05,
            min_depth_edge_ratio=0.05,
            edge_confidence_weight=0.20,
        )
        definition = {
            "enabled": True,
            "dimensions_mm": [15.0, 45.0, 33.0],
            "color": {
                "enabled": True,
                "hsv_lower": [0, 0, 0],
                "hsv_upper": [179, 255, 80],
                "min_ratio": 0.45,
                "confidence_weight": 0.35,
            },
        }
        black_object = np.full((100, 100, 3), 255, dtype=np.uint8)
        black_object[36:64, 45:55] = 0
        detection = detect_target_from_depth(
            depth,
            CameraIntrinsics(600.0, 600.0, 49.5, 49.5),
            "[T1]",
            definition,
            settings,
            0.6,
            np.random.default_rng(3),
            color_bgr=black_object,
        )
        self.assertIsNotNone(detection)
        self.assertGreaterEqual(detection.color_ratio, 0.95)
        self.assertGreater(detection.color_edge_ratio, 0.05)
        self.assertGreater(detection.depth_edge_ratio, 0.05)

        white_object = np.full((100, 100, 3), 255, dtype=np.uint8)
        self.assertIsNone(
            detect_target_from_depth(
                depth,
                CameraIntrinsics(600.0, 600.0, 49.5, 49.5),
                "[T1]",
                definition,
                settings,
                0.6,
                np.random.default_rng(4),
                color_bgr=white_object,
            )
        )

    def test_red_t2_accepts_red_and_rejects_white(self):
        depth = np.ones((100, 100), dtype=np.float32)
        depth[36:64, 45:55] = 0.967
        settings = DetectorSettings(
            roi_xyxy=(0, 0, 100, 100),
            plane_sample_stride=2,
            plane_ransac_iterations=40,
            plane_distance_threshold_m=0.002,
            min_plane_inlier_ratio=0.8,
            object_min_height_m=0.005,
            object_max_height_m=0.08,
            min_component_area_px=20,
            morphology_kernel_px=1,
            dimension_abs_tolerance_mm=8.0,
            dimension_relative_tolerance=0.35,
        )
        definition = {
            "enabled": True,
            "dimensions_mm": [15.0, 45.0, 33.0],
            "color": {
                "enabled": True,
                "hsv_ranges": [
                    {"lower": [0, 100, 70], "upper": [12, 255, 255]},
                    {"lower": [168, 100, 70], "upper": [179, 255, 255]},
                ],
                "min_ratio": 0.35,
                "confidence_weight": 0.40,
            },
        }
        red_object = np.zeros((100, 100, 3), dtype=np.uint8)
        red_object[36:64, 45:55] = [0, 0, 255]
        detection = detect_target_from_depth(
            depth,
            CameraIntrinsics(600.0, 600.0, 49.5, 49.5),
            "[T2]",
            definition,
            settings,
            0.6,
            np.random.default_rng(8),
            color_bgr=red_object,
        )
        self.assertIsNotNone(detection)
        self.assertGreaterEqual(detection.color_ratio, 0.95)

        white_object = np.zeros((100, 100, 3), dtype=np.uint8)
        white_object[36:64, 45:55] = 255
        self.assertIsNone(
            detect_target_from_depth(
                depth,
                CameraIntrinsics(600.0, 600.0, 49.5, 49.5),
                "[T2]",
                definition,
                settings,
                0.6,
                np.random.default_rng(9),
                color_bgr=white_object,
            )
        )

    def test_depth_edge_support_follows_component_boundary(self):
        depth = np.ones((20, 20), dtype=np.float32)
        component = np.zeros((20, 20), dtype=bool)
        component[6:14, 8:12] = True
        depth[component] = 0.96
        edges = depth_edge_mask(depth, 0.006)
        self.assertGreater(edge_support_ratio(component, edges, 1), 0.8)

    def test_transform(self):
        transform = np.eye(4)
        transform[:3, 3] = [0.1, -0.2, 0.3]
        np.testing.assert_allclose(
            camera_to_arm([1.0, 2.0, 3.0], transform), [1.1, 1.8, 3.3]
        )
        document = {
            "calibrated": True,
            "translation_unit": "m",
            "T_arm_camera": np.eye(4).tolist(),
        }
        with patch("geometry_recognition._load_yaml", return_value=document):
            np.testing.assert_allclose(
                load_arm_camera_transform(Path("unused.yaml")), np.eye(4)
            )

    def test_configured_vertical_camera_mycobot_transform(self):
        document = {
            "calibrated": True,
            "translation_unit": "m",
            "T_arm_camera": [
                [0.0, -1.0, 0.0, -0.30],
                [-1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, -1.0, 0.47],
                [0.0, 0.0, 0.0, 1.0],
            ],
        }
        with patch("geometry_recognition._load_yaml", return_value=document):
            transform = load_arm_camera_transform(Path("T_arm_camera.yaml"))
        np.testing.assert_allclose(
            camera_to_arm([0.0, 0.0, 0.0], transform),
            [-0.30, 0.0, 0.47],
            atol=1e-9,
        )
        np.testing.assert_allclose(
            camera_to_arm([0.10, 0.02, 0.40], transform),
            [-0.32, -0.10, 0.07],
            atol=1e-9,
        )


if __name__ == "__main__":
    unittest.main()

"""Depth-geometry recognition helpers for Image_Recognition.

The functions in this file do not depend on OpenRTM or pyrealsense2, which
makes the geometry and coordinate conversion independently testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

import cv2
import numpy as np
import yaml


VALID_TARGET_IDS = frozenset({"[T1]", "[T2]", "[T3]", "[T4]"})


@dataclass(frozen=True)
class CameraIntrinsics:
    fx: float
    fy: float
    ppx: float
    ppy: float


@dataclass(frozen=True)
class DetectorSettings:
    roi_xyxy: tuple[int, int, int, int]
    plane_sample_stride: int
    plane_ransac_iterations: int
    plane_distance_threshold_m: float
    min_plane_inlier_ratio: float
    object_min_height_m: float
    object_max_height_m: float
    min_component_area_px: int
    morphology_kernel_px: int
    dimension_abs_tolerance_mm: float
    dimension_relative_tolerance: float
    color_canny_low_threshold: int = 50
    color_canny_high_threshold: int = 150
    depth_edge_threshold_m: float = 0.008
    edge_search_radius_px: int = 2
    min_color_edge_ratio: float = 0.05
    min_depth_edge_ratio: float = 0.05
    edge_confidence_weight: float = 0.0
    max_component_area_px: int = 2_147_483_647
    min_rectangularity: float = 0.0
    stable_cluster_radius_m: float = 0.012


@dataclass(frozen=True)
class GeometryDetection:
    target_id: str
    confidence: float
    geometry_confidence: float
    color_ratio: Optional[float]
    edge_confidence: Optional[float]
    color_edge_ratio: Optional[float]
    depth_edge_ratio: Optional[float]
    visible_face_confidence: Optional[float]
    visible_face_shape_confidence: Optional[float]
    observed_visible_face_mm: Optional[tuple[float, float]]
    rectangularity: float
    camera_distance_m: float
    point_camera_m: tuple[float, float, float]
    observed_dimensions_mm: tuple[float, float, float]
    pixel_area: int
    bounding_box_xyxy: tuple[int, int, int, int]
    detection_mode: str = "depth"


@dataclass(frozen=True)
class DetectionSample:
    confidence: float
    point_output_m: tuple[float, float, float]
    captured_at: float


def normalize_target_id(value: Any) -> str:
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    target_id = str(value).strip().upper()
    # Select_Target currently sends IDs such as "t1", while some RTCs send
    # the bracketed form "[T1]".  Keep one canonical representation inside
    # this component and accept both wire representations.
    if target_id in {"T1", "T2", "T3", "T4"}:
        target_id = f"[{target_id}]"
    if target_id not in VALID_TARGET_IDS:
        allowed = ", ".join(sorted(VALID_TARGET_IDS))
        raise ValueError(f"Unknown target ID {target_id!r}; expected {allowed}")
    return target_id


def resolve_path(component_dir: Path, configured_path: str) -> Path:
    path = Path(configured_path).expanduser()
    if not path.is_absolute():
        path = component_dir / path
    return path.resolve()


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return value


def load_geometry_configuration(
    path: Path,
) -> tuple[DetectorSettings, Dict[str, Dict[str, Any]], str]:
    document = _load_yaml(path)
    detector = document.get("detector")
    targets = document.get("targets")
    if not isinstance(detector, dict) or not isinstance(targets, dict):
        raise ValueError(f"'detector' and 'targets' mappings are required: {path}")

    roi = detector.get("roi_xyxy", [0, 0, 0, 0])
    if not isinstance(roi, list) or len(roi) != 4:
        raise ValueError("detector.roi_xyxy must contain [x1, y1, x2, y2]")
    settings = DetectorSettings(
        roi_xyxy=tuple(int(value) for value in roi),
        plane_sample_stride=int(detector.get("plane_sample_stride", 4)),
        plane_ransac_iterations=int(detector.get("plane_ransac_iterations", 80)),
        plane_distance_threshold_m=float(
            detector.get("plane_distance_threshold_m", 0.004)
        ),
        min_plane_inlier_ratio=float(detector.get("min_plane_inlier_ratio", 0.35)),
        object_min_height_m=float(detector.get("object_min_height_m", 0.006)),
        object_max_height_m=float(detector.get("object_max_height_m", 0.100)),
        min_component_area_px=int(detector.get("min_component_area_px", 30)),
        morphology_kernel_px=int(detector.get("morphology_kernel_px", 3)),
        dimension_abs_tolerance_mm=float(
            detector.get("dimension_abs_tolerance_mm", 8.0)
        ),
        dimension_relative_tolerance=float(
            detector.get("dimension_relative_tolerance", 0.35)
        ),
        color_canny_low_threshold=int(
            detector.get("color_canny_low_threshold", 50)
        ),
        color_canny_high_threshold=int(
            detector.get("color_canny_high_threshold", 150)
        ),
        depth_edge_threshold_m=float(
            detector.get("depth_edge_threshold_m", 0.008)
        ),
        edge_search_radius_px=int(detector.get("edge_search_radius_px", 2)),
        min_color_edge_ratio=float(detector.get("min_color_edge_ratio", 0.05)),
        min_depth_edge_ratio=float(detector.get("min_depth_edge_ratio", 0.05)),
        edge_confidence_weight=float(
            detector.get("edge_confidence_weight", 0.0)
        ),
        max_component_area_px=int(
            detector.get("max_component_area_px", 2_147_483_647)
        ),
        min_rectangularity=float(detector.get("min_rectangularity", 0.0)),
        stable_cluster_radius_m=float(
            detector.get("stable_cluster_radius_m", 0.012)
        ),
    )
    _validate_settings(settings)

    result: Dict[str, Dict[str, Any]] = {}
    for raw_id, raw_definition in targets.items():
        target_id = normalize_target_id(raw_id)
        if not isinstance(raw_definition, dict):
            raise ValueError(f"Definition for {target_id} must be a mapping")
        definition = dict(raw_definition)
        enabled = definition.get("enabled", True) is True
        definition["enabled"] = enabled
        if enabled:
            dimensions = definition.get("dimensions_mm")
            if not isinstance(dimensions, list) or len(dimensions) != 3:
                raise ValueError(
                    f"Enabled target {target_id} needs three dimensions_mm values"
                )
            dimensions = [float(value) for value in dimensions]
            if any(value <= 0.0 for value in dimensions):
                raise ValueError(f"dimensions_mm for {target_id} must be positive")
            definition["dimensions_mm"] = dimensions
            visible_face_definition = definition.get("visible_face")
            if visible_face_definition is not None:
                if not isinstance(visible_face_definition, dict):
                    raise ValueError(
                        f"visible_face for {target_id} must be a mapping"
                    )
                visible_face_definition = dict(visible_face_definition)
                face_dimensions = visible_face_definition.get("dimensions_mm")
                if not isinstance(face_dimensions, list) or len(face_dimensions) != 2:
                    raise ValueError(
                        f"visible_face for {target_id} needs two dimensions_mm values"
                    )
                face_dimensions = [float(value) for value in face_dimensions]
                if any(value <= 0.0 for value in face_dimensions):
                    raise ValueError(
                        f"visible_face dimensions for {target_id} must be positive"
                    )
                absolute_tolerance_mm = float(
                    visible_face_definition.get("absolute_tolerance_mm", 8.0)
                )
                relative_tolerance = float(
                    visible_face_definition.get("relative_tolerance", 0.30)
                )
                confidence_weight = float(
                    visible_face_definition.get("confidence_weight", 0.35)
                )
                face_shape = str(
                    visible_face_definition.get("shape", "rectangle")
                ).strip().lower()
                measurement = str(
                    visible_face_definition.get("measurement", "plane")
                ).strip().lower()
                min_shape_confidence = float(
                    visible_face_definition.get("min_shape_confidence", 0.50)
                )
                shape_confidence_weight = float(
                    visible_face_definition.get("shape_confidence_weight", 0.20)
                )
                plane_ransac_iterations = int(
                    visible_face_definition.get("plane_ransac_iterations", 80)
                )
                plane_distance_threshold_m = float(
                    visible_face_definition.get(
                        "plane_distance_threshold_m", 0.004
                    )
                )
                min_plane_inlier_ratio = float(
                    visible_face_definition.get("min_plane_inlier_ratio", 0.30)
                )
                if absolute_tolerance_mm <= 0.0 or relative_tolerance <= 0.0:
                    raise ValueError(
                        f"visible_face tolerances for {target_id} must be positive"
                    )
                if not 0.0 <= confidence_weight <= 1.0:
                    raise ValueError(
                        f"visible_face.confidence_weight for {target_id} must be 0..1"
                    )
                if face_shape not in {"rectangle", "circle", "hexagon"}:
                    raise ValueError(
                        f"visible_face.shape for {target_id} must be rectangle, "
                        "circle or hexagon"
                    )
                if measurement not in {"plane", "silhouette"}:
                    raise ValueError(
                        f"visible_face.measurement for {target_id} must be plane "
                        "or silhouette"
                    )
                if not 0.0 <= min_shape_confidence <= 1.0:
                    raise ValueError(
                        f"visible_face.min_shape_confidence for {target_id} must be 0..1"
                    )
                if not 0.0 <= shape_confidence_weight <= 1.0:
                    raise ValueError(
                        f"visible_face.shape_confidence_weight for {target_id} must be 0..1"
                    )
                if plane_ransac_iterations <= 0 or plane_distance_threshold_m <= 0.0:
                    raise ValueError(
                        f"visible_face plane settings for {target_id} must be positive"
                    )
                if not 0.0 < min_plane_inlier_ratio <= 1.0:
                    raise ValueError(
                        f"visible_face.min_plane_inlier_ratio for {target_id} must be 0..1"
                    )
                visible_face_definition["dimensions_mm"] = face_dimensions
                visible_face_definition[
                    "absolute_tolerance_mm"
                ] = absolute_tolerance_mm
                visible_face_definition["relative_tolerance"] = relative_tolerance
                visible_face_definition["confidence_weight"] = confidence_weight
                visible_face_definition["shape"] = face_shape
                visible_face_definition["measurement"] = measurement
                visible_face_definition[
                    "min_shape_confidence"
                ] = min_shape_confidence
                visible_face_definition[
                    "shape_confidence_weight"
                ] = shape_confidence_weight
                visible_face_definition[
                    "plane_ransac_iterations"
                ] = plane_ransac_iterations
                visible_face_definition[
                    "plane_distance_threshold_m"
                ] = plane_distance_threshold_m
                visible_face_definition[
                    "min_plane_inlier_ratio"
                ] = min_plane_inlier_ratio
                definition["visible_face"] = visible_face_definition
            distance_definition = definition.get("camera_distance")
            if distance_definition is not None:
                if not isinstance(distance_definition, dict):
                    raise ValueError(
                        f"camera_distance for {target_id} must be a mapping"
                    )
                distance_definition = dict(distance_definition)
                expected_m = float(distance_definition.get("expected_m", 0.55))
                tolerance_m = float(distance_definition.get("tolerance_m", 0.08))
                confidence_weight = float(
                    distance_definition.get("confidence_weight", 0.15)
                )
                if expected_m <= 0.0 or tolerance_m <= 0.0:
                    raise ValueError(
                        f"camera_distance values for {target_id} must be positive"
                    )
                if not 0.0 <= confidence_weight <= 1.0:
                    raise ValueError(
                        f"camera_distance.confidence_weight for {target_id} must be 0..1"
                    )
                distance_definition["expected_m"] = expected_m
                distance_definition["tolerance_m"] = tolerance_m
                distance_definition["confidence_weight"] = confidence_weight
                definition["camera_distance"] = distance_definition
            color_definition = definition.get("color", {"enabled": False})
            if not isinstance(color_definition, dict):
                raise ValueError(f"color for {target_id} must be a mapping")
            color_definition = dict(color_definition)
            color_enabled = color_definition.get("enabled", False) is True
            color_definition["enabled"] = color_enabled
            if color_enabled:
                raw_ranges = color_definition.get("hsv_ranges")
                if raw_ranges is None:
                    raw_ranges = [
                        {
                            "lower": color_definition.get("hsv_lower"),
                            "upper": color_definition.get("hsv_upper"),
                        }
                    ]
                if not isinstance(raw_ranges, list) or not raw_ranges:
                    raise ValueError(
                        f"Enabled color for {target_id} needs at least one HSV range"
                    )
                limits = [179, 255, 255]
                normalized_ranges = []
                for range_index, raw_range in enumerate(raw_ranges):
                    if not isinstance(raw_range, dict):
                        raise ValueError(
                            f"HSV range {range_index} for {target_id} must be a mapping"
                        )
                    lower = raw_range.get("lower")
                    upper = raw_range.get("upper")
                    if (
                        not isinstance(lower, list)
                        or not isinstance(upper, list)
                        or len(lower) != 3
                        or len(upper) != 3
                    ):
                        raise ValueError(
                            f"HSV range {range_index} for {target_id} needs lower/upper"
                        )
                    lower = [int(value) for value in lower]
                    upper = [int(value) for value in upper]
                    if any(
                        low < 0 or high > limit or low > high
                        for low, high, limit in zip(lower, upper, limits)
                    ):
                        raise ValueError(
                            f"Invalid HSV range {range_index} for {target_id}"
                        )
                    normalized_ranges.append({"lower": lower, "upper": upper})
                min_ratio = float(color_definition.get("min_ratio", 0.45))
                confidence_weight = float(
                    color_definition.get("confidence_weight", 0.35)
                )
                if not 0.0 <= min_ratio <= 1.0:
                    raise ValueError(f"color.min_ratio for {target_id} must be 0..1")
                if not 0.0 <= confidence_weight <= 1.0:
                    raise ValueError(
                        f"color.confidence_weight for {target_id} must be 0..1"
                    )
                color_definition["hsv_ranges"] = normalized_ranges
                color_definition["min_ratio"] = min_ratio
                color_definition["confidence_weight"] = confidence_weight
            definition["color"] = color_definition
            fallback_definition = definition.get(
                "color_fixed_depth_fallback", {"enabled": False}
            )
            if not isinstance(fallback_definition, dict):
                raise ValueError(
                    f"color_fixed_depth_fallback for {target_id} must be a mapping"
                )
            fallback_definition = dict(fallback_definition)
            fallback_enabled = fallback_definition.get("enabled", False) is True
            fallback_definition["enabled"] = fallback_enabled
            if fallback_enabled:
                if not color_enabled:
                    raise ValueError(
                        f"color_fixed_depth_fallback for {target_id} requires color"
                    )
                if visible_face_definition is None:
                    raise ValueError(
                        f"color_fixed_depth_fallback for {target_id} requires visible_face"
                    )
                default_distance_m = (
                    float(distance_definition["expected_m"])
                    if distance_definition is not None
                    else 0.455
                )
                camera_distance_m = float(
                    fallback_definition.get("camera_distance_m", default_distance_m)
                )
                fallback_confidence_threshold = float(
                    fallback_definition.get("confidence_threshold", 0.60)
                )
                if camera_distance_m <= 0.0:
                    raise ValueError(
                        f"color_fixed_depth_fallback distance for {target_id} must be positive"
                    )
                if not 0.0 <= fallback_confidence_threshold <= 1.0:
                    raise ValueError(
                        f"color_fixed_depth_fallback confidence for {target_id} must be 0..1"
                    )
                fallback_definition["camera_distance_m"] = camera_distance_m
                fallback_definition[
                    "confidence_threshold"
                ] = fallback_confidence_threshold
            definition["color_fixed_depth_fallback"] = fallback_definition
        result[target_id] = definition

    missing = VALID_TARGET_IDS.difference(result)
    if missing:
        raise ValueError(f"Target definitions are missing: {', '.join(sorted(missing))}")
    if not any(definition["enabled"] for definition in result.values()):
        raise ValueError("At least one target must be enabled")
    output_frame = str(document.get("output_frame", "camera")).strip().lower()
    if output_frame not in {"camera", "arm"}:
        raise ValueError("output_frame must be 'camera' or 'arm'")
    return settings, result, output_frame


def _validate_settings(settings: DetectorSettings) -> None:
    if settings.plane_sample_stride <= 0:
        raise ValueError("plane_sample_stride must be positive")
    if settings.plane_ransac_iterations <= 0:
        raise ValueError("plane_ransac_iterations must be positive")
    if settings.plane_distance_threshold_m <= 0.0:
        raise ValueError("plane_distance_threshold_m must be positive")
    if not 0.0 < settings.min_plane_inlier_ratio <= 1.0:
        raise ValueError("min_plane_inlier_ratio must be in (0, 1]")
    if not 0.0 < settings.object_min_height_m < settings.object_max_height_m:
        raise ValueError("Object height range is invalid")
    if settings.min_component_area_px <= 0:
        raise ValueError("min_component_area_px must be positive")
    if settings.morphology_kernel_px <= 0:
        raise ValueError("morphology_kernel_px must be positive")
    if settings.dimension_abs_tolerance_mm <= 0.0:
        raise ValueError("dimension_abs_tolerance_mm must be positive")
    if settings.dimension_relative_tolerance <= 0.0:
        raise ValueError("dimension_relative_tolerance must be positive")
    if not (
        0 <= settings.color_canny_low_threshold
        < settings.color_canny_high_threshold
        <= 255
    ):
        raise ValueError("Color Canny thresholds must satisfy 0 <= low < high <= 255")
    if settings.depth_edge_threshold_m <= 0.0:
        raise ValueError("depth_edge_threshold_m must be positive")
    if settings.edge_search_radius_px < 0:
        raise ValueError("edge_search_radius_px cannot be negative")
    if not 0.0 <= settings.min_color_edge_ratio <= 1.0:
        raise ValueError("min_color_edge_ratio must be 0..1")
    if not 0.0 <= settings.min_depth_edge_ratio <= 1.0:
        raise ValueError("min_depth_edge_ratio must be 0..1")
    if not 0.0 <= settings.edge_confidence_weight <= 1.0:
        raise ValueError("edge_confidence_weight must be 0..1")
    if settings.max_component_area_px < settings.min_component_area_px:
        raise ValueError("max_component_area_px cannot be smaller than minimum")
    if not 0.0 <= settings.min_rectangularity <= 1.0:
        raise ValueError("min_rectangularity must be 0..1")
    if settings.stable_cluster_radius_m <= 0.0:
        raise ValueError("stable_cluster_radius_m must be positive")


def load_arm_camera_transform(path: Path) -> np.ndarray:
    document = _load_yaml(path)
    if document.get("calibrated") is not True:
        raise ValueError(
            f"Camera-to-arm transform is not calibrated: {path}. "
            "Set calibrated: true only after measuring T_arm_camera."
        )
    if document.get("translation_unit") != "m":
        raise ValueError("T_arm_camera translation_unit must be 'm'")
    transform = np.asarray(document.get("T_arm_camera"), dtype=np.float64)
    if transform.shape != (4, 4) or not np.all(np.isfinite(transform)):
        raise ValueError("T_arm_camera must be a finite 4 x 4 matrix")
    if not np.allclose(transform[3], [0.0, 0.0, 0.0, 1.0], atol=1e-8):
        raise ValueError("Last row of T_arm_camera must be [0, 0, 0, 1]")
    rotation = transform[:3, :3]
    if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-3):
        raise ValueError("Rotation part of T_arm_camera is not orthonormal")
    if not np.isclose(np.linalg.det(rotation), 1.0, atol=1e-3):
        raise ValueError("Rotation determinant of T_arm_camera must be +1")
    return transform


def camera_to_arm(point_camera_m: Iterable[float], transform: np.ndarray) -> np.ndarray:
    point = np.asarray(tuple(point_camera_m), dtype=np.float64)
    if point.shape != (3,) or not np.all(np.isfinite(point)):
        raise ValueError("point_camera_m must contain three finite values")
    return (transform @ np.append(point, 1.0))[:3]


def fit_plane_ransac(
    points: np.ndarray,
    iterations: int,
    distance_threshold_m: float,
    min_inlier_ratio: float,
    rng: np.random.Generator,
) -> Optional[tuple[np.ndarray, float]]:
    """Fit the dominant plane and orient its normal toward the camera origin."""

    if points.ndim != 2 or points.shape[1] != 3 or len(points) < 3:
        return None
    best_inliers: Optional[np.ndarray] = None
    best_count = 0
    for _ in range(iterations):
        sample = points[rng.choice(len(points), size=3, replace=False)]
        normal = np.cross(sample[1] - sample[0], sample[2] - sample[0])
        norm = float(np.linalg.norm(normal))
        if norm < 1e-9:
            continue
        normal /= norm
        offset = -float(np.dot(normal, sample[0]))
        inliers = np.abs(points @ normal + offset) <= distance_threshold_m
        count = int(np.count_nonzero(inliers))
        if count > best_count:
            best_count = count
            best_inliers = inliers

    if best_inliers is None or best_count / len(points) < min_inlier_ratio:
        return None
    inlier_points = points[best_inliers]
    center = np.mean(inlier_points, axis=0)
    _, _, axes = np.linalg.svd(inlier_points - center, full_matrices=False)
    normal = axes[-1]
    if np.dot(normal, -center) < 0.0:
        normal = -normal
    offset = -float(np.dot(normal, center))
    return normal, offset


def dimension_confidence(
    observed_dimensions_mm: Iterable[float],
    expected_dimensions_mm: Iterable[float],
    absolute_tolerance_mm: float,
    relative_tolerance: float,
) -> Optional[float]:
    observed = np.sort(np.asarray(tuple(observed_dimensions_mm), dtype=np.float64))
    expected = np.sort(np.asarray(tuple(expected_dimensions_mm), dtype=np.float64))
    if observed.shape != (3,) or expected.shape != (3,):
        raise ValueError("Observed and expected dimensions must each have three values")
    tolerance = np.maximum(absolute_tolerance_mm, expected * relative_tolerance)
    normalized_error = np.abs(observed - expected) / tolerance
    if np.any(normalized_error > 1.0):
        return None
    return float(np.exp(-0.5 * np.mean(normalized_error**2)))


def visible_face_confidence(
    observed_dimensions_mm: Iterable[float],
    expected_dimensions_mm: Iterable[float],
    absolute_tolerance_mm: float,
    relative_tolerance: float,
) -> Optional[float]:
    """Score the two orientation-free dimensions of a visible planar face."""

    observed = np.sort(np.asarray(tuple(observed_dimensions_mm), dtype=np.float64))
    expected = np.sort(np.asarray(tuple(expected_dimensions_mm), dtype=np.float64))
    if observed.shape != (2,) or expected.shape != (2,):
        raise ValueError("Visible face dimensions must each contain two values")
    tolerance = np.maximum(absolute_tolerance_mm, expected * relative_tolerance)
    normalized_error = np.abs(observed - expected) / tolerance
    if np.any(normalized_error > 1.0):
        return None
    return float(np.exp(-0.5 * np.mean(normalized_error**2)))


def visible_face_shape_confidence(
    component_mask: np.ndarray,
    expected_shape: str,
    rectangularity: float,
) -> float:
    """Score whether a top-view component is rectangular, circular or hexagonal.

    A square and a circle can have the same width, length/diameter, height and
    color. The fraction of the external contour that fills its enclosing circle
    is therefore used with rectangularity to distinguish those otherwise
    identical targets. Using the external contour ignores internal depth holes.
    Ellipse aspect ratio additionally rejects elongated or partially observed
    circles. A regular hexagon is identified by its characteristic enclosing-
    circle fill ratio, rectangularity and (when OpenCV provides the contour
    API) its approximated vertex count. A NumPy pixel estimate remains
    available for lightweight tests.
    """

    component = np.asarray(component_mask, dtype=bool)
    if component.ndim != 2:
        raise ValueError("component_mask must be a two-dimensional mask")
    pixel_y, pixel_x = np.nonzero(component)
    if len(pixel_x) < 3:
        return 0.0
    center_x = 0.5 * (float(np.min(pixel_x)) + float(np.max(pixel_x)))
    center_y = 0.5 * (float(np.min(pixel_y)) + float(np.max(pixel_y)))
    radius_px = float(
        np.sqrt(np.max((pixel_x - center_x) ** 2 + (pixel_y - center_y) ** 2))
        + 0.5
    )
    if not np.isfinite(radius_px) or radius_px <= 0.0:
        return 0.0
    enclosing_circle_area = np.pi * radius_px**2
    circle_fill_ratio = min(1.0, float(len(pixel_x)) / enclosing_circle_area)
    ellipse_aspect_ratio = 1.0
    polygon_vertex_count: Optional[int] = None

    contour_api_available = all(
        hasattr(cv2, name)
        for name in (
            "findContours",
            "contourArea",
            "minEnclosingCircle",
            "fitEllipse",
            "RETR_EXTERNAL",
            "CHAIN_APPROX_SIMPLE",
        )
    )
    if contour_api_available:
        try:
            contour_result = cv2.findContours(
                component.astype(np.uint8),
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE,
            )
            contours = contour_result[-2]
            if contours:
                contour = max(contours, key=cv2.contourArea)
                contour_area = float(cv2.contourArea(contour))
                _, contour_radius_px = cv2.minEnclosingCircle(contour)
                contour_circle_area = np.pi * float(contour_radius_px) ** 2
                if contour_area > 0.0 and contour_circle_area > 0.0:
                    circle_fill_ratio = min(
                        1.0, contour_area / contour_circle_area
                    )
                if len(contour) >= 5:
                    _, ellipse_axes, _ = cv2.fitEllipse(contour)
                    major_axis = max(float(ellipse_axes[0]), float(ellipse_axes[1]))
                    minor_axis = min(float(ellipse_axes[0]), float(ellipse_axes[1]))
                    if major_axis > 0.0:
                        ellipse_aspect_ratio = min(1.0, minor_axis / major_axis)
                if all(hasattr(cv2, name) for name in ("arcLength", "approxPolyDP")):
                    perimeter = float(cv2.arcLength(contour, True))
                    if perimeter > 0.0:
                        polygon_vertex_count = len(
                            cv2.approxPolyDP(contour, 0.04 * perimeter, True)
                        )
        except Exception:
            # The pixel estimate above is intentionally retained when a small
            # or damaged contour cannot be fitted reliably.
            pass

    normalized_shape = str(expected_shape).strip().lower()
    if normalized_shape == "circle":
        # A filled disk is normally above 0.90; a filled square is near 0.64.
        fill_score = float(
            np.clip((circle_fill_ratio - 0.68) / 0.20, 0.0, 1.0)
        )
        aspect_score = float(
            np.clip((ellipse_aspect_ratio - 0.65) / 0.25, 0.0, 1.0)
        )
        return float(np.sqrt(fill_score * aspect_score))
    if normalized_shape == "rectangle":
        circle_rejection = float(
            np.clip((0.82 - circle_fill_ratio) / 0.18, 0.0, 1.0)
        )
        return float(
            np.sqrt(np.clip(rectangularity, 0.0, 1.0) * circle_rejection)
        )
    if normalized_shape == "hexagon":
        ideal_circle_fill = 3.0 * np.sqrt(3.0) / (2.0 * np.pi)
        fill_score = float(
            np.exp(-0.5 * ((circle_fill_ratio - ideal_circle_fill) / 0.08) ** 2)
        )
        rectangularity_score = float(
            np.exp(-0.5 * ((float(rectangularity) - 0.75) / 0.12) ** 2)
        )
        confidence = float(np.sqrt(fill_score * rectangularity_score))
        if polygon_vertex_count is not None:
            vertex_score = float(
                np.exp(-0.5 * ((float(polygon_vertex_count) - 6.0) / 1.5) ** 2)
            )
            confidence = float(np.sqrt(confidence * vertex_score))
        return confidence
    raise ValueError(
        "expected_shape must be 'rectangle', 'circle' or 'hexagon'"
    )


def measure_visible_face(
    points_camera_m: np.ndarray,
    rng: np.random.Generator,
    ransac_iterations: int = 80,
    distance_threshold_m: float = 0.004,
    min_inlier_ratio: float = 0.30,
) -> Optional[tuple[tuple[float, float], np.ndarray]]:
    """Extract the dominant visible plane and measure its 3D rectangle."""

    points = np.asarray(points_camera_m, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3 or len(points) < 6:
        return None
    plane = fit_plane_ransac(
        points,
        ransac_iterations,
        distance_threshold_m,
        min_inlier_ratio,
        rng,
    )
    if plane is None:
        return None
    normal, offset = plane
    inliers = np.abs(points @ normal + offset) <= distance_threshold_m
    surface_points = points[inliers]
    if len(surface_points) < 6:
        return None
    plane_origin = -offset * normal
    plane_u, plane_v = _plane_axes(normal)
    relative = surface_points - plane_origin
    surface_coordinates = np.column_stack(
        (relative @ plane_u, relative @ plane_v)
    ).astype(np.float32)
    rectangle = cv2.minAreaRect(surface_coordinates)
    face_a, face_b = (float(value) for value in rectangle[1])
    if face_a <= 0.0 or face_b <= 0.0:
        return None
    center_u, center_v = rectangle[0]
    face_center = (
        plane_origin
        + float(center_u) * plane_u
        + float(center_v) * plane_v
    )
    if face_center.shape != (3,) or not np.all(np.isfinite(face_center)):
        return None
    dimensions_mm = tuple(
        float(value)
        for value in np.sort(np.asarray([face_a, face_b]) * 1000.0)
    )
    return dimensions_mm, face_center


def depth_edge_mask(depth_m: np.ndarray, threshold_m: float) -> np.ndarray:
    """Return pixels adjacent to a valid depth discontinuity."""

    valid = np.isfinite(depth_m) & (depth_m > 0.0)
    edges = np.zeros(depth_m.shape, dtype=bool)
    horizontal = (
        valid[:, 1:]
        & valid[:, :-1]
        & (np.abs(depth_m[:, 1:] - depth_m[:, :-1]) >= threshold_m)
    )
    vertical = (
        valid[1:, :]
        & valid[:-1, :]
        & (np.abs(depth_m[1:, :] - depth_m[:-1, :]) >= threshold_m)
    )
    edges[:, 1:] |= horizontal
    edges[:, :-1] |= horizontal
    edges[1:, :] |= vertical
    edges[:-1, :] |= vertical
    return edges


def _dilate_boolean(mask: np.ndarray, radius_px: int) -> np.ndarray:
    if radius_px <= 0:
        return mask.copy()
    height, width = mask.shape
    padded = np.pad(mask, radius_px, mode="constant", constant_values=False)
    dilated = np.zeros_like(mask, dtype=bool)
    diameter = 2 * radius_px + 1
    for offset_y in range(diameter):
        for offset_x in range(diameter):
            dilated |= padded[
                offset_y : offset_y + height,
                offset_x : offset_x + width,
            ]
    return dilated


def edge_support_ratio(
    component: np.ndarray, edge_mask: np.ndarray, search_radius_px: int
) -> float:
    """Measure how much of a component boundary has a nearby image edge."""

    component = np.asarray(component, dtype=bool)
    if component.shape != edge_mask.shape or not np.any(component):
        return 0.0
    height, width = component.shape
    padded = np.pad(component, 1, mode="constant", constant_values=False)
    interior = np.ones_like(component, dtype=bool)
    for offset_y in range(3):
        for offset_x in range(3):
            interior &= padded[
                offset_y : offset_y + height,
                offset_x : offset_x + width,
            ]
    boundary = component & ~interior
    boundary_count = int(np.count_nonzero(boundary))
    if boundary_count == 0:
        return 0.0
    nearby_edges = _dilate_boolean(
        np.asarray(edge_mask, dtype=bool), search_radius_px
    )
    return float(np.count_nonzero(boundary & nearby_edges)) / float(boundary_count)


def _target_color_mask(
    color_bgr: np.ndarray, color_definition: Mapping[str, Any]
) -> np.ndarray:
    """Build one HSV target mask from either normalized or legacy ranges."""

    hsv = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2HSV)
    hsv_ranges = color_definition.get("hsv_ranges")
    if hsv_ranges is None:
        hsv_ranges = [
            {
                "lower": color_definition["hsv_lower"],
                "upper": color_definition["hsv_upper"],
            }
        ]
    color_mask = np.zeros(color_bgr.shape[:2], dtype=bool)
    for hsv_range in hsv_ranges:
        color_mask |= cv2.inRange(
            hsv,
            np.asarray(hsv_range["lower"], dtype=np.uint8),
            np.asarray(hsv_range["upper"], dtype=np.uint8),
        ) > 0
    return color_mask


def detect_target_from_color_at_fixed_depth(
    color_bgr: np.ndarray,
    intrinsics: CameraIntrinsics,
    target_id: str,
    target_definition: Mapping[str, Any],
    settings: DetectorSettings,
    confidence_threshold: float,
) -> Optional[GeometryDetection]:
    """Detect by color/known size when the target has no usable depth pixels."""

    fallback = target_definition.get("color_fixed_depth_fallback", {})
    color_definition = target_definition.get("color", {})
    visible_face_definition = target_definition.get("visible_face")
    if (
        fallback.get("enabled") is not True
        or color_definition.get("enabled") is not True
        or visible_face_definition is None
        or color_bgr.ndim != 3
        or color_bgr.shape[2] != 3
    ):
        return None

    height, width = color_bgr.shape[:2]
    x1, y1, x2, y2 = _clamp_roi(settings.roi_xyxy, width, height)
    color_mask = _target_color_mask(color_bgr, color_definition)
    roi_mask = np.zeros((height, width), dtype=bool)
    roi_mask[y1:y2, x1:x2] = True
    color_mask &= roi_mask
    kernel = np.ones(
        (settings.morphology_kernel_px, settings.morphology_kernel_px),
        dtype=np.uint8,
    )
    component_mask = cv2.morphologyEx(
        color_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel
    )
    component_mask = cv2.morphologyEx(
        component_mask, cv2.MORPH_CLOSE, kernel
    )
    component_count, labels, statistics, _ = cv2.connectedComponentsWithStats(
        component_mask, connectivity=8
    )

    gray = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0.0)
    color_edges = cv2.Canny(
        gray,
        settings.color_canny_low_threshold,
        settings.color_canny_high_threshold,
    ) > 0
    fixed_depth_m = float(fallback["camera_distance_m"])
    expected_face_mm = visible_face_definition["dimensions_mm"]
    required_confidence = max(
        float(confidence_threshold), float(fallback["confidence_threshold"])
    )
    best: Optional[GeometryDetection] = None

    for label in range(1, component_count):
        pixel_area = int(statistics[label, cv2.CC_STAT_AREA])
        if (
            pixel_area < settings.min_component_area_px
            or pixel_area > settings.max_component_area_px
        ):
            continue
        component = labels == label
        pixel_y, pixel_x = np.nonzero(component)
        pixel_rectangle = cv2.minAreaRect(
            np.column_stack((pixel_x, pixel_y)).astype(np.float32)
        )
        pixel_rectangle_area = float(
            pixel_rectangle[1][0] * pixel_rectangle[1][1]
        )
        if pixel_rectangle_area <= 0.0:
            continue
        rectangularity = min(1.0, pixel_area / pixel_rectangle_area)
        if rectangularity < settings.min_rectangularity:
            continue
        shape_confidence: Optional[float] = None
        expected_face_shape = visible_face_definition.get("shape")
        if expected_face_shape is not None:
            shape_confidence = visible_face_shape_confidence(
                component, str(expected_face_shape), rectangularity
            )
            if shape_confidence < float(
                visible_face_definition.get("min_shape_confidence", 0.50)
            ):
                continue

        plane_points = np.column_stack(
            (
                (pixel_x - intrinsics.ppx) * fixed_depth_m / intrinsics.fx,
                (pixel_y - intrinsics.ppy) * fixed_depth_m / intrinsics.fy,
            )
        ).astype(np.float32)
        rectangle_m = cv2.minAreaRect(plane_points)
        face_a_m, face_b_m = (float(value) for value in rectangle_m[1])
        if face_a_m <= 0.0 or face_b_m <= 0.0:
            continue
        observed_face_mm = tuple(
            float(value)
            for value in np.sort(
                np.asarray([face_a_m, face_b_m], dtype=np.float64) * 1000.0
            )
        )
        face_confidence = visible_face_confidence(
            observed_face_mm,
            expected_face_mm,
            float(visible_face_definition["absolute_tolerance_mm"]),
            float(visible_face_definition["relative_tolerance"]),
        )
        if face_confidence is None:
            continue

        remaining_dimensions = [
            float(value) for value in target_definition["dimensions_mm"]
        ]
        for face_dimension in expected_face_mm:
            nearest_index = int(
                np.argmin(
                    np.abs(
                        np.asarray(remaining_dimensions, dtype=np.float64)
                        - float(face_dimension)
                    )
                )
            )
            remaining_dimensions.pop(nearest_index)
        known_thickness_mm = (
            remaining_dimensions[0]
            if remaining_dimensions
            else min(target_definition["dimensions_mm"])
        )
        observed_dimensions_mm = tuple(
            float(value)
            for value in np.sort(
                np.asarray(
                    [observed_face_mm[0], observed_face_mm[1], known_thickness_mm]
                )
            )
        )
        geometry_confidence = dimension_confidence(
            observed_dimensions_mm,
            target_definition["dimensions_mm"],
            settings.dimension_abs_tolerance_mm,
            settings.dimension_relative_tolerance,
        )
        if geometry_confidence is None:
            continue

        color_edge_ratio = edge_support_ratio(
            component, color_edges, settings.edge_search_radius_px
        )
        if color_edge_ratio < settings.min_color_edge_ratio:
            continue
        edge_reference = max(settings.min_color_edge_ratio, 0.05)
        edge_score = min(1.0, color_edge_ratio / edge_reference)
        surface_shape_confidence = (
            shape_confidence if shape_confidence is not None else rectangularity
        )
        confidence = float(
            0.45 * geometry_confidence
            + 0.35 * face_confidence
            + 0.15 * surface_shape_confidence
            + 0.05 * edge_score
        )
        if confidence < required_confidence:
            continue

        center_x_m, center_y_m = (float(value) for value in rectangle_m[0])
        candidate = GeometryDetection(
            target_id=target_id,
            confidence=confidence,
            geometry_confidence=geometry_confidence,
            color_ratio=rectangularity,
            edge_confidence=color_edge_ratio,
            color_edge_ratio=color_edge_ratio,
            depth_edge_ratio=None,
            visible_face_confidence=face_confidence,
            visible_face_shape_confidence=shape_confidence,
            observed_visible_face_mm=observed_face_mm,
            rectangularity=rectangularity,
            camera_distance_m=fixed_depth_m,
            point_camera_m=(center_x_m, center_y_m, fixed_depth_m),
            observed_dimensions_mm=observed_dimensions_mm,
            pixel_area=pixel_area,
            bounding_box_xyxy=(
                int(statistics[label, cv2.CC_STAT_LEFT]),
                int(statistics[label, cv2.CC_STAT_TOP]),
                int(
                    statistics[label, cv2.CC_STAT_LEFT]
                    + statistics[label, cv2.CC_STAT_WIDTH]
                    - 1
                ),
                int(
                    statistics[label, cv2.CC_STAT_TOP]
                    + statistics[label, cv2.CC_STAT_HEIGHT]
                    - 1
                ),
            ),
            detection_mode="color_fixed_depth",
        )
        if best is None or candidate.confidence > best.confidence:
            best = candidate
    return best


def detect_target_from_depth(
    depth_m: np.ndarray,
    intrinsics: CameraIntrinsics,
    target_id: str,
    target_definition: Mapping[str, Any],
    settings: DetectorSettings,
    confidence_threshold: float,
    rng: np.random.Generator,
    color_bgr: Optional[np.ndarray] = None,
) -> Optional[GeometryDetection]:
    """Detect one known-size object using depth geometry and optional color."""

    height, width = depth_m.shape
    x1, y1, x2, y2 = _clamp_roi(settings.roi_xyxy, width, height)
    yy, xx = np.mgrid[0:height, 0:width]
    valid = np.isfinite(depth_m) & (depth_m > 0.0)
    valid[:y1, :] = False
    valid[y2:, :] = False
    valid[:, :x1] = False
    valid[:, x2:] = False
    if np.count_nonzero(valid) < 100:
        return None

    camera_x = (xx - intrinsics.ppx) * depth_m / intrinsics.fx
    camera_y = (yy - intrinsics.ppy) * depth_m / intrinsics.fy

    sampled = valid.copy()
    stride = settings.plane_sample_stride
    sampled &= (xx % stride == 0) & (yy % stride == 0)
    plane_points = np.column_stack(
        (camera_x[sampled], camera_y[sampled], depth_m[sampled])
    )
    if len(plane_points) > 12000:
        plane_points = plane_points[
            rng.choice(len(plane_points), size=12000, replace=False)
        ]
    plane = fit_plane_ransac(
        plane_points,
        settings.plane_ransac_iterations,
        settings.plane_distance_threshold_m,
        settings.min_plane_inlier_ratio,
        rng,
    )
    if plane is None:
        return None
    normal, offset = plane

    signed_height = (
        normal[0] * camera_x
        + normal[1] * camera_y
        + normal[2] * depth_m
        + offset
    )
    object_mask = (
        valid
        & (signed_height >= settings.object_min_height_m)
        & (signed_height <= settings.object_max_height_m)
    ).astype(np.uint8)
    kernel_size = settings.morphology_kernel_px
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_OPEN, kernel)
    object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_CLOSE, kernel)

    component_count, labels, statistics, _ = cv2.connectedComponentsWithStats(
        object_mask, connectivity=8
    )
    plane_origin = -offset * normal
    plane_u, plane_v = _plane_axes(normal)
    expected = target_definition["dimensions_mm"]
    color_definition = target_definition.get("color", {})
    color_enabled = color_definition.get("enabled", False) is True
    edge_enabled = settings.edge_confidence_weight > 0.0
    color_image_valid = (
        color_bgr is not None
        and color_bgr.ndim == 3
        and color_bgr.shape[:2] == depth_m.shape
        and color_bgr.shape[2] == 3
    )
    if (color_enabled or edge_enabled) and not color_image_valid:
        return None
    color_mask: Optional[np.ndarray] = None
    if color_enabled:
        color_mask = _target_color_mask(color_bgr, color_definition)
    color_edges: Optional[np.ndarray] = None
    depth_edges: Optional[np.ndarray] = None
    if edge_enabled:
        gray = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2GRAY)
        # Suppress sensor and resampling speckles before Canny.  Edges are
        # used only for scoring and are never drawn into the preview image.
        gray = cv2.GaussianBlur(gray, (5, 5), 0.0)
        color_edges = cv2.Canny(
            gray,
            settings.color_canny_low_threshold,
            settings.color_canny_high_threshold,
        ) > 0
        depth_edges = depth_edge_mask(depth_m, settings.depth_edge_threshold_m)
    best: Optional[GeometryDetection] = None

    for label in range(1, component_count):
        pixel_area = int(statistics[label, cv2.CC_STAT_AREA])
        if (
            pixel_area < settings.min_component_area_px
            or pixel_area > settings.max_component_area_px
        ):
            continue
        component = labels == label
        pixel_y, pixel_x = np.nonzero(component)
        image_rectangle = cv2.minAreaRect(
            np.column_stack((pixel_x, pixel_y)).astype(np.float32)
        )
        image_rectangle_area = float(
            image_rectangle[1][0] * image_rectangle[1][1]
        )
        if image_rectangle_area <= 0.0:
            continue
        rectangularity = min(1.0, float(pixel_area) / image_rectangle_area)
        if rectangularity < settings.min_rectangularity:
            continue
        shape_confidence: Optional[float] = None
        visible_face_definition = target_definition.get("visible_face")
        if (
            visible_face_definition is not None
            and visible_face_definition.get("shape") is not None
        ):
            shape_confidence = visible_face_shape_confidence(
                component,
                str(visible_face_definition["shape"]),
                rectangularity,
            )
            if shape_confidence < float(
                visible_face_definition.get("min_shape_confidence", 0.50)
            ):
                continue
        points = np.column_stack(
            (camera_x[component], camera_y[component], depth_m[component])
        )
        if len(points) < 3:
            continue
        relative = points - plane_origin
        plane_coordinates = np.column_stack(
            (relative @ plane_u, relative @ plane_v)
        ).astype(np.float32)
        rectangle = cv2.minAreaRect(plane_coordinates)
        footprint_a, footprint_b = (float(value) for value in rectangle[1])
        object_height = float(np.percentile(signed_height[component], 95.0))
        if footprint_a <= 0.0 or footprint_b <= 0.0 or object_height <= 0.0:
            continue
        observed_mm = tuple(
            float(value)
            for value in np.sort(
                np.asarray([footprint_a, footprint_b, object_height]) * 1000.0
            )
        )
        geometry_confidence = dimension_confidence(
            observed_mm,
            expected,
            settings.dimension_abs_tolerance_mm,
            settings.dimension_relative_tolerance,
        )
        if geometry_confidence is None:
            continue
        visible_face_score: Optional[float] = None
        observed_visible_face_mm: Optional[tuple[float, float]] = None
        visible_face_center: Optional[np.ndarray] = None
        confidence = geometry_confidence
        if visible_face_definition is not None:
            measurement = str(
                visible_face_definition.get("measurement", "plane")
            ).strip().lower()
            if measurement == "silhouette":
                observed_visible_face_mm = tuple(
                    float(value)
                    for value in np.sort(
                        np.asarray([footprint_a, footprint_b]) * 1000.0
                    )
                )
            else:
                face_measurement = measure_visible_face(
                    points,
                    rng,
                    int(visible_face_definition.get("plane_ransac_iterations", 80)),
                    float(
                        visible_face_definition.get(
                            "plane_distance_threshold_m", 0.004
                        )
                    ),
                    float(
                        visible_face_definition.get("min_plane_inlier_ratio", 0.30)
                    ),
                )
                if face_measurement is None:
                    continue
                observed_visible_face_mm, visible_face_center = face_measurement
            visible_face_score = visible_face_confidence(
                observed_visible_face_mm,
                visible_face_definition["dimensions_mm"],
                float(visible_face_definition["absolute_tolerance_mm"]),
                float(visible_face_definition["relative_tolerance"]),
            )
            if visible_face_score is None:
                continue
            face_weight = float(visible_face_definition["confidence_weight"])
            confidence = (
                (1.0 - face_weight) * confidence
                + face_weight * visible_face_score
            )
            if shape_confidence is not None:
                shape_weight = float(
                    visible_face_definition.get("shape_confidence_weight", 0.20)
                )
                confidence = (
                    (1.0 - shape_weight) * confidence
                    + shape_weight * shape_confidence
                )
        color_ratio: Optional[float] = None
        if color_enabled:
            color_ratio = float(np.count_nonzero(color_mask & component)) / float(
                pixel_area
            )
            if color_ratio < float(color_definition["min_ratio"]):
                continue
            color_weight = float(color_definition["confidence_weight"])
            confidence = (
                (1.0 - color_weight) * confidence
                + color_weight * color_ratio
            )
        edge_confidence: Optional[float] = None
        color_edge_ratio: Optional[float] = None
        depth_edge_ratio: Optional[float] = None
        if edge_enabled:
            color_edge_ratio = edge_support_ratio(
                component, color_edges, settings.edge_search_radius_px
            )
            depth_edge_ratio = edge_support_ratio(
                component, depth_edges, settings.edge_search_radius_px
            )
            if (
                color_edge_ratio < settings.min_color_edge_ratio
                or depth_edge_ratio < settings.min_depth_edge_ratio
            ):
                continue
            edge_confidence = 0.5 * (color_edge_ratio + depth_edge_ratio)
            confidence = (
                (1.0 - settings.edge_confidence_weight) * confidence
                + settings.edge_confidence_weight * edge_confidence
            )
        center_u, center_v = rectangle[0]
        top_center = (
            plane_origin
            + float(center_u) * plane_u
            + float(center_v) * plane_v
            + object_height * normal
        )
        detection_point = (
            visible_face_center
            if visible_face_center is not None
            else top_center
        )
        if (
            detection_point.shape != (3,)
            or not np.all(np.isfinite(detection_point))
            or detection_point[2] <= 0.0
        ):
            continue
        camera_distance_m = float(detection_point[2])
        distance_definition = target_definition.get("camera_distance")
        if distance_definition is not None:
            distance_error = abs(
                camera_distance_m - float(distance_definition["expected_m"])
            )
            distance_tolerance = float(distance_definition["tolerance_m"])
            if distance_error > distance_tolerance:
                continue
            distance_confidence = float(
                np.exp(-0.5 * (distance_error / distance_tolerance) ** 2)
            )
            distance_weight = float(distance_definition["confidence_weight"])
            confidence = (
                (1.0 - distance_weight) * confidence
                + distance_weight * distance_confidence
            )
        if confidence < confidence_threshold:
            continue
        candidate = GeometryDetection(
            target_id=target_id,
            confidence=confidence,
            geometry_confidence=geometry_confidence,
            color_ratio=color_ratio,
            edge_confidence=edge_confidence,
            color_edge_ratio=color_edge_ratio,
            depth_edge_ratio=depth_edge_ratio,
            visible_face_confidence=visible_face_score,
            visible_face_shape_confidence=shape_confidence,
            observed_visible_face_mm=observed_visible_face_mm,
            rectangularity=rectangularity,
            camera_distance_m=camera_distance_m,
            point_camera_m=tuple(float(value) for value in detection_point),
            observed_dimensions_mm=observed_mm,
            pixel_area=pixel_area,
            bounding_box_xyxy=(
                int(statistics[label, cv2.CC_STAT_LEFT]),
                int(statistics[label, cv2.CC_STAT_TOP]),
                int(
                    statistics[label, cv2.CC_STAT_LEFT]
                    + statistics[label, cv2.CC_STAT_WIDTH]
                    - 1
                ),
                int(
                    statistics[label, cv2.CC_STAT_TOP]
                    + statistics[label, cv2.CC_STAT_HEIGHT]
                    - 1
                ),
            ),
        )
        if best is None or candidate.confidence > best.confidence:
            best = candidate
    return best


def select_best_sample(samples: Iterable[DetectionSample]) -> DetectionSample:
    values = list(samples)
    if not values:
        raise ValueError("Cannot select a sample from an empty collection")
    return max(values, key=lambda sample: sample.confidence)


def select_stable_best_sample(
    samples: Iterable[DetectionSample], radius_m: float, minimum_count: int
) -> Optional[DetectionSample]:
    """Choose the highest-confidence sample in the largest stable 3D cluster."""

    values = list(samples)
    if radius_m <= 0.0 or minimum_count <= 0:
        raise ValueError("Stable-cluster parameters must be positive")
    best_members: list[DetectionSample] = []
    best_score = (-1, -1.0)
    for center in values:
        center_point = np.asarray(center.point_output_m, dtype=np.float64)
        members = [
            sample
            for sample in values
            if np.linalg.norm(
                np.asarray(sample.point_output_m, dtype=np.float64) - center_point
            )
            <= radius_m
        ]
        score = (len(members), sum(sample.confidence for sample in members))
        if score > best_score:
            best_score = score
            best_members = members
    if len(best_members) < minimum_count:
        return None
    return max(best_members, key=lambda sample: sample.confidence)


def _clamp_roi(
    roi_xyxy: tuple[int, int, int, int], width: int, height: int
) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = roi_xyxy
    if x2 <= x1 or y2 <= y1:
        return 0, 0, width, height
    x1 = min(max(x1, 0), width - 1)
    y1 = min(max(y1, 0), height - 1)
    x2 = min(max(x2, x1 + 1), width)
    y2 = min(max(y2, y1 + 1), height)
    return x1, y1, x2, y2


def _plane_axes(normal: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    seed = np.asarray([1.0, 0.0, 0.0])
    if abs(float(np.dot(seed, normal))) > 0.9:
        seed = np.asarray([0.0, 1.0, 0.0])
    plane_u = np.cross(normal, seed)
    plane_u /= np.linalg.norm(plane_u)
    plane_v = np.cross(normal, plane_u)
    plane_v /= np.linalg.norm(plane_v)
    return plane_u, plane_v

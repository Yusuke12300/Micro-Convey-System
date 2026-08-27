from __future__ import annotations

import sys
import time
import unittest
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType, SimpleNamespace


class TimedString:
    pass


class TimedPoint3D:
    pass


class FakePort:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.values = deque()
        self.write_count = 0
        self.write_result = True

    def isNew(self):
        return bool(self.values)

    def read(self):
        return self.values.popleft()

    def write(self):
        self.write_count += 1
        return self.write_result


class FakeComponentBase:
    def __init__(self, manager):
        self.manager = manager

    def addInPort(self, name, port):
        pass

    def addOutPort(self, name, port):
        pass

    def bindParameter(self, name, holder, default):
        pass


rtc = ModuleType("RTC")
rtc.TimedString = TimedString
rtc.TimedPoint3D = TimedPoint3D
rtc.RTC_OK = 0
rtc.RTC_ERROR = 1
sys.modules["RTC"] = rtc

openrtm = ModuleType("OpenRTM_aist")
openrtm.DataFlowComponentBase = FakeComponentBase
openrtm.InPort = FakePort
openrtm.OutPort = FakePort
openrtm.Delete = object()
openrtm.Properties = lambda **kwargs: kwargs
openrtm.setTimestamp = lambda value: None


def instantiate_data_type(data_type):
    if data_type is TimedString:
        return SimpleNamespace(data="")
    if data_type is TimedPoint3D:
        return SimpleNamespace(data=SimpleNamespace(x=0.0, y=0.0, z=0.0))
    raise TypeError(data_type)


openrtm.instantiateDataType = instantiate_data_type
sys.modules["OpenRTM_aist"] = openrtm


@dataclass(frozen=True)
class DetectionSample:
    confidence: float
    point_output_m: tuple[float, float, float]
    captured_at: float


geometry = ModuleType("geometry_recognition")
geometry.CameraIntrinsics = object
geometry.DetectionSample = DetectionSample
geometry.camera_to_arm = lambda point, transform: point
geometry.detect_target_from_color_at_fixed_depth = lambda **kwargs: None
geometry.detect_target_from_depth = lambda **kwargs: None
geometry.load_arm_camera_transform = lambda path: None
geometry.load_geometry_configuration = lambda path: (None, {}, "camera")
def normalize_target_id(value):
    target_id = str(value).strip().upper()
    if target_id in {"T1", "T2", "T3", "T4"}:
        target_id = "[{}]".format(target_id)
    return target_id


geometry.normalize_target_id = normalize_target_id
geometry.resolve_path = lambda component_dir, path: component_dir / path
geometry.select_best_sample = lambda samples: max(
    samples, key=lambda sample: sample.confidence
)
geometry.select_stable_best_sample = lambda samples, radius_m, minimum_count: (
    max(samples, key=lambda sample: sample.confidence)
    if len(samples) >= minimum_count
    else None
)
sys.modules["geometry_recognition"] = geometry

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from Image_Recognition import Image_Recognition, REQUEST_TIMEOUT_SEC  # noqa: E402

# Keep Image_Recognition bound to the lightweight fake helpers above, but do
# not leak the fake module into geometry_recognition's independent test file.
del sys.modules["geometry_recognition"]


class ComponentLogicTests(unittest.TestCase):
    def setUp(self):
        self.component = Image_Recognition(object())

    def test_builder_ports_match_startup_generation_interface(self):
        self.assertEqual(self.component._Target_In1In.name, "Target_In1")
        self.assertEqual(
            self.component._Target_Coordinate_OutOut.name, "target_point"
        )
        self.assertEqual(self.component.onInitialize(), rtc.RTC_OK)

    def test_select_target_and_bracketed_ids_are_separate_requests(self):
        self.component._targets = {
            "[T1]": {"enabled": True, "dimensions_mm": [15, 45, 33]}
        }
        self.component._Target_In1In.values.extend(
            [SimpleNamespace(data="t1"), SimpleNamespace(data="[T1]")]
        )
        self.component._receive_target_requests()
        self.assertEqual(list(self.component._pending_target_ids), ["[T1]", "[T1]"])

    def test_preview_shortcut_queues_only_one_enabled_target_while_idle(self):
        self.component._targets = {
            "[T1]": {"enabled": True},
            "[T2]": {"enabled": True},
            "[T3]": {"enabled": False},
        }

        self.assertTrue(self.component._queue_preview_target("[T1]"))
        self.assertEqual(list(self.component._pending_target_ids), ["[T1]"])
        self.assertFalse(self.component._queue_preview_target("[T2]"))

        self.component._pending_target_ids.clear()
        self.component._active_target_id = "[T1]"
        self.assertFalse(self.component._queue_preview_target("[T2]"))

        self.component._active_target_id = None
        self.assertFalse(self.component._queue_preview_target("[T3]"))

    def test_highest_confidence_coordinate_is_published_once(self):
        self.component._active_target_id = "[T1]"
        self.component._request_started_at = time.monotonic() - 1.0
        self.component._min_detection_count[0] = 3
        self.component._geometry_settings = SimpleNamespace(
            stable_cluster_radius_m=0.012
        )
        self.component._samples.extend(
            [
                DetectionSample(0.72, (1.0, 2.0, 3.0), 1.0),
                DetectionSample(0.94, (4.12354, -5.67856, 6.00049), 2.0),
                DetectionSample(0.81, (7.0, 8.0, 9.0), 3.0),
            ]
        )
        self.component._publish_if_ready(time.monotonic())
        point = self.component._d_Coordinate.data
        self.assertEqual((point.x, point.y, point.z), (4.124, -5.679, 6.0))
        self.assertEqual(
            self.component._last_detection_overlay["point_output_m"],
            (4.124, -5.679, 6.0),
        )
        self.assertEqual(self.component._Target_Coordinate_OutOut.write_count, 1)
        self.assertIsNone(self.component._active_target_id)
        self.assertIn("Sent to target_point", self.component._last_output_status["text"])

    def test_failed_outport_write_keeps_request_active_and_retries(self):
        self.component._active_target_id = "[T1]"
        self.component._request_started_at = time.monotonic() - 1.0
        self.component._min_detection_count[0] = 1
        self.component._geometry_settings = SimpleNamespace(
            stable_cluster_radius_m=0.012
        )
        self.component._samples.append(
            DetectionSample(0.95, (0.315, -0.315, 0.1049), 1.0)
        )
        outport = self.component._Target_Coordinate_OutOut
        outport.write_result = False

        self.component._publish_if_ready(time.monotonic())

        self.assertEqual(outport.write_count, 1)
        self.assertEqual(self.component._active_target_id, "[T1]")
        self.assertTrue(self.component._output_write_failed)

        outport.write_result = True
        self.component._publish_if_ready(time.monotonic())

        self.assertEqual(outport.write_count, 2)
        self.assertIsNone(self.component._active_target_id)
        self.assertFalse(self.component._output_write_failed)

    def test_slow_recognition_waits_fifteen_seconds_before_timeout(self):
        self.component._active_target_id = "[T2]"
        self.component._request_started_at = 100.0
        self.component._samples.extend(
            [DetectionSample(0.8, (0.1, 0.2, 0.3), 101.0)] * 2
        )

        self.assertFalse(self.component._expire_request_if_needed(104.1))
        self.assertEqual(self.component._active_target_id, "[T2]")
        self.assertEqual(REQUEST_TIMEOUT_SEC, 15.0)

        self.assertTrue(self.component._expire_request_if_needed(115.0))
        self.assertIsNone(self.component._active_target_id)
        self.assertIn("Not sent", self.component._last_output_status["text"])
        self.assertIn("2/5 samples", self.component._last_output_status["text"])

    def test_non_finite_detection_point_is_discarded(self):
        point = self.component._refine_point_with_depth_roi(
            None, None, (float("nan"), 0.0, 1.0)
        )
        self.assertIsNone(point)

    def test_each_request_resets_temporal_filter_history(self):
        old_filter = object()
        new_filter = object()
        self.component._temporal_filter = old_filter
        self.component._rs = SimpleNamespace(temporal_filter=lambda: new_filter)
        self.component._pending_target_ids.append("[T1]")

        self.component._start_next_request()

        self.assertEqual(self.component._active_target_id, "[T1]")
        self.assertIs(self.component._temporal_filter, new_filter)
        self.assertEqual(self.component._filter_warmup_frames_remaining, 3)


if __name__ == "__main__":
    unittest.main()

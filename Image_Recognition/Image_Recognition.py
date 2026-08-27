#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

# <rtc-template block="description">
"""
 @file Image_Recognition.py
 @brief ModuleDescription
 @date $Date$


"""
# </rtc-template>

import logging
import math
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

from geometry_recognition import (
    CameraIntrinsics,
    DetectionSample,
    camera_to_arm,
    detect_target_from_color_at_fixed_depth,
    detect_target_from_depth,
    load_arm_camera_transform,
    load_geometry_configuration,
    normalize_target_id,
    resolve_path,
    select_stable_best_sample,
)


LOGGER = logging.getLogger("Image_Recognition")
COMPONENT_DIR = Path(__file__).resolve().parent
GEOMETRY_CONFIG_FILE = "config/geometry_targets.yaml"
REQUEST_TIMEOUT_SEC = 15.0
TEMPORAL_FILTER_WARMUP_FRAMES = 3
OUTPUT_WRITE_WARNING_INTERVAL_SEC = 1.0
PREVIEW_WINDOW_NAME = "Image_Recognition - RealSense"
PREVIEW_OVERLAY_DURATION_SEC = 5.0
PREVIEW_OUTPUT_STATUS_DURATION_SEC = 5.0


# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
image_recognition_spec = ["implementation_id", "Image_Recognition", 
         "type_name",         "Image_Recognition", 
         "description",       "ModuleDescription", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Category", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         "conf.default.camera_serial", "827112070187",
         "conf.default.color_width", "640",
         "conf.default.color_height", "480",
         "conf.default.depth_width", "848",
         "conf.default.depth_height", "480",
         "conf.default.camera_fps", "30",
         "conf.default.buffer_size", "8",
         "conf.default.min_detection_count", "5",
         "conf.default.confidence_threshold", "0.60",
         "conf.default.detection_window_sec", "1.0",
         "conf.default.depth_roi_radius", "2",
         "conf.default.min_depth_m", "0.35",
         "conf.default.max_depth_m", "0.55",
         "conf.default.arm_camera_transform_file", "config/T_arm_camera.yaml",

         "conf.__widget__.camera_serial", "text",
         "conf.__widget__.color_width", "text",
         "conf.__widget__.color_height", "text",
         "conf.__widget__.depth_width", "text",
         "conf.__widget__.depth_height", "text",
         "conf.__widget__.camera_fps", "text",
         "conf.__widget__.buffer_size", "spin.1",
         "conf.__widget__.min_detection_count", "spin",
         "conf.__widget__.confidence_threshold", "slider.0.05",
         "conf.__widget__.detection_window_sec", "spin.0.1",
         "conf.__widget__.depth_roi_radius", "spin.1",
         "conf.__widget__.min_depth_m", "spin.0.1",
         "conf.__widget__.max_depth_m", "spin.0.1",
         "conf.__widget__.arm_camera_transform_file", "text",
         "conf.__constraints__.buffer_size", "1<=x<=30",
         "conf.__constraints__.min_detection_count", "1<=x<=30",
         "conf.__constraints__.confidence_threshold", "0.0<=x<=1.0",
         "conf.__constraints__.detection_window_sec", "0.1<=x<=5.0",
         "conf.__constraints__.depth_roi_radius", "0<=x<=10",
         "conf.__constraints__.min_depth_m", "0.0<x<=10.0",
         "conf.__constraints__.max_depth_m", "0.0<x<=10.0",

         "conf.__type__.camera_serial", "String",
         "conf.__type__.color_width", "int",
         "conf.__type__.color_height", "int",
         "conf.__type__.depth_width", "int",
         "conf.__type__.depth_height", "int",
         "conf.__type__.camera_fps", "int",
         "conf.__type__.buffer_size", "int",
         "conf.__type__.min_detection_count", "int",
         "conf.__type__.confidence_threshold", "double",
         "conf.__type__.detection_window_sec", "double",
         "conf.__type__.depth_roi_radius", "int",
         "conf.__type__.min_depth_m", "double",
         "conf.__type__.max_depth_m", "double",
         "conf.__type__.arm_camera_transform_file", "String",

         ""]
# </rtc-template>

# <rtc-template block="component_description">
##
# @class Image_Recognition
# @brief ModuleDescription
# 
# 
# </rtc-template>
class Image_Recognition(OpenRTM_aist.DataFlowComponentBase):
	
    ##
    # @brief constructor
    # @param manager Maneger Object
    # 
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_Target = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        """
        """
        self._Target_In1In = OpenRTM_aist.InPort("Target_In1", self._d_Target)
        self._d_Coordinate = OpenRTM_aist.instantiateDataType(RTC.TimedPoint3D)
        """
        """
        self._Target_Coordinate_OutOut = OpenRTM_aist.OutPort("target_point", self._d_Coordinate)


		


        # initialize of configuration-data.
        # <rtc-template block="init_conf_param">
        """
        
         - Name:  camera_serial
         - DefaultValue: 827112070187
        """
        self._camera_serial = ['827112070187']
        """
        
         - Name:  color_width
         - DefaultValue: 640
        """
        self._color_width = [640]
        """
        
         - Name:  color_height
         - DefaultValue: 480
        """
        self._color_height = [480]
        """
        
         - Name:  depth_width
         - DefaultValue: 848
        """
        self._depth_width = [848]
        """
        
         - Name:  depth_height
         - DefaultValue: 480
        """
        self._depth_height = [480]
        """
        
         - Name:  camera_fps
         - DefaultValue: 30
        """
        self._camera_fps = [30]
        """
        
         - Name:  buffer_size
         - DefaultValue: 8
        """
        self._buffer_size = [8]
        """
        
         - Name:  min_detection_count
         - DefaultValue: 5
        """
        self._min_detection_count = [5]
        """
        
         - Name:  confidence_threshold
         - DefaultValue: 0.60
        """
        self._confidence_threshold = [0.60]
        """
        
         - Name:  detection_window_sec
         - DefaultValue: 1.0
        """
        self._detection_window_sec = [1.0]
        """
        
         - Name:  depth_roi_radius
         - DefaultValue: 2
        """
        self._depth_roi_radius = [2]
        """
        
         - Name:  min_depth_m
         - DefaultValue: 0.35
        """
        self._min_depth_m = [0.35]
        """
        
         - Name:  max_depth_m
         - DefaultValue: 0.55
        """
        self._max_depth_m = [0.55]
        """
        
         - Name:  arm_camera_transform_file
         - DefaultValue: config/T_arm_camera.yaml
        """
        self._arm_camera_transform_file = ['config/T_arm_camera.yaml']
		
        # </rtc-template>

        # Runtime resources. Camera access is opened only while the RTC is Active.
        self._rs = None
        self._pipeline = None
        self._pipeline_started = False
        self._align = None
        self._spatial_filter = None
        self._temporal_filter = None
        self._hole_filling_filter = None
        self._depth_to_disparity = None
        self._disparity_to_depth = None
        self._filter_warmup_frames_remaining = 0
        self._cv2 = None
        self._preview_available = False
        self._preview_error_logged = False
        self._last_detection_overlay = None
        self._last_output_status = None
        self._depth_scale = 0.001
        self._geometry_settings = None
        self._targets = {}
        self._transform = None
        self._output_frame = "camera"
        self._pending_target_ids = deque()
        self._active_target_id = None
        self._request_started_at = 0.0
        self._output_write_failed = False
        self._last_output_write_warning_at = 0.0
        self._samples = deque()
        self._sample_pixels = {}
        self._sample_bounding_boxes = {}
        self._sample_color_ratios = {}
        self._sample_edge_metrics = {}
        self._rng = np.random.default_rng()


		 
    ##
    #
    # The initialize action (on CREATED->ALIVE transition)
    # 
    # @return RTC::ReturnCode_t
    # 
    #
    def onInitialize(self):
        # Bind variables and configuration variable
        self.bindParameter("camera_serial", self._camera_serial, "827112070187")
        self.bindParameter("color_width", self._color_width, "640")
        self.bindParameter("color_height", self._color_height, "480")
        self.bindParameter("depth_width", self._depth_width, "848")
        self.bindParameter("depth_height", self._depth_height, "480")
        self.bindParameter("camera_fps", self._camera_fps, "30")
        self.bindParameter("buffer_size", self._buffer_size, "8")
        self.bindParameter("min_detection_count", self._min_detection_count, "5")
        self.bindParameter("confidence_threshold", self._confidence_threshold, "0.60")
        self.bindParameter("detection_window_sec", self._detection_window_sec, "1.0")
        self.bindParameter("depth_roi_radius", self._depth_roi_radius, "2")
        self.bindParameter("min_depth_m", self._min_depth_m, "0.35")
        self.bindParameter("max_depth_m", self._max_depth_m, "0.55")
        self.bindParameter("arm_camera_transform_file", self._arm_camera_transform_file, "config/T_arm_camera.yaml")
		
        # Set InPort buffers
        self.addInPort("Target_In1",self._Target_In1In)
		
        # Set OutPort buffers
        self.addOutPort("target_point",self._Target_Coordinate_OutOut)
		
        # Set service provider to Ports
		
        # Set service consumers to Ports
		
        # Set CORBA Service Ports
		
        return RTC.RTC_OK
	
    ##
    # 
    # The finalize action (on ALIVE->END transition)
    # 
    # @return RTC::ReturnCode_t
    #
    # 
    def onFinalize(self):
        self._stop_camera()
        self._clear_request_state()
        return RTC.RTC_OK
	
    ###
    ##
    ## The startup action when ExecutionContext startup
    ## 
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onStartup(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The shutdown action when ExecutionContext stop
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onShutdown(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ##
    #
    # The activated action (Active state entry action)
    #
    # @param ec_id target ExecutionContext Id
    # 
    # @return RTC::ReturnCode_t
    #
    #
    def _configure_depth_sensor_for_low_texture_surfaces(self, depth_sensor, rs):
        """Prefer dense projected depth without making activation depend on it."""

        try:
            if depth_sensor.supports(rs.option.emitter_enabled):
                depth_sensor.set_option(rs.option.emitter_enabled, 1.0)
            if depth_sensor.supports(rs.option.enable_auto_exposure):
                depth_sensor.set_option(rs.option.enable_auto_exposure, 1.0)
            if depth_sensor.supports(rs.option.visual_preset):
                high_density = rs.rs400_visual_preset.high_density
                depth_sensor.set_option(
                    rs.option.visual_preset,
                    float(getattr(high_density, "value", high_density)),
                )
            LOGGER.info(
                "RealSense depth sensor configured for emitter, auto exposure, "
                "and High Density where supported"
            )
        except Exception:
            LOGGER.warning(
                "RealSense depth options could not be fully applied; "
                "color fixed-depth fallback remains available",
                exc_info=True,
            )

    def onActivated(self, ec_id):
        del ec_id
        self._clear_request_state()
        self._last_detection_overlay = None
        self._preview_error_logged = False
        try:
            self._validate_configuration()
            geometry_path = resolve_path(COMPONENT_DIR, GEOMETRY_CONFIG_FILE)
            transform_path = resolve_path(
                COMPONENT_DIR, str(self._arm_camera_transform_file[0])
            )
            (
                self._geometry_settings,
                self._targets,
                self._output_frame,
            ) = load_geometry_configuration(geometry_path)
            if self._output_frame == "arm":
                self._transform = load_arm_camera_transform(transform_path)
            else:
                self._transform = np.eye(4, dtype=np.float64)
                LOGGER.warning(
                    "Camera-coordinate test mode is active: "
                    "target_point is not in the arm frame"
                )

            import cv2
            import pyrealsense2 as rs

            self._cv2 = cv2
            self._rs = rs
            self._pipeline = rs.pipeline()
            camera_config = rs.config()
            serial = str(self._camera_serial[0]).strip()
            if serial:
                camera_config.enable_device(serial)
            camera_config.enable_stream(
                rs.stream.depth,
                int(self._depth_width[0]),
                int(self._depth_height[0]),
                rs.format.z16,
                int(self._camera_fps[0]),
            )
            camera_config.enable_stream(
                rs.stream.color,
                int(self._color_width[0]),
                int(self._color_height[0]),
                rs.format.bgr8,
                int(self._camera_fps[0]),
            )
            profile = self._pipeline.start(camera_config)
            self._pipeline_started = True
            depth_sensor = profile.get_device().first_depth_sensor()
            self._depth_scale = float(depth_sensor.get_depth_scale())
            self._configure_depth_sensor_for_low_texture_surfaces(depth_sensor, rs)
            # Keep the native 640x480 RGB image as the reference and align the
            # depth frame to it.  Resampling RGB into the wider depth viewport
            # can introduce black invalid pixels and visible speckle noise.
            self._align = rs.align(rs.stream.color)
            # Glossy or strongly illuminated surfaces may contain small depth
            # holes.  Stabilize them across space and time before geometry and
            # depth-edge processing.  Mode 2 fills from the nearest neighbor,
            # which is preferable for small foreground objects.
            self._spatial_filter = rs.spatial_filter()
            self._temporal_filter = rs.temporal_filter()
            self._hole_filling_filter = rs.hole_filling_filter(2)
            self._depth_to_disparity = rs.disparity_transform(True)
            self._disparity_to_depth = rs.disparity_transform(False)
            try:
                cv2.namedWindow(PREVIEW_WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
                self._preview_available = True
            except cv2.error:
                self._preview_available = False
                LOGGER.warning(
                    "OpenCV preview window could not be created; "
                    "recognition and DataPort output will continue"
                )
            LOGGER.info(
                "Activated depth-geometry recognition with RealSense %s",
                serial or "auto",
            )
            return RTC.RTC_OK
        except Exception:
            LOGGER.exception("Image_Recognition activation failed")
            self._stop_camera()
            return RTC.RTC_ERROR
	
    ##
    #
    # The deactivated action (Active state exit action)
    #
    # @param ec_id target ExecutionContext Id
    #
    # @return RTC::ReturnCode_t
    #
    #
    def onDeactivated(self, ec_id):
        del ec_id
        self._stop_camera()
        self._clear_request_state()
        return RTC.RTC_OK
	
    ##
    #
    # The execution action that is invoked periodically
    #
    # @param ec_id target ExecutionContext Id
    #
    # @return RTC::ReturnCode_t
    #
    #
    def onExecute(self, ec_id):
        del ec_id
        self._receive_target_requests()
        self._start_next_request()
        now = time.monotonic()
        self._expire_request_if_needed(now)

        try:
            if self._pipeline is None or self._align is None:
                return RTC.RTC_OK
            frames = self._pipeline.poll_for_frames()
            if not frames:
                return RTC.RTC_OK
            aligned_frames = self._align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()
            if not depth_frame or not color_frame:
                return RTC.RTC_OK

            filtered_depth = self._depth_to_disparity.process(depth_frame)
            filtered_depth = self._spatial_filter.process(filtered_depth)
            filtered_depth = self._temporal_filter.process(filtered_depth)
            filtered_depth = self._disparity_to_depth.process(filtered_depth)
            filtered_depth = self._hole_filling_filter.process(filtered_depth)
            filtered_depth_frame = filtered_depth.as_depth_frame()
            if filtered_depth_frame:
                depth_frame = filtered_depth_frame

            color_image = np.asanyarray(color_frame.get_data()).copy()
            depth_m = (
                np.asanyarray(depth_frame.get_data()).astype(np.float32)
                * self._depth_scale
            )
            valid_depth = (
                (depth_m >= float(self._min_depth_m[0]))
                & (depth_m <= float(self._max_depth_m[0]))
            )
            depth_m = np.where(valid_depth, depth_m, np.nan)
            rs_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
            intrinsics = CameraIntrinsics(
                fx=float(rs_intrinsics.fx),
                fy=float(rs_intrinsics.fy),
                ppx=float(rs_intrinsics.ppx),
                ppy=float(rs_intrinsics.ppy),
            )
            if (
                self._active_target_id is not None
                and self._filter_warmup_frames_remaining > 0
            ):
                # Feed a few current frames into the newly-created temporal
                # filter without judging them.  This prevents previous target
                # positions and invalid-depth persistence from contaminating
                # the next recognition request.
                self._filter_warmup_frames_remaining -= 1
                self._show_camera_preview(color_image, now)
                return RTC.RTC_OK
            if self._active_target_id is not None:
                target_id = self._active_target_id
                target_definition = self._targets[target_id]
                detection = detect_target_from_depth(
                    depth_m=depth_m,
                    intrinsics=intrinsics,
                    target_id=target_id,
                    target_definition=target_definition,
                    settings=self._geometry_settings,
                    confidence_threshold=float(self._confidence_threshold[0]),
                    rng=self._rng,
                    color_bgr=color_image,
                )
                if detection is None:
                    detection = detect_target_from_color_at_fixed_depth(
                        color_bgr=color_image,
                        intrinsics=intrinsics,
                        target_id=target_id,
                        target_definition=target_definition,
                        settings=self._geometry_settings,
                        confidence_threshold=float(self._confidence_threshold[0]),
                    )
                if detection is not None:
                    detection_mode = getattr(detection, "detection_mode", "depth")
                    if detection_mode == "color_fixed_depth":
                        camera_point = np.asarray(
                            detection.point_camera_m, dtype=np.float64
                        )
                    else:
                        camera_point = self._refine_point_with_depth_roi(
                            depth_frame, intrinsics, detection.point_camera_m
                        )
                        if camera_point is None:
                            self._show_camera_preview(color_image, now)
                            return RTC.RTC_OK
                    if self._output_frame == "arm":
                        output_point = camera_to_arm(camera_point, self._transform)
                    else:
                        output_point = np.asarray(camera_point, dtype=np.float64)
                    sample = DetectionSample(
                        confidence=detection.confidence,
                        point_output_m=tuple(float(value) for value in output_point),
                        captured_at=now,
                    )
                    self._samples.append(sample)
                    pixel = self._project_camera_point(camera_point, intrinsics)
                    self._sample_pixels[now] = pixel
                    self._sample_bounding_boxes[now] = detection.bounding_box_xyxy
                    self._sample_color_ratios[now] = detection.color_ratio
                    self._sample_edge_metrics[now] = (
                        detection.edge_confidence,
                        detection.color_edge_ratio,
                        detection.depth_edge_ratio,
                    )
                    self._set_detection_overlay(
                        target_id,
                        sample.point_output_m,
                        sample.confidence,
                        pixel,
                        detection.bounding_box_xyxy,
                        detection.color_ratio,
                        self._sample_edge_metrics[now],
                        now,
                    )
                    self._set_output_status(
                        "Not sent: {} stability {}/{}".format(
                            (
                                "color fallback"
                                if detection_mode == "color_fixed_depth"
                                else "checking"
                            ),
                            len(self._samples),
                            int(self._min_detection_count[0]),
                        ),
                        (0, 255, 255),
                        now,
                    )
                    LOGGER.info(
                        "%s mode %s, observed dimensions %.1f x %.1f x %.1f mm, "
                        "geometry %.3f, visible face %s mm (%s), "
                        "rectangularity %.3f, "
                        "camera distance %.3f m, color %s, "
                        "color/depth edges %s/%s, combined %.3f",
                        target_id,
                        detection_mode,
                        *detection.observed_dimensions_mm,
                        detection.geometry_confidence,
                        (
                            "{:.1f} x {:.1f}".format(
                                *detection.observed_visible_face_mm
                            )
                            if detection.observed_visible_face_mm is not None
                            else "disabled"
                        ),
                        (
                            "{:.3f}".format(detection.visible_face_confidence)
                            if detection.visible_face_confidence is not None
                            else "disabled"
                        ),
                        detection.rectangularity,
                        detection.camera_distance_m,
                        (
                            "{:.3f}".format(detection.color_ratio)
                            if detection.color_ratio is not None
                            else "disabled"
                        ),
                        (
                            "{:.3f}".format(detection.color_edge_ratio)
                            if detection.color_edge_ratio is not None
                            else "disabled"
                        ),
                        (
                            "{:.3f}".format(detection.depth_edge_ratio)
                            if detection.depth_edge_ratio is not None
                            else "disabled"
                        ),
                        detection.confidence,
                    )
                    self._publish_if_ready(now)
            self._show_camera_preview(color_image, now)
        except Exception:
            LOGGER.exception("Depth frame processing failed")
        return RTC.RTC_OK

    def _validate_configuration(self):
        positive_integer_parameters = {
            "color_width": self._color_width[0],
            "color_height": self._color_height[0],
            "depth_width": self._depth_width[0],
            "depth_height": self._depth_height[0],
            "camera_fps": self._camera_fps[0],
            "buffer_size": self._buffer_size[0],
            "min_detection_count": self._min_detection_count[0],
        }
        for name, value in positive_integer_parameters.items():
            if int(value) <= 0:
                raise ValueError("{} must be positive".format(name))
        if int(self._depth_roi_radius[0]) < 0:
            raise ValueError("depth_roi_radius cannot be negative")
        if int(self._min_detection_count[0]) > int(self._buffer_size[0]):
            raise ValueError("min_detection_count cannot exceed buffer_size")
        if not 0.0 <= float(self._confidence_threshold[0]) <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1")
        if float(self._detection_window_sec[0]) <= 0.0:
            raise ValueError("detection_window_sec must be positive")
        if not 0.0 < float(self._min_depth_m[0]) < float(self._max_depth_m[0]):
            raise ValueError("Depth range must satisfy 0 < min_depth_m < max_depth_m")

    def _expire_request_if_needed(self, now):
        if (
            self._active_target_id is None
            or now - self._request_started_at < REQUEST_TIMEOUT_SEC
        ):
            return False

        target_id = self._active_target_id
        sample_count = len(self._samples)
        self._set_output_status(
            "Not sent: {} timed out ({}/{} samples)".format(
                target_id, sample_count, int(self._min_detection_count[0])
            ),
            (0, 0, 255),
            now,
        )
        LOGGER.warning(
            "Recognition of %s timed out after %.1f s with %d/%d samples; "
            "no coordinate was output",
            target_id,
            REQUEST_TIMEOUT_SEC,
            sample_count,
            int(self._min_detection_count[0]),
        )
        self._finish_request()
        return True

    def _receive_target_requests(self):
        while self._Target_In1In.isNew():
            received = self._Target_In1In.read()
            try:
                target_id = normalize_target_id(received.data)
            except (UnicodeError, ValueError):
                LOGGER.warning("Ignored invalid Target_In1 value: %r", received.data)
                continue
            definition = self._targets.get(target_id)
            if not definition or definition.get("enabled") is not True:
                LOGGER.warning(
                    "Ignored %s because its dimensions are not enabled", target_id
                )
                continue
            # Every received message is a new request, including repeated IDs.
            self._pending_target_ids.append(target_id)
            LOGGER.info("Queued target request %s", target_id)

    def _queue_preview_target(self, target_id):
        """Queue one target from a preview keyboard shortcut while idle."""

        if self._active_target_id is not None or self._pending_target_ids:
            LOGGER.info("Ignored preview request %s because recognition is busy", target_id)
            return False
        definition = self._targets.get(target_id)
        if not definition or definition.get("enabled") is not True:
            LOGGER.warning(
                "Ignored preview request %s because it is not enabled", target_id
            )
            return False
        self._pending_target_ids.append(target_id)
        LOGGER.info("Queued preview target request %s", target_id)
        return True

    def _start_next_request(self):
        if self._active_target_id is not None or not self._pending_target_ids:
            return
        self._active_target_id = self._pending_target_ids.popleft()
        self._request_started_at = time.monotonic()
        self._samples = deque(maxlen=int(self._buffer_size[0]))
        self._sample_pixels = {}
        self._sample_bounding_boxes = {}
        self._sample_color_ratios = {}
        self._sample_edge_metrics = {}
        self._last_detection_overlay = None
        self._last_output_status = None
        self._reset_temporal_filter_history()
        LOGGER.info("Started recognition of %s", self._active_target_id)

    def _reset_temporal_filter_history(self):
        """Start each request without depth history from an older scene."""

        self._filter_warmup_frames_remaining = TEMPORAL_FILTER_WARMUP_FRAMES
        if self._rs is not None:
            self._temporal_filter = self._rs.temporal_filter()
            LOGGER.debug(
                "Reset temporal depth history; warming up for %d frames",
                TEMPORAL_FILTER_WARMUP_FRAMES,
            )

    def _refine_point_with_depth_roi(
        self, depth_frame, intrinsics, estimated_point_camera_m
    ):
        point = np.asarray(estimated_point_camera_m, dtype=np.float64)
        if (
            point.shape != (3,)
            or not np.all(np.isfinite(point))
            or point[2] <= 0.0
        ):
            return None
        center_x = int(round(intrinsics.fx * point[0] / point[2] + intrinsics.ppx))
        center_y = int(round(intrinsics.fy * point[1] / point[2] + intrinsics.ppy))
        radius = int(self._depth_roi_radius[0])
        depths = []
        for y in range(
            max(0, center_y - radius),
            min(depth_frame.get_height(), center_y + radius + 1),
        ):
            for x in range(
                max(0, center_x - radius),
                min(depth_frame.get_width(), center_x + radius + 1),
            ):
                depth_value = float(depth_frame.get_distance(x, y))
                if (
                    math.isfinite(depth_value)
                    and float(self._min_depth_m[0]) <= depth_value
                    <= float(self._max_depth_m[0])
                ):
                    depths.append(depth_value)
        if not depths:
            return point
        median_depth = float(np.median(np.asarray(depths, dtype=np.float64)))
        return np.asarray(
            self._rs.rs2_deproject_pixel_to_point(
                depth_frame.profile.as_video_stream_profile().intrinsics,
                [center_x, center_y],
                median_depth,
            ),
            dtype=np.float64,
        )

    @staticmethod
    def _project_camera_point(point_camera_m, intrinsics):
        point = np.asarray(point_camera_m, dtype=np.float64)
        if point.shape != (3,) or not np.all(np.isfinite(point)) or point[2] <= 0.0:
            return None
        return (
            int(round(intrinsics.fx * point[0] / point[2] + intrinsics.ppx)),
            int(round(intrinsics.fy * point[1] / point[2] + intrinsics.ppy)),
        )

    def _set_detection_overlay(
        self,
        target_id,
        point_output_m,
        confidence,
        pixel,
        bounding_box_xyxy,
        color_ratio,
        edge_metrics,
        captured_at,
    ):
        self._last_detection_overlay = {
            "target_id": target_id,
            "point_output_m": tuple(float(value) for value in point_output_m),
            "confidence": float(confidence),
            "pixel": pixel,
            "bounding_box_xyxy": bounding_box_xyxy,
            "color_ratio": color_ratio,
            "edge_metrics": edge_metrics,
            "expires_at": captured_at + PREVIEW_OVERLAY_DURATION_SEC,
        }

    def _set_output_status(self, text, color, now):
        self._last_output_status = {
            "text": str(text),
            "color": color,
            "expires_at": now + PREVIEW_OUTPUT_STATUS_DURATION_SEC,
        }

    def _draw_preview_text(self, image, text, origin, color):
        self._cv2.putText(
            image,
            text,
            origin,
            self._cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            color,
            1,
            self._cv2.LINE_AA,
        )

    def _show_camera_preview(self, color_image, now):
        if not self._preview_available or self._cv2 is None:
            return
        try:
            image = color_image.copy()
            overlay = self._last_detection_overlay
            if overlay is not None and now > overlay["expires_at"]:
                self._last_detection_overlay = None
                overlay = None
            output_status = self._last_output_status
            if output_status is not None and now > output_status["expires_at"]:
                self._last_output_status = None
                output_status = None

            # Draw the detected region before the information panel so the
            # text always stays readable even when the object is underneath it.
            if overlay is not None:
                bounding_box = overlay["bounding_box_xyxy"]
                if bounding_box is not None:
                    height, width = image.shape[:2]
                    x1, y1, x2, y2 = bounding_box
                    x1 = max(0, min(width - 1, int(x1)))
                    y1 = max(0, min(height - 1, int(y1)))
                    x2 = max(0, min(width - 1, int(x2)))
                    y2 = max(0, min(height - 1, int(y2)))
                    if x2 > x1 and y2 > y1:
                        self._cv2.rectangle(
                            image, (x1, y1), (x2, y2), (0, 255, 0), 2
                        )
                pixel = overlay["pixel"]
                if pixel is not None:
                    pixel_x, pixel_y = pixel
                    height, width = image.shape[:2]
                    if 0 <= pixel_x < width and 0 <= pixel_y < height:
                        self._cv2.circle(
                            image, (pixel_x, pixel_y), 8, (0, 255, 0), 2
                        )
                        self._cv2.drawMarker(
                            image,
                            (pixel_x, pixel_y),
                            (0, 255, 0),
                            self._cv2.MARKER_CROSS,
                            18,
                            2,
                        )

            if self._active_target_id is None and self._pending_target_ids:
                status = "Queued: {}".format(self._pending_target_ids[0])
            elif self._active_target_id is None:
                status = "Waiting: send t1/t2 or press 1/2"
            else:
                status = "Searching: {}".format(self._active_target_id)
            lines = [(status, (0, 255, 255))]
            if output_status is not None:
                lines.append((output_status["text"], output_status["color"]))
            if self._output_write_failed:
                lines.append(
                    ("Output not connected; retrying", (0, 0, 255))
                )
            if overlay is not None:
                x, y, z = overlay["point_output_m"]
                lines.extend(
                    [
                        (
                            "Target: {}".format(overlay["target_id"]),
                            (0, 255, 0),
                        ),
                        ("Frame: {}".format(self._output_frame), (0, 255, 0)),
                        ("X [m]: {:+.4f}".format(x), (0, 255, 0)),
                        ("Y [m]: {:+.4f}".format(y), (0, 255, 0)),
                        ("Z [m]: {:+.4f}".format(z), (0, 255, 0)),
                        (
                            "Confidence: {:.3f}".format(overlay["confidence"]),
                            (0, 255, 0),
                        ),
                    ]
                )
                if overlay["color_ratio"] is not None:
                    lines.append(
                        (
                            "Color match: {:.1f}%".format(
                                100.0 * overlay["color_ratio"]
                            ),
                            (0, 255, 0),
                        )
                    )
                edge_metrics = overlay["edge_metrics"]
                if edge_metrics is not None:
                    _, color_edge_ratio, depth_edge_ratio = edge_metrics
                    if color_edge_ratio is not None and depth_edge_ratio is not None:
                        lines.extend(
                            [
                                (
                                    "Color edge: {:.1f}%".format(
                                        100.0 * color_edge_ratio
                                    ),
                                    (0, 255, 0),
                                ),
                                (
                                    "Depth edge: {:.1f}%".format(
                                        100.0 * depth_edge_ratio
                                    ),
                                    (0, 255, 0),
                                ),
                            ]
                        )

            # A translucent dark panel plus one text draw per row avoids the
            # doubled/overlapping appearance on a bright camera image.
            height, width = image.shape[:2]
            line_step = 24
            panel_width = min(width - 8, 360)
            panel_height = min(height - 8, 12 + line_step * len(lines))
            panel = image.copy()
            self._cv2.rectangle(
                panel,
                (4, 4),
                (panel_width, panel_height),
                (0, 0, 0),
                -1,
            )
            self._cv2.addWeighted(panel, 0.65, image, 0.35, 0.0, image)
            for index, (text, color) in enumerate(lines):
                self._draw_preview_text(
                    image,
                    text,
                    (12, 24 + line_step * index),
                    color,
                )

            self._cv2.imshow(PREVIEW_WINDOW_NAME, image)
            key = self._cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                self._preview_available = False
                self._cv2.destroyWindow(PREVIEW_WINDOW_NAME)
                LOGGER.info("RealSense preview window was closed by the user")
            elif key in (ord("1"), ord("2")):
                self._queue_preview_target("[T{}]".format(chr(key)))
        except Exception:
            self._preview_available = False
            if not self._preview_error_logged:
                LOGGER.exception(
                    "OpenCV preview failed; recognition and DataPort output continue"
                )
                self._preview_error_logged = True

    def _publish_if_ready(self, now):
        sample_count = len(self._samples)
        buffer_is_full = sample_count >= int(self._buffer_size[0])
        window_finished = (
            now - self._request_started_at
            >= float(self._detection_window_sec[0])
        )
        has_minimum_samples = sample_count >= int(self._min_detection_count[0])
        if not buffer_is_full and not (window_finished and has_minimum_samples):
            return

        best = select_stable_best_sample(
            self._samples,
            self._geometry_settings.stable_cluster_radius_m,
            int(self._min_detection_count[0]),
        )
        if best is None:
            LOGGER.debug(
                "Rejected unstable %s detections: no %d-sample cluster "
                "within %.1f mm",
                self._active_target_id,
                int(self._min_detection_count[0]),
                self._geometry_settings.stable_cluster_radius_m * 1000.0,
            )
            return
        self._set_detection_overlay(
            self._active_target_id,
            best.point_output_m,
            best.confidence,
            self._sample_pixels.get(best.captured_at),
            self._sample_bounding_boxes.get(best.captured_at),
            self._sample_color_ratios.get(best.captured_at),
            self._sample_edge_metrics.get(best.captured_at),
            now,
        )
        self._d_Coordinate.data.x = best.point_output_m[0]
        self._d_Coordinate.data.y = best.point_output_m[1]
        self._d_Coordinate.data.z = best.point_output_m[2]
        OpenRTM_aist.setTimestamp(self._d_Coordinate)
        write_succeeded = self._Target_Coordinate_OutOut.write()
        if not write_succeeded:
            self._output_write_failed = True
            self._set_output_status(
                "Send failed: target_point retrying", (0, 0, 255), now
            )
            if (
                now - self._last_output_write_warning_at
                >= OUTPUT_WRITE_WARNING_INTERVAL_SEC
            ):
                LOGGER.warning(
                    "target_point write failed; connect "
                    "Image_Recognition0.target_point to "
                    "Startup_Generation_Before0.target_point. Retrying while "
                    "the current recognition request remains active."
                )
                self._last_output_write_warning_at = now
            return
        self._output_write_failed = False
        self._set_output_status(
            "Sent to target_point: {}".format(self._active_target_id),
            (0, 255, 0),
            now,
        )
        LOGGER.info(
            "target_point [%s frame]: %s "
            "(%.6f, %.6f, %.6f) m, confidence %.3f",
            self._output_frame,
            self._active_target_id,
            *best.point_output_m,
            best.confidence,
        )
        self._finish_request()

    def _finish_request(self):
        self._active_target_id = None
        self._request_started_at = 0.0
        self._output_write_failed = False
        self._samples.clear()
        self._sample_pixels.clear()
        self._sample_bounding_boxes.clear()
        self._sample_color_ratios.clear()
        self._sample_edge_metrics.clear()
        self._filter_warmup_frames_remaining = 0

    def _clear_request_state(self):
        self._pending_target_ids.clear()
        self._active_target_id = None
        self._request_started_at = 0.0
        self._output_write_failed = False
        self._last_output_status = None
        self._samples = deque(maxlen=max(1, int(self._buffer_size[0])))
        self._sample_pixels = {}
        self._sample_bounding_boxes = {}
        self._sample_color_ratios = {}
        self._sample_edge_metrics = {}
        self._filter_warmup_frames_remaining = 0

    def _stop_camera(self):
        if self._cv2 is not None and self._preview_available:
            try:
                self._cv2.destroyWindow(PREVIEW_WINDOW_NAME)
                self._cv2.waitKey(1)
            except Exception:
                pass
        self._preview_available = False
        if self._pipeline is not None and self._pipeline_started:
            try:
                self._pipeline.stop()
            except Exception:
                LOGGER.exception("Failed to stop the RealSense pipeline cleanly")
        self._pipeline_started = False
        self._pipeline = None
        self._align = None
        self._spatial_filter = None
        self._temporal_filter = None
        self._hole_filling_filter = None
        self._depth_to_disparity = None
        self._disparity_to_depth = None
        self._filter_warmup_frames_remaining = 0
        self._rs = None
        self._cv2 = None
	
    ###
    ##
    ## The aborting action when main logic error occurred.
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onAborting(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The error action in ERROR state
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onError(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The reset action that is invoked resetting
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onReset(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The state update action that is invoked after onExecute() action
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onStateUpdate(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The action that is invoked when execution context's rate is changed
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onRateChanged(self, ec_id):
    #
    #    return RTC.RTC_OK
	



def Image_RecognitionInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=image_recognition_spec)
    manager.registerFactory(profile,
                            Image_Recognition,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Image_RecognitionInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Image_Recognition" + args)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    # remove --instance_name= option
    argv = [i for i in sys.argv if not "--instance_name=" in i]
    # Initialize manager
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()

if __name__ == "__main__":
    main()


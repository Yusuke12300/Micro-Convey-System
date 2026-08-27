#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

# <rtc-template block="description">
"""
 @file Image_RecognitionTest.py
 @brief ModuleDescription
 @date $Date$


"""
# </rtc-template>

from __future__ import print_function
import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist


# Import Service implementation class
# <rtc-template block="service_impl">

import Image_Recognition

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
image_recognitiontest_spec = ["implementation_id", "Image_RecognitionTest", 
         "type_name",         "Image_RecognitionTest", 
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
         "conf.default.depth_width", "640",
         "conf.default.depth_height", "480",
         "conf.default.camera_fps", "30",
         "conf.default.buffer_size", "5",
         "conf.default.min_detection_count", "3",
         "conf.default.confidence_threshold", "0.6",
         "conf.default.detection_window_sec", "0.5",
         "conf.default.depth_roi_radius", "2",
         "conf.default.min_depth_m", "0.2",
         "conf.default.max_depth_m", "2.0",
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
# @class Image_RecognitionTest
# @brief ModuleDescription
# 
# 
# </rtc-template>
class Image_RecognitionTest(OpenRTM_aist.DataFlowComponentBase):
    
    ##
    # @brief constructor
    # @param manager Maneger Object
    # 
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_Coordinate = OpenRTM_aist.instantiateDataType(RTC.TimedPoint3D)
        """
        """
        self._Target_Coordinate_OutIn = OpenRTM_aist.InPort("target_point", self._d_Coordinate)
        self._d_Target = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        """
        """
        self._Target_In1Out = OpenRTM_aist.OutPort("Target_In1", self._d_Target)


        


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
         - DefaultValue: 640
        """
        self._depth_width = [640]
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
         - DefaultValue: 5
        """
        self._buffer_size = [5]
        """
        
         - Name:  min_detection_count
         - DefaultValue: 3
        """
        self._min_detection_count = [3]
        """
        
         - Name:  confidence_threshold
         - DefaultValue: 0.6
        """
        self._confidence_threshold = [0.6]
        """
        
         - Name:  detection_window_sec
         - DefaultValue: 0.5
        """
        self._detection_window_sec = [0.5]
        """
        
         - Name:  depth_roi_radius
         - DefaultValue: 2
        """
        self._depth_roi_radius = [2]
        """
        
         - Name:  min_depth_m
         - DefaultValue: 0.2
        """
        self._min_depth_m = [0.2]
        """
        
         - Name:  max_depth_m
         - DefaultValue: 2.0
        """
        self._max_depth_m = [2.0]
        """
        
         - Name:  arm_camera_transform_file
         - DefaultValue: config/T_arm_camera.yaml
        """
        self._arm_camera_transform_file = ['config/T_arm_camera.yaml']
        
        # </rtc-template>


         
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
        self.bindParameter("depth_width", self._depth_width, "640")
        self.bindParameter("depth_height", self._depth_height, "480")
        self.bindParameter("camera_fps", self._camera_fps, "30")
        self.bindParameter("buffer_size", self._buffer_size, "5")
        self.bindParameter("min_detection_count", self._min_detection_count, "3")
        self.bindParameter("confidence_threshold", self._confidence_threshold, "0.6")
        self.bindParameter("detection_window_sec", self._detection_window_sec, "0.5")
        self.bindParameter("depth_roi_radius", self._depth_roi_radius, "2")
        self.bindParameter("min_depth_m", self._min_depth_m, "0.2")
        self.bindParameter("max_depth_m", self._max_depth_m, "2.0")
        self.bindParameter("arm_camera_transform_file", self._arm_camera_transform_file, "config/T_arm_camera.yaml")
        
        # Set InPort buffers
        self.addInPort("target_point",self._Target_Coordinate_OutIn)
        
        # Set OutPort buffers
        self.addOutPort("Target_In1",self._Target_In1Out)
        
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
    def onActivated(self, ec_id):
    
        return RTC.RTC_OK
    
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
    
        return RTC.RTC_OK
    
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
    
    def runTest(self):
        return True

def RunTest():
    manager = OpenRTM_aist.Manager.instance()
    comp = manager.getComponent("Image_RecognitionTest0")
    if comp is None:
        print('Component get failed.', file=sys.stderr)
        return False
    return comp.runTest()

def Image_RecognitionTestInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=image_recognitiontest_spec)
    manager.registerFactory(profile,
                            Image_RecognitionTest,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Image_RecognitionTestInit(manager)
    Image_Recognition.Image_RecognitionInit(manager)

    # Create a component
    comp = manager.createComponent("Image_RecognitionTest")

def main():
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager(True)

    ret = RunTest()
    mgr.shutdown()

    if ret:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()


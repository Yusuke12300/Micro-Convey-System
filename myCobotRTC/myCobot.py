#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file myCobot.py
 @brief myCobot Controller Component
 @date $Date$

 @author n-miyamoto@aist.go.jp

 LGPL

"""
from pymycobot.genre import Coord
from pymycobot.genre import Angle
from pymycobot import MyCobot280 
import sys
import os
sys.path.append(os.path.dirname(__file__))
from ManipulatorCommonInterface_Common_idl_example import *
from ManipulatorCommonInterface_Middle_idl_example import *
import JARA_ARM
import OpenRTM_aist
import RTC
import time


# Import RTM module


# Import Service implementation class
# <rtc-template block="service_impl">


# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
mycobot_spec = ["implementation_id", "myCobot",
                "type_name",         "myCobot",
                "description",       "myCobot Controller Component",
                "version",           "1.0.0",
                "vendor",            "TMU",
                "category",          "Manipulator",
                "activity_type",     "STATIC",
                "max_instance",      "1",
                "language",          "Python",
                "lang_type",         "SCRIPT",
                "conf.default.com_port", "COM3",
                "conf.default.baudrate", "115200",
                "conf.default.solenoid_pin", "2",
                "conf.default.motor_pin", "5",

                "conf.__widget__.com_port", "text",
                "conf.__widget__.baudrate", "radio",
                "conf.__widget__.solenoid_pin", "text",
                "conf.__widget__.motor_pin", "text",
                "conf.__constraints__.baudrate", "(1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200)",

                "conf.__type__.com_port", "string",
                "conf.__type__.baudrate", "int",
                "conf.__type__.solenoid_pin", "int",
                "conf.__type__.motor_pin", "int",

                ""]
# </rtc-template>

##
# @class myCobot
# @brief myCobot Controller Component
#
# myCobot制御コンポーネント
#
#


class myCobot(OpenRTM_aist.DataFlowComponentBase):

    ##
    # @brief constructor
    # @param manager Maneger Object
    #
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        """
		"""
        self._middlePort = OpenRTM_aist.CorbaPort("middle")
        """
		"""
        self._commonPort = OpenRTM_aist.CorbaPort("common")

        """
		"""
        self._JARA_ARM_ManipulatorCommonInterface_Middle = ManipulatorCommonInterface_Middle_i()
        """
		"""
        self._JARA_ARM_ManipulatorCommonInterface_Common = ManipulatorCommonInterface_Common_i()

        # initialize of configuration-data.
        # <rtc-template block="init_conf_param">
        """
		
		 - Name:  com_port
		 - DefaultValue: COM3
		"""
        self._com_port = ['COM3']
        """
		
		 - Name:  baudrate
		 - DefaultValue: 115200
		"""
        self._baudrate = [115200]
        """
		
		 - Name:  solenoid_pin
		 - DefaultValue: 2
		"""
        self._solenoid_pin = [2]
        """
		
		 - Name:  motor_pin
		 - DefaultValue: 5
		"""
        self._motor_pin = [5]

        self._mycobot = None

        # </rtc-template>

    ##
    #
    # The initialize action (on CREATED->ALIVE transition)
    # formaer rtc_init_entry()
    #
    # @return RTC::ReturnCode_t
    #
    #

    def onInitialize(self):
        # Bind variables and configuration variable
        self.bindParameter("com_port", self._com_port, "COM3")
        self.bindParameter("baudrate", self._baudrate, "115200")
        self.bindParameter("solenoid_pin", self._solenoid_pin, "2")
        self.bindParameter("motor_pin", self._motor_pin, "5")

        # Set InPort buffers

        # Set OutPort buffers

        # Set service provider to Ports
        self._middlePort.registerProvider("JARA_ARM_ManipulatorCommonInterface_Middle",
                                          "JARA_ARM::ManipulatorCommonInterface_Middle", self._JARA_ARM_ManipulatorCommonInterface_Middle)
        self._commonPort.registerProvider("JARA_ARM_ManipulatorCommonInterface_Common",
                                          "JARA_ARM::ManipulatorCommonInterface_Common", self._JARA_ARM_ManipulatorCommonInterface_Common)

        # Set service consumers to Ports

        # Set CORBA Service Ports
        self.addPort(self._middlePort)
        self.addPort(self._commonPort)

        try:
            self._mycobot = MyCobot280(self._com_port[0], self._baudrate[0])
            self._JARA_ARM_ManipulatorCommonInterface_Middle.setMyCobot(
                self._mycobot)
            self._JARA_ARM_ManipulatorCommonInterface_Middle.setSuctionPump(
                self._solenoid_pin[0], self._motor_pin[0])
            self._JARA_ARM_ManipulatorCommonInterface_Common.setMyCobot(
                self._mycobot)
        except BaseException:
            import traceback
            traceback.print_exc()

        return RTC.RTC_OK

    ###
    ##
    # The finalize action (on ALIVE->END transition)
    # formaer rtc_exiting_entry()
    ##
    # @return RTC::ReturnCode_t
    #
    ##
    # def onFinalize(self):
    #
    #	return RTC.RTC_OK

    ###
    ##
    # The startup action when ExecutionContext startup
    # former rtc_starting_entry()
    ##
    # @param ec_id target ExecutionContext Id
    ##
    # @return RTC::ReturnCode_t
    ##
    ##
    # def onStartup(self, ec_id):
    #
    #	return RTC.RTC_OK

    ###
    ##
    # The shutdown action when ExecutionContext stop
    # former rtc_stopping_entry()
    ##
    # @param ec_id target ExecutionContext Id
    ##
    # @return RTC::ReturnCode_t
    ##
    ##
    # def onShutdown(self, ec_id):
    #
    #	return RTC.RTC_OK

    ##
    #
    # The activated action (Active state entry action)
    # former rtc_active_entry()
    #
    # @param ec_id target ExecutionContext Id
    #
    # @return RTC::ReturnCode_t
    #
    #
    def onActivated(self, ec_id):
        if self._mycobot is None:
            try:
                self._mycobot = MyCobot280(self._com_port[0])
                self._JARA_ARM_ManipulatorCommonInterface_Middle.setMyCobot(
                    self._mycobot)
                self._JARA_ARM_ManipulatorCommonInterface_Middle.setSuctionPump(
                    self._solenoid_pin[0], self._motor_pin[0])
                self._JARA_ARM_ManipulatorCommonInterface_Common.setMyCobot(
                    self._mycobot)
            except BaseException:
                import traceback
                traceback.print_exc()
                return RTC.RTC_ERROR
        return RTC.RTC_OK

    ###
    ##
    # The deactivated action (Active state exit action)
    # former rtc_active_exit()
    ##
    # @param ec_id target ExecutionContext Id
    ##
    # @return RTC::ReturnCode_t
    ##
    ##
    # def onDeactivated(self, ec_id):
    #
    #	return RTC.RTC_OK

    ###
    ##
    # The execution action that is invoked periodically
    # former rtc_active_do()
    ##
    # @param ec_id target ExecutionContext Id
    ##
    # @return RTC::ReturnCode_t
    ##
    ##
    # def onExecute(self, ec_id):
    #
    #	return RTC.RTC_OK

    ###
    ##
    # The aborting action when main logic error occurred.
    # former rtc_aborting_entry()
    ##
    # @param ec_id target ExecutionContext Id
    ##
    # @return RTC::ReturnCode_t
    ##
    ##
    # def onAborting(self, ec_id):
    #
    #	return RTC.RTC_OK

    ###
    ##
    # The error action in ERROR state
    # former rtc_error_do()
    ##
    # @param ec_id target ExecutionContext Id
    ##
    # @return RTC::ReturnCode_t
    ##
    ##
    # def onError(self, ec_id):
    #
    #	return RTC.RTC_OK

    ###
    ##
    # The reset action that is invoked resetting
    # This is same but different the former rtc_init_entry()
    ##
    # @param ec_id target ExecutionContext Id
    ##
    # @return RTC::ReturnCode_t
    ##
    ##
    # def onReset(self, ec_id):
    #
    #	return RTC.RTC_OK

    ###
    ##
    # The state update action that is invoked after onExecute() action
    # no corresponding operation exists in OpenRTm-aist-0.2.0
    ##
    # @param ec_id target ExecutionContext Id
    ##
    # @return RTC::ReturnCode_t
    ##

    ##
    # def onStateUpdate(self, ec_id):
    #
    #	return RTC.RTC_OK

    ###
    ##
    # The action that is invoked when execution context's rate is changed
    # no corresponding operation exists in OpenRTm-aist-0.2.0
    ##
    # @param ec_id target ExecutionContext Id
    ##
    # @return RTC::ReturnCode_t
    ##
    ##
    # def onRateChanged(self, ec_id):
    #
    #	return RTC.RTC_OK


def myCobotInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=mycobot_spec)
    manager.registerFactory(profile,
                            myCobot,
                            OpenRTM_aist.Delete)


def MyModuleInit(manager):
    myCobotInit(manager)

    # Create a component
    comp = manager.createComponent("myCobot")


def main():
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()


if __name__ == "__main__":
    main()

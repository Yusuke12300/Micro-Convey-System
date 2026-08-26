#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file myCobotTest.py
 @brief myCobot Test Component
 @date $Date$


"""
import JARA_ARM
import OpenRTM_aist
import RTC
import sys
import time
import math
sys.path.append(".")

# Import RTM module


# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">


# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
mycobottest_spec = ["implementation_id", "myCobotTest",
                    "type_name",         "myCobotTest",
                    "description",       "myCobot Test Component",
                    "version",           "1.0.0",
                    "vendor",            "TMU",
                    "category",          "Manipulator",
                    "activity_type",     "STATIC",
                    "max_instance",      "1",
                    "language",          "Python",
                    "lang_type",         "SCRIPT",
                    ""]
# </rtc-template>

##
# @class myCobotTest
# @brief myCobot Test Component
#
#


class myCobotTest(OpenRTM_aist.DataFlowComponentBase):

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
        self._JARA_ARM_ManipulatorCommonInterface_Middle = OpenRTM_aist.CorbaConsumer(
            interfaceType=JARA_ARM.ManipulatorCommonInterface_Middle)
        """
        """
        self._JARA_ARM_ManipulatorCommonInterface_Common = OpenRTM_aist.CorbaConsumer(
            interfaceType=JARA_ARM.ManipulatorCommonInterface_Common)

        # initialize of configuration-data.
        # <rtc-template block="init_conf_param">

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

        # Set InPort buffers

        # Set OutPort buffers

        # Set service provider to Ports

        # Set service consumers to Ports
        self._middlePort.registerConsumer("JARA_ARM_ManipulatorCommonInterface_Middle",
                                          "JARA_ARM::ManipulatorCommonInterface_Middle", self._JARA_ARM_ManipulatorCommonInterface_Middle)
        self._commonPort.registerConsumer("JARA_ARM_ManipulatorCommonInterface_Common",
                                          "JARA_ARM::ManipulatorCommonInterface_Common", self._JARA_ARM_ManipulatorCommonInterface_Common)

        # Set CORBA Service Ports
        self.addPort(self._middlePort)
        self.addPort(self._commonPort)

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

    ###
    ##
    # The activated action (Active state entry action)
    # former rtc_active_entry()
    ##
    # @param ec_id target ExecutionContext Id
    ##
    # @return RTC::ReturnCode_t
    ##
    ##
    # def onActivated(self, ec_id):
    #
    #	return RTC.RTC_OK

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

    ##
    #
    # The execution action that is invoked periodically
    # former rtc_active_do()
    #
    # @param ec_id target ExecutionContext Id
    #
    # @return RTC::ReturnCode_t
    #
    #
    def onExecute(self, ec_id):
        print("input command:")
        s = input()

        commands = s.split(" ")

        middle = self._JARA_ARM_ManipulatorCommonInterface_Middle._ptr()
        common = self._JARA_ARM_ManipulatorCommonInterface_Common._ptr()

        try:
            if commands[0] == "moveAbs":
                x = float(commands[1]) / 1000.0
                y = float(commands[2]) / 1000.0
                z = float(commands[3]) / 1000.0
                ret = middle.moveLinearCartesianAbs(
                    JARA_ARM.CarPosWithElbow([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z]], 0,  0))
                print(ret)
            elif commands[0] == "moveRel":
                x = float(commands[1]) / 1000.0
                y = float(commands[2]) / 1000.0
                z = float(commands[3]) / 1000.0
                ret = middle.moveLinearCartesianRel(
                    JARA_ARM.CarPosWithElbow([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z]], 0,  0))
                print(ret)
            elif commands[0] == "jointAbs":
                j0 = float(commands[1]) * math.pi/180
                j1 = float(commands[2]) * math.pi/180
                j2 = float(commands[3]) * math.pi/180
                j3 = float(commands[4]) * math.pi/180
                j4 = float(commands[5]) * math.pi/180
                j5 = float(commands[6]) * math.pi/180
                ret = middle.movePTPJointAbs([j0, j1, j2, j3, j4, j5])
                print(ret)
            elif commands[0] == "JointRel":
                j0 = float(commands[1]) * math.pi/180
                j1 = float(commands[2]) * math.pi/180
                j2 = float(commands[3]) * math.pi/180
                j3 = float(commands[4]) * math.pi/180
                j4 = float(commands[5]) * math.pi/180
                j5 = float(commands[6]) * math.pi/180
                ret = middle.movePTPJointRel([j0, j1, j2, j3, j4, j5])
                print(ret)
            elif commands[0] == "pause":
                ret = middle.pause()
                print(ret)
            elif commands[0] == "resume":
                ret = middle.resume()
                print(ret)
            elif commands[0] == "stop":
                ret = middle.stop()
                print(ret)
            elif commands[0] == "setSpeed":
                ret = middle.setSpeedCartesian(int(commands[1]))
                print(ret)
            elif commands[0] == "setSpeedJoint":
                ret = middle.setSpeedJoint(int(commands[1]))
                print(ret)
            elif commands[0] == "setHome":
                j0 = float(commands[1]) * math.pi/180
                j1 = float(commands[2]) * math.pi/180
                j2 = float(commands[3]) * math.pi/180
                j3 = float(commands[4]) * math.pi/180
                j4 = float(commands[5]) * math.pi/180
                j5 = float(commands[6]) * math.pi/180
                ret = middle.setHome([j0, j1, j2, j3, j4, j5])
                print(ret)
            elif commands[0] == "getHome":
                ret, home = middle.getHome()
                print(ret, home)
            elif commands[0] == "goHome":
                ret = middle.goHome()
                print(ret)
            elif commands[0] == "closeGripper":
                ret = middle.closeGripper()
                print(ret)
            elif commands[0] == "openGripper":
                ret = middle.openGripper()
                print(ret)
            elif commands[0] == "servoOFF":
                ret = common.servoOFF()
                print(ret)
            elif commands[0] == "servoON":
                ret = common.servoON()
                print(ret)
        except BaseException:
            import traceback
            traceback.print_exc()

        return RTC.RTC_OK

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


def myCobotTestInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=mycobottest_spec)
    manager.registerFactory(profile,
                            myCobotTest,
                            OpenRTM_aist.Delete)


def MyModuleInit(manager):
    myCobotTestInit(manager)

    # Create a component
    comp = manager.createComponent("myCobotTest")


def main():
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()


if __name__ == "__main__":
    main()

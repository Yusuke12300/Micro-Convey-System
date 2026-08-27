#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file ManipulatorCommonInterface_Middle_idl_example.py
 @brief Python example implementations generated from ManipulatorCommonInterface_Middle.idl
 @date $Date$

 @author n-miyamoto@aist.go.jp

 LGPL

"""

import omniORB
from omniORB import CORBA, PortableServer
import JARA_ARM
import JARA_ARM__POA

from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle
from pymycobot.genre import Coord

import math3d
import math
import time
import numpy

def diffMatrix(R4_target, R4_current, e):

    R_current = R4_current[:, :3]
    t_current = R4_current[:, 3]

    R_target = R4_target[:, :3]
    t_target = R4_target[:, 3]

    R_diff = R_target @ R_current.T

    cos_theta = (numpy.trace(R_diff) - 1.0) / 2.0
    cos_theta = numpy.clip(cos_theta, -1.0, 1.0)

    rot_diff = numpy.arccos(cos_theta)

    position_error = numpy.linalg.norm(t_target - t_current)

    if rot_diff+position_error > e:
        return True
    return False
    

    



class ManipulatorCommonInterface_Middle_i (JARA_ARM__POA.ManipulatorCommonInterface_Middle):
    """
    @class ManipulatorCommonInterface_Middle_i
    Example class implementing IDL interface JARA_ARM.ManipulatorCommonInterface_Middle
    """

    def __init__(self):
        """
        @brief standard constructor
        Initialise member variables here
        """
        self._mycobot = None
        self._spdCartesianRatio = 50
        self._spdJointRatio = 50
        self._home = [0, 0, 0, 0, 0, 0]

        self._solenoid_pin = 2
        self._motor_pin = 5

        self._prePos = numpy.array([[-1.0, 0.0, 0.0, 0.0], [0.0, 0.0, -1.0, 0.0], [0.0, -1.0, 0.0, 0.4]])

    def setMyCobot(self, mycobot):
        self._mycobot = mycobot

    def setSuctionPump(self, solenoid_pin, motor_pin):
        self._solenoid_pin = solenoid_pin
        self._motor_pin = motor_pin

    # RETURN_ID closeGripper()

    def closeGripper(self):
        self._mycobot.set_basic_output(self._solenoid_pin, 0)
        time.sleep(0.5)
        self._mycobot.set_basic_output(self._motor_pin, 0)
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID getBaseOffset(out HgMatrix offset)
    def getBaseOffset(self):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result, offset

    # RETURN_ID getFeedbackPosCartesian(out CarPosWithElbow pos)
    def getFeedbackPosCartesian(self):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result, pos

    # RETURN_ID getMaxSpeedCartesian(out CartesianSpeed speed)
    def getMaxSpeedCartesian(self):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result, speed

    # RETURN_ID getMaxSpeedJoint(out DoubleSeq speed)
    def getMaxSpeedJoint(self):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result, speed

    # RETURN_ID getMinAccelTimeCartesian(out double aclTime)
    def getMinAccelTimeCartesian(self):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result, aclTime

    # RETURN_ID getMinAccelTimeJoint(out double aclTime)
    def getMinAccelTimeJoint(self):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result, aclTime

    # RETURN_ID getSoftLimitCartesian(out LimitValue xLimit, out LimitValue yLimit, out LimitValue zLimit)
    def getSoftLimitCartesian(self):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result, xLimit, yLimit, zLimit

    # RETURN_ID moveGripper(in ULONG angleRatio)
    def moveGripper(self, angleRatio):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID moveLinearCartesianAbs(in CarPosWithElbow carPoint)
    def moveLinearCartesianAbs(self, carPoint):
        targetPos = numpy.array(carPoint.carPos)
        if diffMatrix(targetPos, self._prePos, 0.01):
            self._prePos = targetPos
        else:
            return JARA_ARM.RETURN_ID(0, "OK")
        trans = math3d.Transform(carPoint.carPos)
        pos = trans.pos
        #vec = trans.pose_vector
        vec = trans.orient.to_euler('xyz')
        x = pos.x * 1000
        y = pos.y * 1000
        z = pos.z * 1000
        roll = vec[0]*180/math.pi
        pitch = vec[1]*180/math.pi
        yaw = vec[2]*180/math.pi
        self._mycobot.sync_send_coords(
            [x, y, z, roll, pitch, yaw], self._spdCartesianRatio, 1)
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID moveLinearCartesianRel(in CarPosWithElbow carPoint)
    def moveLinearCartesianRel(self, carPoint):
        coords = self._mycobot.get_coords()
        print(coords)
        trans = math3d.Transform(carPoint.carPos)
        pos = trans.pos
        #vec = trans.pose_vector
        vec = trans.orient.to_euler('xyz')
        x = pos.x * 1000 + coords[0]
        y = pos.y * 1000 + coords[1]
        z = pos.z * 1000 + coords[2]
        roll = vec[0]*180/math.pi + coords[3]
        pitch = vec[1]*180/math.pi + coords[4]
        yaw = vec[2]*180/math.pi + coords[5]
        self._mycobot.sync_send_coords(
            [x, y, z, roll, pitch, yaw], self._spdCartesianRatio, 1)
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID movePTPCartesianAbs(in CarPosWithElbow carPoint)
    def movePTPCartesianAbs(self, carPoint):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID movePTPCartesianRel(in CarPosWithElbow carPoint)
    def movePTPCartesianRel(self, carPoint):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID movePTPJointAbs(in JointPos jointPoints)
    def movePTPJointAbs(self, jointPoints):
        angles = [s*180/math.pi for s in jointPoints]
        self._mycobot.sync_send_angles(angles, self._spdJointRatio)
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID movePTPJointRel(in JointPos jointPoints)
    def movePTPJointRel(self, jointPoints):
        current_angles = self._mycobot.get_radians()
        angles = []
        for i in range(0, len(jointPoints)):
            angles.append((current_angles[i] + jointPoints[i])*180/math.pi)

        self._mycobot.sync_send_angles(angles, self._spdJointRatio)
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID openGripper()
    def openGripper(self):
        self._mycobot.set_basic_output(self._motor_pin, 1)
        time.sleep(0.5)
        self._mycobot.set_basic_output(self._solenoid_pin, 1)
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID pause()
    def pause(self):
        self._mycobot.pause()
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID resume()
    def resume(self):
        self._mycobot.resume()
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID stop()
    def stop(self):
        self._mycobot.stop()
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID setAccelTimeCartesian(in double aclTime)
    def setAccelTimeCartesian(self, aclTime):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID setAccelTimeJoint(in double aclTime)
    def setAccelTimeJoint(self, aclTime):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID setBaseOffset(in HgMatrix offset)
    def setBaseOffset(self, offset):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID setControlPointOffset(in HgMatrix offset)
    def setControlPointOffset(self, offset):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID setMaxSpeedCartesian(in CartesianSpeed speed)
    def setMaxSpeedCartesian(self, speed):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID setMaxSpeedJoint(in DoubleSeq speed)
    def setMaxSpeedJoint(self, speed):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID setMinAccelTimeCartesian(in double aclTime)
    def setMinAccelTimeCartesian(self, aclTime):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID setMinAccelTimeJoint(in double aclTime)
    def setMinAccelTimeJoint(self, aclTime):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID setSoftLimitCartesian(in LimitValue xLimit, in LimitValue yLimit, in LimitValue zLimit)
    def setSoftLimitCartesian(self, xLimit, yLimit, zLimit):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID setSpeedCartesian(in ULONG spdRatio)
    def setSpeedCartesian(self, spdRatio):
        self._spdCartesianRatio = spdRatio
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID setSpeedJoint(in ULONG spdRatio)
    def setSpeedJoint(self, spdRatio):
        self._spdJointRatio = spdRatio
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID moveCircularCartesianAbs(in CarPosWithElbow carPointR, in CarPosWithElbow carPointT)
    def moveCircularCartesianAbs(self, carPointR, carPointT):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID moveCircularCartesianRel(in CarPosWithElbow carPointR, in CarPosWithElbow carPointT)
    def moveCircularCartesianRel(self, carPointR, carPointT):
        raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)
        # *** Implement me
        # Must return: result

    # RETURN_ID setHome(in JointPos jointPoint)
    def setHome(self, jointPoint):
        self._home = [s*180/math.pi for s in jointPoint]
        return JARA_ARM.RETURN_ID(0, "OK")

    # RETURN_ID getHome(out JointPos jointPoint)
    def getHome(self):
        return JARA_ARM.RETURN_ID(0, "OK"), self._home

    # RETURN_ID goHome()
    def goHome(self):
        self._mycobot.sync_send_angles(self._home, self._spdJointRatio)
        return JARA_ARM.RETURN_ID(0, "OK")


if __name__ == "__main__":
    import sys

    # Initialise the ORB
    orb = CORBA.ORB_init(sys.argv)

    # As an example, we activate an object in the Root POA
    poa = orb.resolve_initial_references("RootPOA")

    # Create an instance of a servant class
    servant = ManipulatorCommonInterface_Middle_i()

    # Activate it in the Root POA
    poa.activate_object(servant)

    # Get the object reference to the object
    objref = servant._this()

    # Print a stringified IOR for it
    print(orb.object_to_string(objref))

    # Activate the Root POA's manager
    poa._get_the_POAManager().activate()

    # Run the ORB, blocking this thread
    orb.run()

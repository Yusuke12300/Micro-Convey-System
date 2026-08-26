#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

# <rtc-template block="description">
"""
 @file myCobot280Io.py
 @brief myCobot Choreonoid Body Io Component
 @date $Date$


"""
# </rtc-template>

import sys
import time
sys.path.append(".")

import cnoid.OpenRTMPythonPlugin
import cnoid.Body

# Import RTM module
import RTC
import OpenRTM_aist


# Import Service implementation class
# <rtc-template block="service_impl">
from ManipulatorCommonInterface_Middle_idl_example import *
from ManipulatorCommonInterface_Common_idl_example import *

import numpy

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
mycobot280io_spec = ["implementation_id", "myCobot280Io", 
         "type_name",         "myCobot280Io", 
         "description",       "myCobot Choreonoid Body Io Component", 
         "version",           "1.0.0", 
         "vendor",            "AIST", 
         "category",          "Simulator", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]
# </rtc-template>

# <rtc-template block="component_description">
##
# @class myCobot280Io
# @brief myCobot Choreonoid Body Io Component
# 
# 
# </rtc-template>
class myCobot280Io(OpenRTM_aist.DataFlowComponentBase):
	
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
        self._JARA_ARM_ManipulatorCommonInterface_Middle = ManipulatorCommonInterface_Middle_i(self)
        """
        """
        self._JARA_ARM_ManipulatorCommonInterface_Common = ManipulatorCommonInterface_Common_i(self)

        self.ioBody = None
		
        self._target = 0.0
        self._target_angles = []
        self._target_pos = None


        # initialize of configuration-data.
        # <rtc-template block="init_conf_param">
		
        # </rtc-template>

    def setBody(self, body):

        self.ioBody = body
        self.joints = [self.ioBody.link("joint2"), self.ioBody.link("joint3"), self.ioBody.link("joint4"), 
                       self.ioBody.link("joint5"), self.ioBody.link("joint6"), self.ioBody.link("joint6_flange")]
        
        
        for joint in self.joints:
            joint.setActuationMode(cnoid.Body.Link.JointAngle)


        """

        #for joint in self.joints:
        #cnoid.OpenRTMPythonPlugin.set_q_target(joint, self._target)
        #self._target += 0.0002
        base = self.ioBody.link("g_base")
        ee = self.joints[-1]
        #path = cnoid.Body.getCustomJointPath(self.ioBody, base, ee)
        path = cnoid.Body.getCustomJointPath(self.ioBody, base, ee)
        path.setNumericalIkMaxIkError(0.005)
        path.setNumericalIkDampingConstant(0.02)
        #path.setNumericalIkDeltaScale(0.5)
        #path.calcForwardKinematics()
        print(path.isBestEffortIkMode())

        #pos = []
        #for joint in self.joints:
        #    pos.append(joint.q)
        
        #T = path.endLink.T.copy()
        #T = self.joints[-1].T.copy()
        
        T = numpy.array([[-9.95796883e-17,  1.00000000e+00, -1.34924605e-11,  3.14388635e-08],
                         [-1.00000000e+00, -1.49140571e-16, -3.67321860e-06, -6.46210270e-02],
                         [-3.67321860e-06,  1.34924605e-11,  1.00000000e+00,  4.11139763e-01],
                         [ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  1.00000000e+00]])
        #T[0,3] += 0.01
        #T[1,3] -= 0.001
        #T[2,3] -= 0.01
        #print(path.isCustomIkDisabled())
        #print(path.hasCustomIK())
        #print(path.calcInverseKinematics(T))
        #print(path.baseLink.p)
        #print(path.endLink.p)
        #print(T)
        #print(path.calcInverseKinematics(T))
        print(path.getNumJoints())
        #print([path.getJoint(0).q, path.getJoint(1).q, path.getJoint(2).q, path.getJoint(3).q, path.getJoint(4).q])
        
        if path.calcInverseKinematics(T):
            angles = []
            for i in range(path.getNumJoints()):
                joint = path.getJoint(i)
                angles.append(joint.q)
                #print(joint)
                #joint.q = pos[i+1]
                #cnoid.OpenRTMPythonPlugin.set_q_target(joint, joint.q)
                #print(i)
                #print(joint.q_target)
                #print(joint.q)
            #size = 100
            #move = 
            #for i in range(size):
            #self._target_angles
        """

        

    def inputFromSimulator(self):
        if self.ioBody:
            pass
    
    def outputToSimulator(self):
        if self.ioBody:
            if self._target_angles:
                for i in range(len(self.joints)):
                    joint = self.joints[i]
                    angle = self._target_angles[0][i]
                    cnoid.OpenRTMPythonPlugin.set_q_target(joint, angle)
                del self._target_angles[0]
            #cnoid.OpenRTMPythonPlugin.set_q_target(self.ioBody.link("joint6_flange"), 0)
                
            """
            if self._target_pos is not None:
                print(self._target_pos)
                base = self.ioBody.link("g_base")
                ee = self.joints[-1]
                path = cnoid.Body.getCustomJointPath(self.ioBody, base, ee)
                path.setNumericalIkMaxIkError(0.0005)
                path.setNumericalIkDampingConstant(0.02)
                path.setBestEffortIkMode(True)

                T = self.joints[-1].T.copy()
                T[0] = self._target_pos[0]
                T[1] = self._target_pos[1]
                T[2] = self._target_pos[2]
                #T[0,3] += 0.0005
                #T[1,3] -= 0.001
                #T[2,3] -= 0.0005

                #print([T[0,3], T[1,3], T[2,3]])

                print(path.calcInverseKinematics(T))

                #if path.calcInverseKinematics(T):
                for i in range(path.getNumJoints()):
                    joint = path.getJoint(i)
                    cnoid.OpenRTMPythonPlugin.set_q_target(joint, joint.q)
            """

    def getAngles(self):
        angles = []
        for joint in self.joints:
            angles.append(joint.q_target)
        return angles


    def setTargetPos(self, pos, abs=True):
        print(pos)
        self._target_pos = numpy.array(pos)
        
        if self.ioBody:
            base = self.ioBody.link("g_base")
            ee = self.joints[-1]
            path = cnoid.Body.getCustomJointPath(self.ioBody, base, ee)
            path.setNumericalIkMaxIkError(0.0005)
            path.setNumericalIkDampingConstant(0.1)
            path.setBestEffortIkMode(True)
            
            for i in range(path.getNumJoints()):
                joint = path.getJoint(i)

            T = self.joints[-1].T.copy()
            #print(T)

            
            
            if abs:
                R_change = numpy.array([
                    #[ 0, 0, 1],
                    #[-1, 0, 0],
                    #[ 0, -1, 0]
                    #[ 0, 0, 1],
                    #[ 1, 0, 0],
                    #[ 0, 1, 0]
                    [ 0, -1, 0],
                    [ 1, 0, 0],
                    [ 0, 0, 1]
                ], dtype=float)
                T[0] = self._target_pos[0]
                T[1] = self._target_pos[1]
                T[2] = self._target_pos[2]

                T[:3, :3] = R_change @ T[:3, :3]
            else:
                T[0,3] += self._target_pos[0,3]
                T[1,3] += self._target_pos[1,3]
                T[2,3] += self._target_pos[2,3]

                T[:3, :3] = self._target_pos[:3, :3] @ T[:3, :3]
            

            path.calcInverseKinematics(T)



            goal = []

            for i in range(path.getNumJoints()):
                joint = path.getJoint(i)
                goal.append(joint.q)
                #cnoid.OpenRTMPythonPlugin.set_q_target(joint, joint.q)
                

            delta = 1000
            
            
            for i in range(delta):
                target_angle = []
                for j in range(len(goal)):
                    target_angle.append(goal[j] * float(i)/float(delta) + self.joints[j].q_target* float(delta-i)/float(delta))

                self._target_angles.append(target_angle)

    def setTargetAngle(self, angles, abs=True):
        if abs:
            goal = angles
        else:
            goal = [self.joints[i].q_target+angles[i] for i in len(angles)]
            

            
        delta = 1000
        for i in range(delta):
            target_angle = []
            for j in range(len(angles)):
                target_angle.append(angles[j] * float(i)/float(delta) + self.joints[j].q_target* float(delta-i)/float(delta))

            self._target_angles.append(target_angle)



    def waitControl(self):
        count = 0
        size = len(self._target_angles)
        while self._target_angles:
            #print(self._target_angles)
            time.sleep(0.01)
            if len(self._target_angles) == size:
                count += 1
            else:
                count = 0
                size = len(self._target_angles)
            if count > 100:
                return False
        return True
            
            





		 
    ##
    #
    # The initialize action (on CREATED->ALIVE transition)
    # 
    # @return RTC::ReturnCode_t
    # 
    #
    def onInitialize(self):
        # Bind variables and configuration variable
		
        # Set InPort buffers
		
        # Set OutPort buffers
		
        # Set service provider to Ports
        self._middlePort.registerProvider("JARA_ARM_ManipulatorCommonInterface_Middle", "JARA_ARM::ManipulatorCommonInterface_Middle", self._JARA_ARM_ManipulatorCommonInterface_Middle)
        self._commonPort.registerProvider("JARA_ARM_ManipulatorCommonInterface_Common", "JARA_ARM::ManipulatorCommonInterface_Common", self._JARA_ARM_ManipulatorCommonInterface_Common)
		
        # Set service consumers to Ports
		
        # Set CORBA Service Ports
        self.addPort(self._middlePort)
        self.addPort(self._commonPort)
		
        return RTC.RTC_OK
	
    ###
    ## 
    ## The finalize action (on ALIVE->END transition)
    ## 
    ## @return RTC::ReturnCode_t
    #
    ## 
    #def onFinalize(self):
    #

    #    return RTC.RTC_OK
	
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
	
    ###
    ##
    ## The activated action (Active state entry action)
    ##
    ## @param ec_id target ExecutionContext Id
    ## 
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onActivated(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The deactivated action (Active state exit action)
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onDeactivated(self, ec_id):
    #
    #    return RTC.RTC_OK
	
    ###
    ##
    ## The execution action that is invoked periodically
    ##
    ## @param ec_id target ExecutionContext Id
    ##
    ## @return RTC::ReturnCode_t
    ##
    ##
    #def onExecute(self, ec_id):
    #
    #    return RTC.RTC_OK
	
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
	



def myCobot280IoInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=mycobot280io_spec)
    manager.registerFactory(profile,
                            myCobot280Io,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    myCobot280IoInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("myCobot280Io" + args)

def main():
    # remove --instance_name= option
    argv = [i for i in sys.argv if not "--instance_name=" in i]
    # Initialize manager
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    mgr.runManager()

if __name__ == "__main__":
    main()


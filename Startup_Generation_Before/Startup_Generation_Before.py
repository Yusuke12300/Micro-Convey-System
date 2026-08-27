#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

# <rtc-template block="description">
"""
 @file Startup_Generation_Before.py
 @brief ModuleDescription
 @date $Date$


"""
# </rtc-template>

import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist


# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
startup_generation_before_spec = ["implementation_id", "Startup_Generation_Before", 
         "type_name",         "Startup_Generation_Before", 
         "description",       "ModuleDescription", 
         "version",           "1.0.0", 
         "vendor",            "VenderName", 
         "category",          "Category", 
         "activity_type",     "STATIC", 
         "max_instance",      "1", 
         "language",          "Python", 
         "lang_type",         "SCRIPT",
         ""]
# </rtc-template>

# <rtc-template block="component_description">
##
# @class Startup_Generation_Before
# @brief ModuleDescription
# 
# 
# </rtc-template>
class Startup_Generation_Before(OpenRTM_aist.DataFlowComponentBase):
	
    ##
    # @brief constructor
    # @param manager Maneger Object
    # 
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_target_point = OpenRTM_aist.instantiateDataType(RTC.TimedPoint3D)
        """
        """
        self._target_pointIn = OpenRTM_aist.InPort("target_point", self._d_target_point)
        self._d_endcmd_from_Arm_Controller = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        """
        """
        self._endcmd_from_Arm_ControllerIn = OpenRTM_aist.InPort("endcmd_from_Arm_Controller", self._d_endcmd_from_Arm_Controller)
        self._d_target_pose = OpenRTM_aist.instantiateDataType(RTC.TimedPose3D)
        """
        """
        self._target_poseOut = OpenRTM_aist.OutPort("target_pose", self._d_target_pose)
        self._d_endcmd = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        """
        """
        self._endcmdOut = OpenRTM_aist.OutPort("endcmd", self._d_endcmd)


		


        # initialize of configuration-data.
        # <rtc-template block="init_conf_param">
		
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
		
        # Set InPort buffers
        self.addInPort("target_point",self._target_pointIn)
        self.addInPort("endcmd_from_Arm_Controller",self._endcmd_from_Arm_ControllerIn)
		
        # Set OutPort buffers
        self.addOutPort("target_pose",self._target_poseOut)
        self.addOutPort("endcmd",self._endcmdOut)
		
        # Set service provider to Ports
		
        # Set service consumers to Ports
		
        # Set CORBA Service Ports

        # =========================================================
        # 【ここに追記】 軌道生成ステートマシン用の独自変数を初期化
        # =========================================================
        self.state = 0           # 現在の状態 (0:待機, 1:アプローチ点, 2:下降点)
        self.target_x = 0.0      # 目標のX座標
        self.target_y = 0.0      # 目標のY座標
        self.target_z = 0.0      # 目標のZ座標
		
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

    def onExecute(self, ec_id):
        # 現在の状態（self.state）によって処理を分岐
        match self.state:
            
            # ==========================================
            # 状態0：画像データ受信待ち ＆ アプローチ点へ移動
            # ==========================================
            case 0:
                if self._target_pointIn.isNew(): # TimedPoint3Dを受信
                    data = self._target_pointIn.read()
                    
                    # 座標を保存
                    self.target_x = data.data.x
                    self.target_y = data.data.y
                    self.target_z = data.data.z + 0.085 # Zにアームの先端からハンドの高さを足す
                    print(f"ターゲット受信: X={self.target_x}, Y={self.target_y}, Z={self.target_z}")

                    # --- 型変換 ＆ 送信（アプローチ点） ---
                    self._d_target_pose.data.position.x = self.target_x
                    self._d_target_pose.data.position.y = self.target_y
                    self._d_target_pose.data.position.z = self.target_z + 0.05 # Zに安全な高さを足す
                    
                    # 姿勢はすべて0（アーム制御RTC側で自動的に真下を向くため）
                    self._d_target_pose.data.orientation.r = 0.0
                    self._d_target_pose.data.orientation.p = 0.0
                    self._d_target_pose.data.orientation.y = 0.0

                    OpenRTM_aist.setTimestamp(self._d_target_pose)
                    self._target_poseOut.write() # アーム制御RTCへTimedPose3Dを送信
                    
                    print("状態1: アプローチ点へ移動を開始します")
                    self.state = 1  # 状態1へ切り替え
            
            # ==========================================
            # 状態1：アプローチ点への完了通知待ち ＆ ターゲットへ下降
            # ==========================================
            case 1:
                if self._endcmd_from_Arm_ControllerIn.isNew(): # TimedBooleanを受信
                    complete_signal = self._endcmd_from_Arm_ControllerIn.read()
                    
                    if complete_signal.data == True:
                        # --- 送信（ターゲット点へ下がる） ---
                        self._d_target_pose.data.position.x = self.target_x
                        self._d_target_pose.data.position.y = self.target_y
                        self._d_target_pose.data.position.z = self.target_z # ハンドがターゲットに到達する高さ
                        
                        OpenRTM_aist.setTimestamp(self._d_target_pose)
                        self._target_poseOut.write() 
                        
                        print("状態2: ターゲットへの下降を開始します")
                        self.state = 2  # 状態2へ切り替え
            
            # ==========================================
            # 状態2：下降の完了通知待ち ＆ 台車用RTCへ完了通知
            # ==========================================
            case 2:
                if self._endcmd_from_Arm_ControllerIn.isNew():
                    complete_signal = self._endcmd_from_Arm_ControllerIn.read()
                    
                    if complete_signal.data == True:
                        print("ターゲットへ到達。台車用RTCへ完了通知を送ります")
                        
                        # 次のコンポーネントへアーム操作完了（TimedBoolean）を送信
                        self._d_endcmd.data = True
                        OpenRTM_aist.setTimestamp(self._d_endcmd)
                        self._endcmdOut.write()
                        
                        self.state = 0  # 全て完了したので状態0（初期状態）に戻る

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
	



def Startup_Generation_BeforeInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=startup_generation_before_spec)
    manager.registerFactory(profile,
                            Startup_Generation_Before,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Startup_Generation_BeforeInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Startup_Generation_Before" + args)

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


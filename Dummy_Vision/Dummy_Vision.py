#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

# <rtc-template block="description">
"""
 @file Dummy_Vision.py
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

# 以下の1行を手動で追加します
import threading



# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
dummy_vision_spec = ["implementation_id", "Dummy_Vision", 
         "type_name",         "Dummy_Vision", 
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
# @class Dummy_Vision
# @brief ModuleDescription
# 
# 
# </rtc-template>
class Dummy_Vision(OpenRTM_aist.DataFlowComponentBase):
	
    ##
    # @brief constructor
    # @param manager Maneger Object
    # 
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_target_point = OpenRTM_aist.instantiateDataType(RTC.TimedPoint3D)
        """
        """
        self._target_pointOut = OpenRTM_aist.OutPort("target_point", self._d_target_point)


		


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
		
        # Set OutPort buffers
        self.addOutPort("target_point",self._target_pointOut)
		
        # Set service provider to Ports
		
        # Set service consumers to Ports
		
        # Set CORBA Service Ports
		
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
    
        #return RTC.RTC_OK

    # ===============================================
    # 【追加】cmdから呼ばれる独自の送信関数
    # ===============================================
    def send_coordinates(self, x, y, z):
        self._d_target_point.data.x = x
        self._d_target_point.data.y = y
        self._d_target_point.data.z = z
        
        OpenRTM_aist.setTimestamp(self._d_target_point)
        self._target_pointOut.write()
        print(f"\n[送信完了] 座標 (X:{x}, Y:{y}, Z:{z}) を送信しました！\n")
	
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
	



def Dummy_VisionInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=dummy_vision_spec)
    manager.registerFactory(profile,
                            Dummy_Vision,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Dummy_VisionInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Dummy_Vision" + args)

def main():
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()

    # --- ここから書き換え ---
    
    # MyModuleInitで生成されたRTCインスタンスを取得する
    comp = mgr.getComponents()[0]

    # mgr.runManager() を別スレッドで動かす（通信を止めないため）[cite: 3]
    rtc_thread = threading.Thread(target=mgr.runManager, daemon=True)
    rtc_thread.start()

    print("=== ダミー画像認識RTC 起動 ===")
    print("※終了するには Ctrl+C を押してください")
    
    # メインスレッドでは cmd からの入力を無限ループで待ち受ける
    while True:
        try:
            print("-" * 30)
            # アーム制御側がメートル(m)単位のため、入力もメートルを想定
            x = float(input("目標の X座標(m) を入力: "))
            y = float(input("目標の Y座標(m) を入力: "))
            z = float(input("目標の Z座標(m) を入力: "))
            
            # 追加した送信関数を呼び出す
            comp.send_coordinates(x, y, z)
            
        except ValueError:
            print("\n※エラー: 正しい数値を入力してください！")
        except KeyboardInterrupt:
            print("\n終了します。")
            break

if __name__ == "__main__":
    main()


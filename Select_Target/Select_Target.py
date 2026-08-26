#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

# <rtc-template block="description">
"""
 @file Select_Target.py
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

#tkinterというGUIライブラリをインポート
import threading
import tkinter as tk
import sys

# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
select_target_spec = ["implementation_id", "Select_Target", 
         "type_name",         "Select_Target", 
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
# @class Select_Target
# @brief ModuleDescription
# 
# 
# </rtc-template>
class Select_Target(OpenRTM_aist.DataFlowComponentBase):
	
    ##
    # @brief constructor
    # @param manager Maneger Object
    # 
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_target_out1 = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        """
        """
        self._target_out1Out = OpenRTM_aist.OutPort("target_out1", self._d_target_out1)
        self._d_target_out2 = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        """
        """
        self._target_out2Out = OpenRTM_aist.OutPort("target_out2", self._d_target_out2)


		


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
        self.addOutPort("target_out1",self._target_out1Out)
        self.addOutPort("target_out2",self._target_out2Out)
		
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
    #
    #    return RTC.RTC_OK

    # ===============================================
    # 【追加】UIのボタンが押されたときに呼ばれる関数
    # ===============================================
    def send_target(self, target_id):
        # 1つ目のポート (target_out1) に送信
        self._d_target_out1.data = target_id
        OpenRTM_aist.setTimestamp(self._d_target_out1)
        self._target_out1Out.write()

        # 2つ目のポート (target_out2) にも同じデータを送信
        self._d_target_out2.data = target_id
        OpenRTM_aist.setTimestamp(self._d_target_out2)
        self._target_out2Out.write()

        print(f"[RTC] 2つのポートから同時に送信しました: {target_id}")
	
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
	



def Select_TargetInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=select_target_spec)
    manager.registerFactory(profile,
                            Select_Target,
                            OpenRTM_aist.Delete)

# ===============================================
# 【追加】TkinterのUIクラス
# ===============================================
class TargetSelectionUI:
    def __init__(self, rtc_instance):
        self.rtc = rtc_instance
        self.root = tk.Tk()
        self.root.title("ターゲット選択")
        self.root.geometry("300x300")

        label = tk.Label(self.root, text="ターゲットを選択してください", font=("Arial", 12))
        label.pack(pady=10)

        # 送信ボタン t1
        btn_t1 = tk.Button(self.root, text="ターゲット t1 を送信", 
                           command=lambda: self.on_button_click("t1"))
        btn_t1.pack(pady=5, fill=tk.X, padx=20)

        # 送信ボタン t2
        btn_t2 = tk.Button(self.root, text="ターゲット t2 を送信", 
                           command=lambda: self.on_button_click("t2"))
        btn_t2.pack(pady=5, fill=tk.X, padx=20)

        # 送信ボタン t3
        btn_t3 = tk.Button(self.root, text="ターゲット t3 を送信", 
                           command=lambda: self.on_button_click("t3"))
        btn_t3.pack(pady=5, fill=tk.X, padx=20)
           
        # 送信ボタン t4
        btn_t4 = tk.Button(self.root, text="ターゲット t4 を送信", 
                           command=lambda: self.on_button_click("t4"))
        btn_t4.pack(pady=5, fill=tk.X, padx=20)

        # ウィンドウを閉じたときの処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_button_click(self, target_id):
        print(f"[UI] ボタン押下: {target_id}")
        self.rtc.send_target(target_id)  # 上で作った送信関数を呼ぶ

    def on_closing(self):
        self.root.destroy()
        sys.exit() # プログラム全体を終了

    def run(self):
        self.root.mainloop()


def MyModuleInit(manager):
    Select_TargetInit(manager)

    # create instance_name option for createComponent()
    instance_name = [i for i in sys.argv if "--instance_name=" in i]
    if instance_name:
        args = instance_name[0].replace("--", "?")
    else:
        args = ""
  
    # Create a component
    comp = manager.createComponent("Select_Target" + args)

def main():
    # remove --instance_name= option
    argv = [i for i in sys.argv if not "--instance_name=" in i]
    # Initialize manager
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    #mgr.runManager()
    # --- ここから書き換え ---
    
    # MyModuleInitで生成されたRTCインスタンスを取得する
    comp = mgr.getComponents()[0]

    # mgr.runManager() を別スレッドで動かす（UIを止めないため）
    rtc_thread = threading.Thread(target=mgr.runManager, daemon=True)
    rtc_thread.start()

    # TkinterのUIを起動し、取得したRTCインスタンスを渡す
    ui = TargetSelectionUI(comp)
    ui.run()

if __name__ == "__main__":
    main()


// -*- C++ -*-
// <rtc-template block="description">
/*!
 * @file  Hand_Controller.cpp
 * @brief ModuleDescription
 *
 */
// </rtc-template>

#include "Hand_Controller.h"

#include <iostream>
#include <string>

static std::string current_target_id = "";

// Module specification
// <rtc-template block="module_spec">
#if RTM_MAJOR_VERSION >= 2
static const char* const hand_controller_spec[] =
#else
static const char* hand_controller_spec[] =
#endif
  {
    "implementation_id", "Hand_Controller",
    "type_name",         "Hand_Controller",
    "description",       "ModuleDescription",
    "version",           "1.0.0",
    "vendor",            "VenderName",
    "category",          "Controller",
    "activity_type",     "PERIODIC",
    "kind",              "DataFlowComponent",
    "max_instance",      "1",
    "language",          "C++",
    "lang_type",         "compile",
    ""
  };
// </rtc-template>

/*!
 * @brief constructor
 * @param manager Maneger Object
 */
Hand_Controller::Hand_Controller(RTC::Manager* manager)
    // <rtc-template block="initializer">
  : RTC::DataFlowComponentBase(manager),
    m_hand_startIn("hand_start", m_hand_start),
    m_target_idIn("target_id", m_target_id),
    m_hand_releaseIn("hand_release", m_hand_release),
    m_hand_endOut("hand_end", m_hand_end),
    m_middlePort("middle")
    // </rtc-template>
{
}

/*!
 * @brief destructor
 */
Hand_Controller::~Hand_Controller()
{
}



RTC::ReturnCode_t Hand_Controller::onInitialize()
{
  // Registration: InPort/OutPort/Service
  // <rtc-template block="registration">
  // Set InPort buffers
  addInPort("hand_start", m_hand_startIn);
  addInPort("target_id", m_target_idIn);
  addInPort("hand_release", m_hand_releaseIn);
  
  // Set OutPort buffer
  addOutPort("hand_end", m_hand_endOut);

  
  // Set service provider to Ports
  
  // Set service consumers to Ports
  m_middlePort.registerConsumer("JARA_ARM_ManipulatorCommonInterface_Middle", "JARA_ARM::ManipulatorCommonInterface_Middle", m_JARA_ARM_ManipulatorCommonInterface_Middle);
  
  // Set CORBA Service Ports
  addPort(m_middlePort);
  
  // </rtc-template>

  // <rtc-template block="bind_config">
  // </rtc-template>

  
  return RTC::RTC_OK;
}

/*
RTC::ReturnCode_t Hand_Controller::onFinalize()
{
  return RTC::RTC_OK;
}
*/


//RTC::ReturnCode_t Hand_Controller::onStartup(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Hand_Controller::onShutdown(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


RTC::ReturnCode_t Hand_Controller::onActivated(RTC::UniqueId /*ec_id*/)
{
  // 前回の対象物IDをクリア
  current_target_id = "";

  std::cout << "[Hand_Controller] Activated" << std::endl;

  // ==========================================
  // Activate時にグリッパを最大まで開く
  // ==========================================
  std::cout << "[Hand_Controller] Initial open gripper: 100"
            << std::endl;

  m_JARA_ARM_ManipulatorCommonInterface_Middle
    ->moveGripper(100);

  std::cout << "[Hand_Controller] Initial gripper opening completed"
            << std::endl;

  return RTC::RTC_OK;
}


RTC::ReturnCode_t Hand_Controller::onDeactivated(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Hand_Controller::onExecute(RTC::UniqueId /*ec_id*/)
{
  // ==========================================
  // 対象物IDを受信して保持
  // ==========================================
  if (m_target_idIn.isNew())
  {
    m_target_idIn.read();

    current_target_id = m_target_id.data;

    std::cout << "[Hand_Controller] target_id received: "
              << current_target_id
              << std::endl;
  }


  // ==========================================
  // 把持開始指令
  // ==========================================
  if (m_hand_startIn.isNew())
  {
    m_hand_startIn.read();

    if (m_hand_start.data == true)
    {
      std::cout << "[Hand_Controller] GRASP command received"
                << std::endl;

      int gripper_value = -1;

      // 対象物IDごとの把持開度
      if (current_target_id == "t1")
      {
        gripper_value = 67;
      }
      else if (current_target_id == "t2")
      {
        // 後で設定
      }
      else if (current_target_id == "t3")
      {
        // 後で設定
      }
      else if (current_target_id == "t4")
      {
        // 後で設定
      }


      if (gripper_value >= 0)
      {
        // ① 最大まで開く
        std::cout << "[Hand_Controller] Open gripper: 100"
                  << std::endl;

        m_JARA_ARM_ManipulatorCommonInterface_Middle
          ->moveGripper(100);


        // ② 対象物に合わせて閉じる
        std::cout << "[Hand_Controller] target_id = "
                  << current_target_id
                  << std::endl;

        std::cout << "[Hand_Controller] Close gripper: "
                  << gripper_value
                  << std::endl;

        m_JARA_ARM_ManipulatorCommonInterface_Middle
          ->moveGripper(gripper_value);


        // ③ 把持完了通知
        m_hand_end.data = true;
        m_hand_endOut.write();

        std::cout << "[Hand_Controller] GRASP completed"
                  << std::endl;

        std::cout << "[Hand_Controller] hand_end sent"
                  << std::endl;
      }
      else
      {
        std::cout << "[Hand_Controller] Unknown target_id: "
                  << current_target_id
                  << std::endl;
      }
    }
  }


  // ==========================================
  // 解放開始指令
  // ==========================================
  if (m_hand_releaseIn.isNew())
  {
    m_hand_releaseIn.read();

    if (m_hand_release.data == true)
    {
      std::cout << "[Hand_Controller] RELEASE command received"
                << std::endl;

      // 最大まで開いて対象物を離す
      std::cout << "[Hand_Controller] Open gripper: 100"
                << std::endl;

      m_JARA_ARM_ManipulatorCommonInterface_Middle
        ->moveGripper(100);


      // 解放完了通知
      m_hand_end.data = true;
      m_hand_endOut.write();

      std::cout << "[Hand_Controller] RELEASE completed"
                << std::endl;

      std::cout << "[Hand_Controller] hand_end sent"
                << std::endl;
    }
  }


  return RTC::RTC_OK;
}


//RTC::ReturnCode_t Hand_Controller::onAborting(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Hand_Controller::onError(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Hand_Controller::onReset(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Hand_Controller::onStateUpdate(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Hand_Controller::onRateChanged(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}



extern "C"
{
 
  void Hand_ControllerInit(RTC::Manager* manager)
  {
    coil::Properties profile(hand_controller_spec);
    manager->registerFactory(profile,
                             RTC::Create<Hand_Controller>,
                             RTC::Delete<Hand_Controller>);
  }
  
}

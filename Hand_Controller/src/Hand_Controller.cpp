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
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Hand_Controller::onDeactivated(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Hand_Controller::onExecute(RTC::UniqueId /*ec_id*/)
{
  // 対象物IDを受信して保持
  if (m_target_idIn.isNew())
  {
    m_target_idIn.read();

    current_target_id = m_target_id.data;

    std::cout << "[Hand_Controller] target_id received: "
              << current_target_id
              << std::endl;
  }


  // ハンド動作開始指令を受信
  if (m_hand_startIn.isNew())
  {
    m_hand_startIn.read();

    if (m_hand_start.data == true)
    {
      std::cout << "[Hand_Controller] hand_start received"
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
        // gripper_value = ○○;
      }
      else if (current_target_id == "t3")
      {
        // 後で設定
        // gripper_value = ○○;
      }
      else if (current_target_id == "t4")
      {
        // 後で設定
        // gripper_value = ○○;
      }


      // 有効なIDだった場合のみハンドを動かす
      if (gripper_value >= 0)
      {
        std::cout << "[Hand_Controller] target_id = "
                  << current_target_id
                  << std::endl;

        std::cout << "[Hand_Controller] gripper_value = "
                  << gripper_value
                  << std::endl;

        // myCobotRTCへグリッパ開度を指令
        m_JARA_ARM_ManipulatorCommonInterface_Middle
          ->moveGripper(gripper_value);

        std::cout << "[Hand_Controller] gripper completed"
                  << std::endl;

        // ハンド動作完了通知
        m_hand_end.data = true;
        m_hand_endOut.write();

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

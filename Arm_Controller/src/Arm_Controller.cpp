// -*- C++ -*-
// <rtc-template block="description">
/*!
 * @file  Arm_Controller.cpp
 * @brief ModuleDescription
 *
 */
// </rtc-template>

#include "Arm_Controller.h"
#include <iostream>

// Module specification
// <rtc-template block="module_spec">
#if RTM_MAJOR_VERSION >= 2
static const char* const arm_controller_spec[] =
#else
static const char* arm_controller_spec[] =
#endif
  {
    "implementation_id", "Arm_Controller",
    "type_name",         "Arm_Controller",
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
Arm_Controller::Arm_Controller(RTC::Manager* manager)
    // <rtc-template block="initializer">
  : RTC::DataFlowComponentBase(manager),
    m_target_pose_beforeIn("target_pose_before", m_target_pose_before),
    m_target_pose_afterIn("target_pose_after", m_target_pose_after),
    m_arm_endcmd_beforeOut("arm_endcmd_before", m_arm_endcmd_before),
    m_arm_endcmd_afterOut("arm_endcmd_after", m_arm_endcmd_after),
    m_middlePort("middle"),
    m_commonPort("common")
    // </rtc-template>
{
}

/*!
 * @brief destructor
 */
Arm_Controller::~Arm_Controller()
{
}



RTC::ReturnCode_t Arm_Controller::onInitialize()
{
  // Registration: InPort/OutPort/Service
  // <rtc-template block="registration">
  // Set InPort buffers
  addInPort("target_pose_before", m_target_pose_beforeIn);
  addInPort("target_pose_after", m_target_pose_afterIn);
  
  // Set OutPort buffer
  addOutPort("arm_endcmd_before", m_arm_endcmd_beforeOut);
  addOutPort("arm_endcmd_after", m_arm_endcmd_afterOut);

  
  // Set service provider to Ports
  
  // Set service consumers to Ports
  m_middlePort.registerConsumer("JARA_ARM_ManipulatorCommonInterface_Middle", "JARA_ARM::ManipulatorCommonInterface_Middle", m_JARA_ARM_ManipulatorCommonInterface_Middle);
  m_commonPort.registerConsumer("JARA_ARM_ManipulatorCommonInterface_Common", "JARA_ARM::ManipulatorCommonInterface_Common", m_JARA_ARM_ManipulatorCommonInterface_Common);
  
  // Set CORBA Service Ports
  addPort(m_middlePort);
  addPort(m_commonPort);
  
  // </rtc-template>

  // <rtc-template block="bind_config">
  // </rtc-template>

  
  return RTC::RTC_OK;
}

/*
RTC::ReturnCode_t Arm_Controller::onFinalize()
{
  return RTC::RTC_OK;
}
*/


//RTC::ReturnCode_t Arm_Controller::onStartup(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Arm_Controller::onShutdown(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


RTC::ReturnCode_t Arm_Controller::onActivated(RTC::UniqueId /*ec_id*/)
{
  std::cout << "[Arm_Controller] onActivated start" << std::endl;

  std::cout << "[Arm_Controller] servoON start" << std::endl;
  m_JARA_ARM_ManipulatorCommonInterface_Common->servoON();
  std::cout << "[Arm_Controller] servoON done" << std::endl;

  std::cout << "[Arm_Controller] goHome start" << std::endl;
  m_JARA_ARM_ManipulatorCommonInterface_Middle->goHome();
  std::cout << "[Arm_Controller] goHome done" << std::endl;

  return RTC::RTC_OK;
}


RTC::ReturnCode_t Arm_Controller::onDeactivated(RTC::UniqueId /*ec_id*/)
{
  std::cout << "[Arm_Controller] Deactivated" << std::endl;
  // サーボOFF
  m_JARA_ARM_ManipulatorCommonInterface_Common->servoOFF();

  return RTC::RTC_OK;
}


RTC::ReturnCode_t Arm_Controller::onExecute(RTC::UniqueId /*ec_id*/)
{
  // target_pose_before に新しい目標値が届いたか確認
  if (m_target_pose_beforeIn.isNew())
  {
    // InPortからデータを読み込む
    m_target_pose_beforeIn.read();

    // 受信した目標位置を表示
    std::cout << "[Arm_Controller] target_pose_before received" << std::endl;
    std::cout << "x = "
              << m_target_pose_before.data.position.x << std::endl;
    std::cout << "y = "
              << m_target_pose_before.data.position.y << std::endl;
    std::cout << "z = "
              << m_target_pose_before.data.position.z << std::endl;

    // myCobot用の位置姿勢データ
    JARA_ARM::CarPosWithElbow pose;

    // 姿勢は講習会サンプルと同じ固定姿勢
    pose.carPos[0][0] = -1;
    pose.carPos[0][1] = 0;
    pose.carPos[0][2] = 0;

    pose.carPos[1][0] = 0;
    pose.carPos[1][1] = 1;
    pose.carPos[1][2] = 0;

    pose.carPos[2][0] = 0;
    pose.carPos[2][1] = 0;
    pose.carPos[2][2] = -1;

    // target_pose_before の位置をmyCobotの目標位置へ設定
    pose.carPos[0][3] = m_target_pose_before.data.position.x;

    pose.carPos[1][3] = m_target_pose_before.data.position.y;

    pose.carPos[2][3] = m_target_pose_before.data.position.z;

    pose.elbow = 0;
    pose.structFlag = 0;

    std::cout << "[Arm_Controller] Move start" << std::endl;

    // 目標位置へ移動
    // 移動完了までこの関数から戻らない
    m_JARA_ARM_ManipulatorCommonInterface_Middle->moveLinearCartesianAbs(pose);

    std::cout << "[Arm_Controller] Move completed" << std::endl;

    // 軌道生成RTCへ移動完了を通知
    m_arm_endcmd_before.data = true;
    m_arm_endcmd_beforeOut.write();

    std::cout << "[Arm_Controller] arm_endcmd_before sent"
              << std::endl;
  }
  return RTC::RTC_OK;
}


//RTC::ReturnCode_t Arm_Controller::onAborting(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Arm_Controller::onError(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Arm_Controller::onReset(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Arm_Controller::onStateUpdate(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Arm_Controller::onRateChanged(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}



extern "C"
{
 
  void Arm_ControllerInit(RTC::Manager* manager)
  {
    coil::Properties profile(arm_controller_spec);
    manager->registerFactory(profile,
                             RTC::Create<Arm_Controller>,
                             RTC::Delete<Arm_Controller>);
  }
  
}

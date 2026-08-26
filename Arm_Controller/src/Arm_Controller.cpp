// -*- C++ -*-
// <rtc-template block="description">
/*!
 * @file  Arm_Controller.cpp
 * @brief ModuleDescription
 *
 */
// </rtc-template>

#include "Arm_Controller.h"

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
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Arm_Controller::onDeactivated(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Arm_Controller::onExecute(RTC::UniqueId /*ec_id*/)
{
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

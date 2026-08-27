// -*- C++ -*-
// <rtc-template block="description">
/*!
 * @file  Hand_Controller.cpp
 * @brief ModuleDescription
 *
 */
// </rtc-template>

#include "Hand_Controller.h"

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

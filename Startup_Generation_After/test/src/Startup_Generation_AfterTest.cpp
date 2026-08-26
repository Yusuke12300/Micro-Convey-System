// -*- C++ -*-
// <rtc-template block="description">
/*!
 * @file  Startup_Generation_AfterTest.cpp
 * @brief ModuleDescription (test code)
 *
 */
// </rtc-template>

#include "Startup_Generation_AfterTest.h"

// Module specification
// <rtc-template block="module_spec">
#if RTM_MAJOR_VERSION >= 2
static const char* const startup_generation_after_spec[] =
#else
static const char* startup_generation_after_spec[] =
#endif
  {
    "implementation_id", "Startup_Generation_AfterTest",
    "type_name",         "Startup_Generation_AfterTest",
    "description",       "ModuleDescription",
    "version",           "1.0.0",
    "vendor",            "Yusuke Ito",
    "category",          "Robot",
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
Startup_Generation_AfterTest::Startup_Generation_AfterTest(RTC::Manager* manager)
    // <rtc-template block="initializer">
  : RTC::DataFlowComponentBase(manager),
    m_endcmd_from_ArmControllerOut("endcmd_from_ArmController", m_endcmd_from_ArmController),
    m_endcmd_from_HandControllerOut("endcmd_from_HandController", m_endcmd_from_HandController),
    m_endcmdIn("endcmd", m_endcmd),
    m_target_poseIn("target_pose", m_target_pose)

    // </rtc-template>
{
}

/*!
 * @brief destructor
 */
Startup_Generation_AfterTest::~Startup_Generation_AfterTest()
{
}



RTC::ReturnCode_t Startup_Generation_AfterTest::onInitialize()
{
  // Registration: InPort/OutPort/Service
  // <rtc-template block="registration">
  // Set InPort buffers
  addInPort("endcmd", m_endcmdIn);
  addInPort("target_pose", m_target_poseIn);
  
  // Set OutPort buffer
  addOutPort("endcmd_from_ArmController", m_endcmd_from_ArmControllerOut);
  addOutPort("endcmd_from_HandController", m_endcmd_from_HandControllerOut);
  
  // Set service provider to Ports
  
  // Set service consumers to Ports
  
  // Set CORBA Service Ports
  
  // </rtc-template>

  // <rtc-template block="bind_config">
  // </rtc-template>
  
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Startup_Generation_AfterTest::onFinalize()
{
  return RTC::RTC_OK;
}


//RTC::ReturnCode_t Startup_Generation_AfterTest::onStartup(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Startup_Generation_AfterTest::onShutdown(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


RTC::ReturnCode_t Startup_Generation_AfterTest::onActivated(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Startup_Generation_AfterTest::onDeactivated(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Startup_Generation_AfterTest::onExecute(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


//RTC::ReturnCode_t Startup_Generation_AfterTest::onAborting(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Startup_Generation_AfterTest::onError(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Startup_Generation_AfterTest::onReset(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Startup_Generation_AfterTest::onStateUpdate(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Startup_Generation_AfterTest::onRateChanged(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


bool Startup_Generation_AfterTest::runTest()
{
    return true;
}


extern "C"
{
 
  void Startup_Generation_AfterTestInit(RTC::Manager* manager)
  {
    coil::Properties profile(startup_generation_after_spec);
    manager->registerFactory(profile,
                             RTC::Create<Startup_Generation_AfterTest>,
                             RTC::Delete<Startup_Generation_AfterTest>);
  }
  
}

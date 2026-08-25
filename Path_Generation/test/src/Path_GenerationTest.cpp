// -*- C++ -*-
// <rtc-template block="description">
/*!
 * @file  Path_GenerationTest.cpp
 * @brief Serve serve, reserve bumper (test code)
 *
 */
// </rtc-template>

#include "Path_GenerationTest.h"

// Module specification
// <rtc-template block="module_spec">
#if RTM_MAJOR_VERSION >= 2
static const char* const path_generation_spec[] =
#else
static const char* path_generation_spec[] =
#endif
  {
    "implementation_id", "Path_GenerationTest",
    "type_name",         "Path_GenerationTest",
    "description",       "Serve serve, reserve bumper",
    "version",           "1.0.0",
    "vendor",            "YusukeIto",
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
Path_GenerationTest::Path_GenerationTest(RTC::Manager* manager)
    // <rtc-template block="initializer">
  : RTC::DataFlowComponentBase(manager),
    m_bumperOut("bumper", m_bumper),
    m_completeOut("complete", m_complete),
    m_targetVelocityIn("targetVelocity", m_targetVelocity)

    // </rtc-template>
{
}

/*!
 * @brief destructor
 */
Path_GenerationTest::~Path_GenerationTest()
{
}



RTC::ReturnCode_t Path_GenerationTest::onInitialize()
{
  // Registration: InPort/OutPort/Service
  // <rtc-template block="registration">
  // Set InPort buffers
  addInPort("targetVelocity", m_targetVelocityIn);
  
  // Set OutPort buffer
  addOutPort("bumper", m_bumperOut);
  addOutPort("complete", m_completeOut);
  
  // Set service provider to Ports
  
  // Set service consumers to Ports
  
  // Set CORBA Service Ports
  
  // </rtc-template>

  // <rtc-template block="bind_config">
  // </rtc-template>
  
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Path_GenerationTest::onFinalize()
{
  return RTC::RTC_OK;
}


//RTC::ReturnCode_t Path_GenerationTest::onStartup(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Path_GenerationTest::onShutdown(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


RTC::ReturnCode_t Path_GenerationTest::onActivated(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Path_GenerationTest::onDeactivated(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Path_GenerationTest::onExecute(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


//RTC::ReturnCode_t Path_GenerationTest::onAborting(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Path_GenerationTest::onError(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Path_GenerationTest::onReset(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Path_GenerationTest::onStateUpdate(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Path_GenerationTest::onRateChanged(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


bool Path_GenerationTest::runTest()
{
    return true;
}


extern "C"
{
 
  void Path_GenerationTestInit(RTC::Manager* manager)
  {
    coil::Properties profile(path_generation_spec);
    manager->registerFactory(profile,
                             RTC::Create<Path_GenerationTest>,
                             RTC::Delete<Path_GenerationTest>);
  }
  
}

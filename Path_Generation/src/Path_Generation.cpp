// -*- C++ -*-
// <rtc-template block="description">
/*!
 * @file  Path_Generation.cpp
 * @brief Serve serve, reserve bumper
 *
 */
// </rtc-template>

#include "Path_Generation.h"

// Module specification
// <rtc-template block="module_spec">
#if RTM_MAJOR_VERSION >= 2
static const char* const path_generation_spec[] =
#else
static const char* path_generation_spec[] =
#endif
  {
    "implementation_id", "Path_Generation",
    "type_name",         "Path_Generation",
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
Path_Generation::Path_Generation(RTC::Manager* manager)
    // <rtc-template block="initializer">
  : RTC::DataFlowComponentBase(manager),
    m_bumperIn("bumper", m_bumper),
    m_completeIn("complete", m_complete),
    m_targetVelocityOut("targetVelocity", m_targetVelocity)
    // </rtc-template>
{
}

/*!
 * @brief destructor
 */
Path_Generation::~Path_Generation()
{
}



RTC::ReturnCode_t Path_Generation::onInitialize()
{
  // Registration: InPort/OutPort/Service
  // <rtc-template block="registration">
  // Set InPort buffers
  addInPort("bumper", m_bumperIn);
  addInPort("complete", m_completeIn);
  
  // Set OutPort buffer
  addOutPort("targetVelocity", m_targetVelocityOut);

  
  // Set service provider to Ports
  
  // Set service consumers to Ports
  
  // Set CORBA Service Ports
  
  // </rtc-template>

  // <rtc-template block="bind_config">
  // </rtc-template>

  
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Path_Generation::onFinalize()
{
  return RTC::RTC_OK;
}


//RTC::ReturnCode_t Path_Generation::onStartup(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Path_Generation::onShutdown(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


RTC::ReturnCode_t Path_Generation::onActivated(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Path_Generation::onDeactivated(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Path_Generation::onExecute(RTC::UniqueId /*ec_id*/)
{
    if (m_bumperIn.isNew()) {
        m_bumperIn.read();

        if (m_bumper.data[1] == true) {
             m_targetVelocity.data.vx = 0.0;
             m_targetVelocity.data.vy = 0.0;
             m_targetVelocity.data.va = 0.0;
        }
        else {
            m_targetVelocity.data.vx = 0.2;
            m_targetVelocity.data.vy = 0.0;
            m_targetVelocity.data.va = 0.0;
        }

        m_targetVelocityOut.write();
    }


  return RTC::RTC_OK;
}


//RTC::ReturnCode_t Path_Generation::onAborting(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Path_Generation::onError(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Path_Generation::onReset(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Path_Generation::onStateUpdate(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Path_Generation::onRateChanged(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}



extern "C"
{
 
  void Path_GenerationInit(RTC::Manager* manager)
  {
    coil::Properties profile(path_generation_spec);
    manager->registerFactory(profile,
                             RTC::Create<Path_Generation>,
                             RTC::Delete<Path_Generation>);
  }
  
}

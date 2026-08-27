// -*- C++ -*-
// <rtc-template block="description">
/*!
 * @file  Path_Generation.cpp
 * @brief Serve serve, reserve bumper
 *
 */
// </rtc-template>

#include "Path_Generation.h"
#include<iostream>

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
    m_targetVelocityOut("targetVelocity", m_targetVelocity),
    m_currentPoseIn("currentPose", m_currentPose)
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
  addInPort("currentPose", m_currentPoseIn);
  
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
    m_step = 0;
    std::cout << "Activeになりました" << std::endl;

  return RTC::RTC_OK;
}


RTC::ReturnCode_t Path_Generation::onDeactivated(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Path_Generation::onExecute(RTC::UniqueId /*ec_id*/)
{
    

    switch (m_step) {
    case 0:
        if (m_completeIn.isNew()) {
            m_completeIn.read();
            std::cout << "完了通知取得" << std::endl;
            if (m_complete.data == true) {
                m_step = 3;
                std::cout << "Kobuki始動" << std::endl;
            }
        }
        break;

    case 1:
        if (m_bumperIn.isNew()) {
            m_bumperIn.read();
            std::cout << "Kobuki始動2" << std::endl;
            if(m_bumper.data[0] == true || m_bumper.data[1] == true || m_bumper.data[2] == true){
                m_targetVelocity.data.vx = 0.0;
                m_targetVelocity.data.vy = 0.0;
                m_targetVelocity.data.va = 0.0;

                m_step = 2;
                std::cout <<"衝突検知" << std::endl;
            }
            else {
                m_targetVelocity.data.vx = 0.2;
                m_targetVelocity.data.vy = 0.0;
                m_targetVelocity.data.va = 0.0;
            }
        m_targetVelocityOut.write();
        }
        break;

    case 2:
        break;


    case 3:
        while (m_currentPoseIn.isNew()) {
            m_currentPoseIn.read();
        }

        // 読み終わった最新のデータだけを画面に出す
        std::cout << m_currentPose.data.position.x << "," << m_currentPose.data.position.y << std::endl;

        if (m_currentPose.data.position.x <= 0.95) {
            m_targetVelocity.data.vx = 0.2;
            m_targetVelocity.data.vy = 0.0;
            m_targetVelocity.data.va = 0.0;
        }
        else {
            m_targetVelocity.data.vx = 0.0;
            m_targetVelocity.data.vy = 0.0;
            m_targetVelocity.data.va = 0.0;
            std::cout << "停止します" << std::endl;
            m_step = 2;
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

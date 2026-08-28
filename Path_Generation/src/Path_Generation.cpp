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
#include<chrono>

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
    m_step = 1;
    std::cout << "Activeになりました" << std::endl;

    target_position_x = 1.9;
    target_position_y = -0.7;

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
                m_step = 1;
                std::cout << "Kobuki始動" << std::endl;
            }
        }
        break;
        
    case 1:
        while (m_currentPoseIn.isNew()) {
            m_currentPoseIn.read();
        }

        // 読み終わった最新のデータだけを画面に出す
        std::cout << m_currentPose.data.position.x << "," << m_currentPose.data.position.y << std::endl;

        //目標y座標へ移動
        if (m_currentPose.data.position.x <= 1.9) {
            m_targetVelocity.data.vx = 0.2;
            m_targetVelocity.data.vy = 0.0;
            m_targetVelocity.data.va = 0.0;

            if (m_bumperIn.isNew()) {
                m_bumperIn.read();
                if (m_bumper.data[0] == true || m_bumper.data[1] == true || m_bumper.data[2] == true) {
                    m_step = 3;

                    // 回避開始の時間を記録
                    m_start_time = std::chrono::system_clock::now();
                }
            }
        }
        else {
            m_step = 9;
            m_start_time = std::chrono::system_clock::now();
          
        }
        m_targetVelocityOut.write();

        break;

    case 2:
        while (m_currentPoseIn.isNew()) {
            m_currentPoseIn.read();
        }

        // 読み終わった最新のデータだけを画面に出す
        std::cout << m_currentPose.data.position.x << "," << m_currentPose.data.position.y << std::endl;


       
        //目標のx座標へ移動
        if (m_currentPose.data.position.y >= -0.7) {
            m_targetVelocity.data.vx = 0.2;
            m_targetVelocity.data.vy = 0.0;
            m_targetVelocity.data.va = 0.0;

            if (m_bumperIn.isNew()) {
                m_bumperIn.read();
                if (m_bumper.data[0] == true || m_bumper.data[1] == true || m_bumper.data[2] == true) {
                    m_step = 3;

                    // 回避開始の時間を記録
                    m_start_time = std::chrono::system_clock::now();
                }
            }
        }
        else {
            m_step = 7;
        }
        m_targetVelocityOut.write();
        break;


    case 3: // バック（仮に2秒間）
        m_targetVelocity.data.vx = -0.2;
        m_targetVelocity.data.vy = 0.0;
        m_targetVelocity.data.va = 0.0;
        m_targetVelocityOut.write();

        // 2000ミリ秒(2秒)経過したら次の動作へ
        if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now() - m_start_time).count() > 2000) {
            m_step = 4;
            m_start_time = std::chrono::system_clock::now(); // 時間リセット
        }
        break;

    case 4: // 回転（仮に2秒間）
        m_targetVelocity.data.vx = 0.0;
        m_targetVelocity.data.vy = 0.0;
        m_targetVelocity.data.va = 0.4;
        m_targetVelocityOut.write();

        if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now() - m_start_time).count() > 3400) {
            m_step = 5;
            m_start_time = std::chrono::system_clock::now();
        }
        break;

    case 5: // 前進（仮に2秒間）
        m_targetVelocity.data.vx = 0.2;
        m_targetVelocity.data.vy = 0.0;
        m_targetVelocity.data.va = 0.0;
        m_targetVelocityOut.write();

        if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now() - m_start_time).count() > 3000) {
            m_step = 6;
            m_start_time = std::chrono::system_clock::now();
        }
        break;

    case 6: // 逆回転（仮に2秒間）
        m_targetVelocity.data.vx = 0.0;
        m_targetVelocity.data.vy = 0.0;
        m_targetVelocity.data.va = -0.4;
        m_targetVelocityOut.write();

        if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now() - m_start_time).count() > 3400) {
            m_step = 1; // 通常の前進に戻る
        }
        break;


    case 7:
        m_targetVelocity.data.vx = 0.0;
        m_targetVelocity.data.vy = 0.0;
        m_targetVelocity.data.va = 0.0;
        std::cout << "停止します" << std::endl;
        m_step = 8;
        m_targetVelocityOut.write();
        break;

    case 8:
        break;

    case 9:
        //回転
        m_targetVelocity.data.vx = 0.0;
        m_targetVelocity.data.vy = 0.0;
        m_targetVelocity.data.va = -0.4; 
        m_targetVelocityOut.write();


        if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now() - m_start_time).count() > 3500) {
            m_step = 2;
        }
        break;



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

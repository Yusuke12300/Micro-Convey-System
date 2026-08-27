// -*- C++ -*-
// <rtc-template block="description">
/*!
 * @file  Startup_Generation_After.cpp
 * @brief ModuleDescription
 *
 */
// </rtc-template>

#include "Startup_Generation_After.h"
#include<iostream>

// Module specification
// <rtc-template block="module_spec">
#if RTM_MAJOR_VERSION >= 2
static const char* const startup_generation_after_spec[] =
#else
static const char* startup_generation_after_spec[] =
#endif
  {
    "implementation_id", "Startup_Generation_After",
    "type_name",         "Startup_Generation_After",
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
Startup_Generation_After::Startup_Generation_After(RTC::Manager* manager)
    // <rtc-template block="initializer">
  : RTC::DataFlowComponentBase(manager),
    m_endcmd_from_ArmControllerIn("endcmd_from_ArmController", m_endcmd_from_ArmController),
    m_endcmd_from_HandControllerIn("endcmd_from_HandController", m_endcmd_from_HandController),
    m_endcmdOut("endcmd", m_endcmd),
    m_target_poseOut("target_pose", m_target_pose),
    m_endcmd_to_HandControllerOut("endcmd_to_HandController", m_endcmd_to_HandController)
    // </rtc-template>
{
}

/*!
 * @brief destructor
 */
Startup_Generation_After::~Startup_Generation_After()
{
}



RTC::ReturnCode_t Startup_Generation_After::onInitialize()
{
  // Registration: InPort/OutPort/Service
  // <rtc-template block="registration">
  // Set InPort buffers
  addInPort("endcmd_from_ArmController", m_endcmd_from_ArmControllerIn);
  addInPort("endcmd_from_HandController", m_endcmd_from_HandControllerIn);
  
  // Set OutPort buffer
  addOutPort("endcmd", m_endcmdOut);
  addOutPort("target_pose", m_target_poseOut);
  addOutPort("endcmd_to_HandController", m_endcmd_to_HandControllerOut);

  
  // Set service provider to Ports
  
  // Set service consumers to Ports
  
  // Set CORBA Service Ports
  
  // </rtc-template>

  // <rtc-template block="bind_config">
  // </rtc-template>

  
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Startup_Generation_After::onFinalize()
{
  return RTC::RTC_OK;
}


//RTC::ReturnCode_t Startup_Generation_After::onStartup(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Startup_Generation_After::onShutdown(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


RTC::ReturnCode_t Startup_Generation_After::onActivated(RTC::UniqueId /*ec_id*/)
{
    m_step = 0;
    m_endcmd.data = false;
    m_endcmd_to_HandController.data = false;

    m_target_list.clear();

    RTC::Pose3D pose1;
    pose1.position.x = -0.2;
    pose1.position.y = 0.0;
    pose1.position.z = 0.2;

    pose1.orientation.r = 0.0;
    pose1.orientation.p = 0.0;
    pose1.orientation.y = 0.0;
    m_target_list.push_back(pose1);

    RTC::Pose3D pose2;
    pose2.position.x = 0.0;
    pose2.position.y = -0.2;
    pose2.position.z = 0.2;

    pose2.orientation.r = 0.0;
    pose2.orientation.p = 0.0;
    pose2.orientation.y = 0.0;
    m_target_list.push_back(pose2);

    RTC::Pose3D pose3;
    pose3.position.x = 0.2;
    pose3.position.y = 0.0;
    pose3.position.z = 0.24;

    pose3.orientation.r = 0.0;
    pose3.orientation.p = 0.0;
    pose3.orientation.y = 0.0;
    m_target_list.push_back(pose3);

    return RTC::RTC_OK;
}


RTC::ReturnCode_t Startup_Generation_After::onDeactivated(RTC::UniqueId /*ec_id*/)
{
  return RTC::RTC_OK;
}


RTC::ReturnCode_t Startup_Generation_After::onExecute(RTC::UniqueId /*ec_id*/)
{
    switch (m_step) {
    case 0://初期状態（ハンドコンポーネントからの完了信号待ち）
        if (m_endcmd_from_HandControllerIn.isNew()) {
            m_endcmd_from_HandControllerIn.read();

            if (m_endcmd_from_HandController.data == true) {
                m_target_pose.data = m_target_list[0];
                setTimestamp(m_target_pose); // 現在時刻を付与
                m_target_poseOut.write();

                m_step = 1;
                std::cout << "ハンドコンポーネントからの把持完了通知を取得" << std::endl;
                std::cout << "第一座標を送信" << std::endl;
            }
        }
        break;

    case 1://アームコンポーネントからの1回目の完了信号待ち

        if (m_endcmd_from_ArmControllerIn.isNew()) {
            m_endcmd_from_ArmControllerIn.read();

            if (m_endcmd_from_ArmController.data == true) {
                m_target_pose.data = m_target_list[1]; 
                setTimestamp(m_target_pose); // 現在時刻を付与
                m_target_poseOut.write();

                m_step = 2;
                std::cout << "第二座標を送信" << std::endl;
            }
        }
        break;

    case 2://アームコンポーネントからの2回目の完了信号待ち

        if (m_endcmd_from_ArmControllerIn.isNew()) {
            m_endcmd_from_ArmControllerIn.read();

            if (m_endcmd_from_ArmController.data == true) {
                m_target_pose.data = m_target_list[2];
                setTimestamp(m_target_pose); // 現在時刻を付与
                m_target_poseOut.write();

                m_step = 3;
                std::cout << "第三座標を送信" << std::endl;
            }
        }
        break;


    case 3://アームコンポーネントからの2回目の完了信号待ち

        if (m_endcmd_from_ArmControllerIn.isNew()) {
            m_endcmd_from_ArmControllerIn.read();

            if (m_endcmd_from_ArmController.data == true) {
                std::cout << "アームコンポーネントからの完了通知を受信" << std::endl;
                m_endcmd_to_HandController.data = true;
                setTimestamp(m_endcmd_to_HandController);
                m_endcmd_to_HandControllerOut.write();

                m_step = 4;
            }
        }
        break;

    case 4:
        if (m_endcmd_from_HandControllerIn.isNew()) {
            m_endcmd_from_HandControllerIn.read();

            if (m_endcmd_from_HandController.data == true) {
                std::cout << "ハンドコンポーネントからの開放完了通知を受信" << std::endl;

                m_endcmd.data = true;
                setTimestamp(m_endcmd); // 完了通知にも現在時刻を付与
                m_endcmdOut.write();

                m_step = 5; 
                std::cout << "動作完了" << std::endl;
            }
        }
        break;

    case 5:
        break;
    }





    return RTC::RTC_OK;
}


//RTC::ReturnCode_t Startup_Generation_After::onAborting(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Startup_Generation_After::onError(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Startup_Generation_After::onReset(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Startup_Generation_After::onStateUpdate(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}


//RTC::ReturnCode_t Startup_Generation_After::onRateChanged(RTC::UniqueId /*ec_id*/)
//{
//  return RTC::RTC_OK;
//}



extern "C"
{
 
  void Startup_Generation_AfterInit(RTC::Manager* manager)
  {
    coil::Properties profile(startup_generation_after_spec);
    manager->registerFactory(profile,
                             RTC::Create<Startup_Generation_After>,
                             RTC::Delete<Startup_Generation_After>);
  }
  
}

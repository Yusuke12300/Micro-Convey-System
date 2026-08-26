// -*- C++ -*-
// <rtc-template block="description">
/*!
 * @file  Path_Generation.h
 * @brief Serve serve, reserve bumper
 *
 */
// </rtc-template>

#ifndef PATH_GENERATION_H
#define PATH_GENERATION_H

#include <rtm/idl/BasicDataTypeSkel.h>
#include <rtm/idl/ExtendedDataTypesSkel.h>
#include <rtm/idl/InterfaceDataTypesSkel.h>

// Service implementation headers
// <rtc-template block="service_impl_h">

// </rtc-template>

// Service Consumer stub headers
// <rtc-template block="consumer_stub_h">
#include "BasicDataTypeStub.h"
#include "ExtendedDataTypesStub.h"

// </rtc-template>

#include <rtm/Manager.h>
#include <rtm/DataFlowComponentBase.h>
#include <rtm/CorbaPort.h>
#include <rtm/DataInPort.h>
#include <rtm/DataOutPort.h>


// <rtc-template block="component_description">
/*!
 * @class Path_Generation
 * @brief Serve serve, reserve bumper
 *
 */
// </rtc-template>
class Path_Generation
  : public RTC::DataFlowComponentBase
{
 public:
  /*!
   * @brief constructor
   * @param manager Maneger Object
   */
  Path_Generation(RTC::Manager* manager);

  /*!
   * @brief destructor
   */
  ~Path_Generation() override;

  // <rtc-template block="public_attribute">
  
  // </rtc-template>

  // <rtc-template block="public_operation">
  
  // </rtc-template>

  // <rtc-template block="activity">
  /***
   *
   * The initialize action (on CREATED->ALIVE transition)
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
   RTC::ReturnCode_t onInitialize() override;

  /***
   *
   * The finalize action (on ALIVE->END transition)
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
   RTC::ReturnCode_t onFinalize() override;

  /***
   *
   * The startup action when ExecutionContext startup
   *
   * @param ec_id target ExecutionContext Id
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
  // RTC::ReturnCode_t onStartup(RTC::UniqueId ec_id) override;

  /***
   *
   * The shutdown action when ExecutionContext stop
   *
   * @param ec_id target ExecutionContext Id
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
  // RTC::ReturnCode_t onShutdown(RTC::UniqueId ec_id) override;

  /***
   *
   * The activated action (Active state entry action)
   *
   * @param ec_id target ExecutionContext Id
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
   RTC::ReturnCode_t onActivated(RTC::UniqueId ec_id) override;

  /***
   *
   * The deactivated action (Active state exit action)
   *
   * @param ec_id target ExecutionContext Id
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
   RTC::ReturnCode_t onDeactivated(RTC::UniqueId ec_id) override;

  /***
   *
   * The execution action that is invoked periodically
   *
   * @param ec_id target ExecutionContext Id
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
   RTC::ReturnCode_t onExecute(RTC::UniqueId ec_id) override;

  /***
   *
   * The aborting action when main logic error occurred.
   *
   * @param ec_id target ExecutionContext Id
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
  // RTC::ReturnCode_t onAborting(RTC::UniqueId ec_id) override;

  /***
   *
   * The error action in ERROR state
   *
   * @param ec_id target ExecutionContext Id
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
  // RTC::ReturnCode_t onError(RTC::UniqueId ec_id) override;

  /***
   *
   * The reset action that is invoked resetting
   *
   * @param ec_id target ExecutionContext Id
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
  // RTC::ReturnCode_t onReset(RTC::UniqueId ec_id) override;
  
  /***
   *
   * The state update action that is invoked after onExecute() action
   *
   * @param ec_id target ExecutionContext Id
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
  // RTC::ReturnCode_t onStateUpdate(RTC::UniqueId ec_id) override;

  /***
   *
   * The action that is invoked when execution context's rate is changed
   *
   * @param ec_id target ExecutionContext Id
   *
   * @return RTC::ReturnCode_t
   * 
   * 
   */
  // RTC::ReturnCode_t onRateChanged(RTC::UniqueId ec_id) override;
  // </rtc-template>


 protected:
  // <rtc-template block="protected_attribute">
  
  // </rtc-template>

  // <rtc-template block="protected_operation">
  
  // </rtc-template>

  // Configuration variable declaration
  // <rtc-template block="config_declare">

  // </rtc-template>

  // DataInPort declaration
  // <rtc-template block="inport_declare">
  RTC::TimedBooleanSeq m_bumper;
  /*!
   * センサ情報　true:障害物検出（バンパ接触、車輪落下、崖検知）　
   * false:障害物無し
   * - Type: RTC::TimedBooleanSeq
   * - Semantics: 0	RIGHT_BUMPER	右バンパ
   *              1	CENTER_BUMPER	中央バンパ
   *              2	LEFT_BUMPER	左バンパ
   *              3	RIGHT_WHEEL_DROP	右車輪脱輪
   *              4	LEFT_WHEEL_DROP	左車輪脱輪
   *              5	RIGHT_CLIFF	右崖センサ
   *              6	CENTER_CLIFF	中央崖センサ
   *              7	LEFT_CLIFF	左崖センサ
   *              8	RIGHT_IRFAR_RIGHT	右IR/ドック右遠
   *              9	RIGHT_IRFAR_CENTER	右IR/ドック中央遠
   *              10	RIGHT_IRFAR_LEFT	右IR/ドック左遠
   *              11	RIGHT_IRNEAR_RIGHT	右IR/ドック右近
   *              12	RIGHT_IRNEAR_CENTER	右IR/ドック中央近
   *              13	RIGHT_IRNEAR_LEFT	右IR/ドック左近
   *              14	CENTER_IRFAR_RIGHT	中央IR/ドック右遠
   *              15	CENTER_IRFAR_CENTER	中央IR/ドック中央遠
   *              16	CENTER_IRFAR_LEFT	中央IR/ドック左遠
   *              17	CENTER_IRNEAR_RIGHT	中央IR/ドック右近
   *              18	CENTER_IRNEAR_CENTER	中央IR/ドック中央近
   *              19	CENTER_IRNEAR_LEFT	中央IR/ドック左近
   *              20	LEFT_IRFAR_RIGHT	左IR/ドック右遠
   *              21	LEFT_IRFAR_CENTER	左IR/ドック中央遠
   *              22	LEFT_IRFAR_LEFT	左IR/ドック左遠
   *              23	LEFT_IRNEAR_RIGHT	左IR/ドック右近
   *              24	LEFT_IRNEAR_CENTER	左IR/ドック中央近
   *              25	LEFT_IRNEAR_LEFT	左IR/ドック左近
   *              26	KOBUKI_DOCKED	ドック完了
   */
  RTC::InPort<RTC::TimedBooleanSeq> m_bumperIn;
  RTC::TimedBoolean m_complete;
  /*!
   * 完了通知
   * - Type: RTC::TimedBoolean
   * - Semantics: True or False
   */
  RTC::InPort<RTC::TimedBoolean> m_completeIn;
  
  // </rtc-template>


  // DataOutPort declaration
  // <rtc-template block="outport_declare">
  RTC::TimedVelocity2D m_targetVelocity;
  /*!
   * 移動ロボットの速度ベクトル
   * - Type: RTC::TimedVelocity2D
   * - Semantics: vx: 並進速度、vy: 0.0、va: 角速度
   * - Unit: vx [m/s]、va [rad/s]
   */
  RTC::OutPort<RTC::TimedVelocity2D> m_targetVelocityOut;
  
  // </rtc-template>

  // CORBA Port declaration
  // <rtc-template block="corbaport_declare">
  
  // </rtc-template>

  // Service declaration
  // <rtc-template block="service_declare">
  
  // </rtc-template>

  // Consumer declaration
  // <rtc-template block="consumer_declare">
  
  // </rtc-template>


 private:
  // <rtc-template block="private_attribute">
  
  // </rtc-template>

  // <rtc-template block="private_operation">
  
  // </rtc-template>
	 int m_step;

};


extern "C"
{
  DLL_EXPORT void Path_GenerationInit(RTC::Manager* manager);
};

#endif // PATH_GENERATION_H

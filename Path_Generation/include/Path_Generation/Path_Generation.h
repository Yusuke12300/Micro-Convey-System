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

#include <chrono>

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
	RTC::InPort<RTC::TimedBooleanSeq> m_bumperIn;

	RTC::TimedBoolean m_complete;
	RTC::InPort<RTC::TimedBoolean> m_completeIn;

	// </rtc-template>


	// DataOutPort declaration
	// <rtc-template block="outport_declare">
	RTC::TimedVelocity2D m_targetVelocity;
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

	RTC::TimedPose2D m_currentPose;
	RTC::InPort<RTC::TimedPose2D> m_currentPoseIn;


private:
	// <rtc-template block="private_attribute">

	// </rtc-template>

	// <rtc-template block="private_operation">

	// </rtc-template>
	int m_step;
	std::chrono::system_clock::time_point m_start_time; // 開始時刻を記録する変数
	double target_position_x;
	double target_position_y;

};


extern "C"
{
	DLL_EXPORT void Path_GenerationInit(RTC::Manager* manager);
};

#endif // PATH_GENERATION_H
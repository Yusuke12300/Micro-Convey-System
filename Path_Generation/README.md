# Path_Generation

## Overview

Serve serve, reserve bumper

## Description



### Input and Output



### Algorithm etc



### Basic Information

|  |  |
----|---- 
| Module Name | Path_Generation |
| Description | Serve serve, reserve bumper |
| Version | 1.0.0 |
| Vendor | YusukeIto |
| Category | Robot |
| Comp. Type | STATIC |
| Act. Type | PERIODIC |
| Kind | DataFlowComponent |
| MAX Inst. | 1 |

### Activity definition

<table>
  <tr>
    <td rowspan="4">on_initialize</td>
    <td colspan="2">implemented</td>
    <tr>
      <td>Description</td>
      <td></td>
    </tr>
    <tr>
      <td>PreCondition</td>
      <td></td>
    </tr>
    <tr>
      <td>PostCondition</td>
      <td></td>
    </tr>
  </tr>
  <tr>
    <td rowspan="4">on_finalize</td>
    <td colspan="2">implemented</td>
    <tr>
      <td>Description</td>
      <td></td>
    </tr>
    <tr>
      <td>PreCondition</td>
      <td></td>
    </tr>
    <tr>
      <td>PostCondition</td>
      <td></td>
    </tr>
  </tr>
  <tr>
    <td>on_startup</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>on_shutdown</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td rowspan="4">on_activated</td>
    <td colspan="2">implemented</td>
    <tr>
      <td>Description</td>
      <td></td>
    </tr>
    <tr>
      <td>PreCondition</td>
      <td></td>
    </tr>
    <tr>
      <td>PostCondition</td>
      <td></td>
    </tr>
  </tr>
  <tr>
    <td rowspan="4">on_deactivated</td>
    <td colspan="2">implemented</td>
    <tr>
      <td>Description</td>
      <td></td>
    </tr>
    <tr>
      <td>PreCondition</td>
      <td></td>
    </tr>
    <tr>
      <td>PostCondition</td>
      <td></td>
    </tr>
  </tr>
  <tr>
    <td rowspan="4">on_execute</td>
    <td colspan="2">implemented</td>
    <tr>
      <td>Description</td>
      <td></td>
    </tr>
    <tr>
      <td>PreCondition</td>
      <td></td>
    </tr>
    <tr>
      <td>PostCondition</td>
      <td></td>
    </tr>
  </tr>
  <tr>
    <td>on_aborting</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>on_error</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>on_reset</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>on_state_update</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>on_rate_changed</td>
    <td colspan="2"></td>
  </tr>
</table>

### InPorts definition

#### bumper

センサ情報　true:障害物検出（バンパ接触、車輪落下、崖検知）　false:障害物無し

<table>
  <tr>
    <td>DataType</td>
    <td>RTC::TimedBooleanSeq</td>
    <td>RTC::TimedBooleanSeq</td>
  </tr>
  <tr>
    <td>IDL file</td>
    <td colspan="2">BasicDataType.idl</td>
  </tr>
  <tr>
    <td>Number of Data</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Semantics</td>
    <td colspan="2">0	RIGHT_BUMPER	右バンパ<br/>1	CENTER_BUMPER	中央バンパ<br/>2	LEFT_BUMPER	左バンパ<br/>3	RIGHT_WHEEL_DROP	右車輪脱輪<br/>4	LEFT_WHEEL_DROP	左車輪脱輪<br/>5	RIGHT_CLIFF	右崖センサ<br/>6	CENTER_CLIFF	中央崖センサ<br/>7	LEFT_CLIFF	左崖センサ<br/>8	RIGHT_IRFAR_RIGHT	右IR/ドック右遠<br/>9	RIGHT_IRFAR_CENTER	右IR/ドック中央遠<br/>10	RIGHT_IRFAR_LEFT	右IR/ドック左遠<br/>11	RIGHT_IRNEAR_RIGHT	右IR/ドック右近<br/>12	RIGHT_IRNEAR_CENTER	右IR/ドック中央近<br/>13	RIGHT_IRNEAR_LEFT	右IR/ドック左近<br/>14	CENTER_IRFAR_RIGHT	中央IR/ドック右遠<br/>15	CENTER_IRFAR_CENTER	中央IR/ドック中央遠<br/>16	CENTER_IRFAR_LEFT	中央IR/ドック左遠<br/>17	CENTER_IRNEAR_RIGHT	中央IR/ドック右近<br/>18	CENTER_IRNEAR_CENTER	中央IR/ドック中央近<br/>19	CENTER_IRNEAR_LEFT	中央IR/ドック左近<br/>20	LEFT_IRFAR_RIGHT	左IR/ドック右遠<br/>21	LEFT_IRFAR_CENTER	左IR/ドック中央遠<br/>22	LEFT_IRFAR_LEFT	左IR/ドック左遠<br/>23	LEFT_IRNEAR_RIGHT	左IR/ドック右近<br/>24	LEFT_IRNEAR_CENTER	左IR/ドック中央近<br/>25	LEFT_IRNEAR_LEFT	左IR/ドック左近<br/>26	KOBUKI_DOCKED	ドック完了</td>
  </tr>
  <tr>
    <td>Unit</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Occirrence frecency Period</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Operational frecency Period</td>
    <td colspan="2"></td>
  </tr>
</table>

#### complete

完了通知

<table>
  <tr>
    <td>DataType</td>
    <td>RTC::TimedBoolean</td>
    <td>RTC::TimedBoolean</td>
  </tr>
  <tr>
    <td>IDL file</td>
    <td colspan="2">BasicDataType.idl</td>
  </tr>
  <tr>
    <td>Number of Data</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Semantics</td>
    <td colspan="2">True or False</td>
  </tr>
  <tr>
    <td>Unit</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Occirrence frecency Period</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Operational frecency Period</td>
    <td colspan="2"></td>
  </tr>
</table>


### OutPorts definition

#### targetVelocity

移動ロボットの速度ベクトル

<table>
  <tr>
    <td>DataType</td>
    <td>RTC::TimedVelocity2D</td>
    <td>RTC::TimedVelocity2D</td>
  </tr>
  <tr>
    <td>IDL file</td>
    <td colspan="2">ExtendedDataTypes.idl</td>
  </tr>
  <tr>
    <td>Number of Data</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Semantics</td>
    <td colspan="2">vx: 並進速度、vy: 0.0、va: 角速度</td>
  </tr>
  <tr>
    <td>Unit</td>
    <td colspan="2">vx [m/s]、va [rad/s]</td>
  </tr>
  <tr>
    <td>Occirrence frecency Period</td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td>Operational frecency Period</td>
    <td colspan="2"></td>
  </tr>
</table>


### Service Port definition


### Configuration definition


## Demo

## Requirement

## Setup

### Windows

### Ubuntu

## Usage

## Running the tests

## LICENCE




## References




## Author



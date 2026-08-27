@echo off
chcp 65001
echo ==========================================
echo Micro-Convey-System ポート接続スクリプト
echo ==========================================

set NS=localhost

echo 各コンポーネントのポートを接続しています...

REM [16, 1] Startup_Before(Out) -> Arm_Controller(In)
rtcon /%NS%/Startup_Generation_Before0.rtc:target_pose /%NS%/Arm_Controller0.rtc:target_pose_before

REM [21, 2] Startup_After(Out) -> Arm_Controller(In)
rtcon /%NS%/Startup_Generation_After0.rtc:target_pose /%NS%/Arm_Controller0.rtc:target_pose_after

REM [3, 15] Arm_Controller(Out) -> Startup_Before(In)
rtcon /%NS%/Arm_Controller0.rtc:arm_endcmd_before /%NS%/Startup_Generation_Before0.rtc:endcmd_from_Arm_Controller

REM [4, 18] Arm_Controller(Out) -> Startup_After(In)
rtcon /%NS%/Arm_Controller0.rtc:arm_endcmd_after /%NS%/Startup_Generation_After0.rtc:endcmd_from_ArmController

REM [5, 12] Arm_Controller(Service) <-> myCobot(Service)
rtcon /%NS%/Arm_Controller0.rtc:middle /%NS%/myCobot0.rtc:middle

REM [6, 13] Arm_Controller(Service) <-> myCobot(Service)
rtcon /%NS%/Arm_Controller0.rtc:common /%NS%/myCobot0.rtc:common

REM 【修正箇所】[17, 7] Startup_Before(Out) -> Hand_Controller(In)
rtcon /%NS%/Startup_Generation_Before0.rtc:endcmd /%NS%/Hand_Controller0.rtc:hand_start

REM [28, 8] Select_Target(Out) -> Hand_Controller(In)
rtcon /%NS%/Select_Target0.rtc:target_out2 /%NS%/Hand_Controller0.rtc:target_id

REM 【修正箇所】[22, 9] Startup_After(Out) -> Hand_Controller(In)
rtcon /%NS%/Startup_Generation_After0.rtc:endcmd_to_HandController /%NS%/Hand_Controller0.rtc:hand_release

REM [10, 19] Hand_Controller(Out) -> Startup_After(In)
rtcon /%NS%/Hand_Controller0.rtc:hand_end /%NS%/Startup_Generation_After0.rtc:endcmd_from_HandController

REM [11, 12] Hand_Controller(Service) <-> myCobot(Service)
rtcon /%NS%/Hand_Controller0.rtc:middle /%NS%/myCobot0.rtc:middle

rtcon /%NS%/Select_Target0.rtc:target_out1 /%NS%/Image_Recognition0.rtc:Target_In1
rtcon /%NS%/Image_Recognition0.rtc:target_point /%NS%/Startup_Generatoin_Before0.rtc:target_point
rtcon /%NS%/Startup_Generation_After0.rtc:endcmd /%NS%/Path_Generation0.rtc:complete

echo.
echo ==========================================
echo 接続処理が完了しました。
echo ==========================================
pause
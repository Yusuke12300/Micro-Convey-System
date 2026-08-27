@echo off
chcp 65001
echo ==========================================
echo Micro-Convey-System コンポーネント起動スクリプト
echo ==========================================

REM ------------------------------------------------
REM 【1】C++ コンポーネント (Debug版)
REM ------------------------------------------------
start "Path_Gen" /D "%~dp0Path_Generation\build\src\Debug" "Path_GenerationComp.exe" -o "naming.formats:%%n.rtc"
start "StartupAfter" /D "%~dp0Startup_Generation_After\build\src\Debug" "Startup_Generation_AfterComp.exe" -o "naming.formats:%%n.rtc"

REM ------------------------------------------------
REM 【2】C++ コンポーネント (Release版)
REM ------------------------------------------------
start "Arm" /D "%~dp0Arm_Controller\build\src\Release" "Arm_ControllerComp.exe" -o "naming.formats:%%n.rtc"
start "Hand" /D "%~dp0Hand_Controller\build\src\Release" "Hand_ControllerComp.exe" -o "naming.formats:%%n.rtc"

REM ------------------------------------------------
REM 【3】Python コンポーネント
REM ------------------------------------------------
start "SelectTarget" /D "%~dp0Select_Target" python "Select_Target.py" -o "naming.formats:%%n.rtc"
start "ImageRecog" /D "%~dp0Image_Recognition" python "Image_Recognition.py" -o "naming.formats:%%n.rtc"
start "StartupBefore" /D "%~dp0Startup_Generation_Before" python "Startup_Generation_Before.py" -o "naming.formats:%%n.rtc"
start "myCobot" /D "%~dp0choreonoid\myCobotRTC" python "myCobot.py" -o "naming.formats:%%n.rtc"

echo.
echo ==========================================
echo 全てのコンポーネントの起動処理が完了しました。
echo ==========================================
pause
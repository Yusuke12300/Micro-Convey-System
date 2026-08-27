@echo off
chcp 65001
echo ==========================================
echo Micro-Convey-System コンポーネント起動スクリプト
echo ==========================================

REM ------------------------------------------------
REM 【1】C++ コンポーネント (Debug版)
REM ------------------------------------------------
start "Path_Gen" /D "%~dp0Path_Generation\build\src\Debug" "Path_GenerationComp.exe"
start "StartupAfter" /D "%~dp0Startup_Generation_After\build\src\Debug" "Startup_Generation_AfterComp.exe"

REM ------------------------------------------------
REM 【2】C++ コンポーネント (Release版)
REM ------------------------------------------------
start "Arm" /D "%~dp0Arm_Controller\build\src\Release" "Arm_ControllerComp.exe"
start "Hand" /D "%~dp0Hand_Controller\build\src\Release" "Hand_ControllerComp.exe"

REM ------------------------------------------------
REM 【3】Python コンポーネント
REM ------------------------------------------------
start "SelectTarget" /D "%~dp0Select_Target" python "Select_Target.py"
start "ImageRecog" /D "%~dp0Image_Recognition" python "Image_Recognition.py"
start "StartupBefore" /D "%~dp0Startup_Generation_Before" python "Startup_Generation_Before.py"
start "myCobot" /D "%~dp0choreonoid\myCobotRTC" python "myCobot.py"

echo.
echo ==========================================
echo 全てのコンポーネントの起動処理が完了しました。
echo ==========================================
pause
@echo off
chcp 65001
echo ==========================================
echo Micro-Convey-System 一括ビルドスクリプト
echo ==========================================

REM ------------------------------------------------
REM 【1】自分が作ったコンポーネント（Debug版）
REM ------------------------------------------------
echo.
echo [1/4] Path_Generation をビルドしています (Debug)...
cd /d "%~dp0Path_Generation\build"
cmake --build . --config Debug

echo.
echo [2/4] Startup_Generation_After をビルドしています (Debug)...
cd /d "%~dp0Startup_Generation_After\build"
cmake --build . --config Debug


REM ------------------------------------------------
REM 【2】他の人が作ったコンポーネント（Release版・初期構成込み）
REM ------------------------------------------------
echo.
echo [3/4] Arm_Controller をビルドしています (Release)...
cd /d "%~dp0Arm_Controller"
if not exist build mkdir build
cd build
cmake ..
cmake --build . --config Release

echo.
echo [4/4] Hand_Controller をビルドしています (Release)...
cd /d "%~dp0Hand_Controller"
if not exist build mkdir build
cd build
cmake ..
cmake --build . --config Release


echo.
echo ==========================================
echo 全てのビルド処理が完了しました！
echo ==========================================
pause
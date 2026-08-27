@echo off
chcp 65001
echo ==========================================
echo Micro-Convey-System 終了スクリプト
echo ==========================================

set NS=localhost

echo [1/1] コンポーネントに終了信号(rtexit)を送信しています...
REM ------------------------------------------------
REM 書式: rtexit /%NS%/コンポーネント名0.rtc
REM ------------------------------------------------

REM --- C++ コンポーネント ---
rtexit /%NS%/Path_Generation0.rtc
rtexit /%NS%/Startup_Generation_After0.rtc
rtexit /%NS%/Arm_Controller0.rtc
rtexit /%NS%/Hand_Controller0.rtc

REM --- Python コンポーネント ---
REM ※Python側もインスタンス名（末尾に0がついた名前）を指定します
rtexit /%NS%/Select_Target0.rtc
rtexit /%NS%/Image_Recognition0.rtc
rtexit /%NS%/Startup_Generation_Before0.rtc
rtexit /%NS%/myCobot0.rtc


echo.
echo ネームサーバーの更新を待機しています...
timeout /t 3 /nobreak >nul

REM ------------------------------------------------
REM 【予備】もしフリーズして閉じない画面があった場合の強制終了コマンド
REM 普段は使いませんが、必要になったら行の先頭の「REM 」を消して使ってください。
REM ------------------------------------------------
REM taskkill /F /IM Path_GenerationComp.exe
REM taskkill /F /IM Startup_Generation_AfterComp.exe
REM taskkill /F /IM Arm_ControllerComp.exe
REM taskkill /F /IM Hand_ControllerComp.exe
REM taskkill /F /IM python.exe


echo.
echo ==========================================
echo 全ての終了処理が完了しました！
echo ==========================================
pause
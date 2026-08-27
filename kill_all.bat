@echo off
chcp 65001
echo ==========================================
echo Micro-Convey-System 強制終了スクリプト
echo ==========================================

echo すべてのコンポーネントを強制終了(taskkill)します...
REM ------------------------------------------------
REM 書式 taskkill F(強制) IM(イメージ名) 実行ファイル名
REM ネームサーバーの状態に関係なく、Windowsの権限でプロセスを直接キルします。
REM ------------------------------------------------

REM --- C++ コンポーネント ---
taskkill F IM Path_GenerationComp.exe
taskkill F IM Startup_Generation_AfterComp.exe
taskkill F IM Arm_ControllerComp.exe
taskkill F IM Hand_ControllerComp.exe

REM --- Python コンポーネント ---
REM ※注意：python.exeをキルすると、ロボットと無関係な裏で動いているPythonプログラムも巻き添えで終了します。
REM 他にPythonを動かしていなければ、これで一掃できます。
taskkill F IM python.exe


echo.
echo ==========================================
echo 強制終了が完了しました。
echo ==========================================
pause
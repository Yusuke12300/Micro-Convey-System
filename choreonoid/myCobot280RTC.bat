set PYTHONPATH=%~dp0\python-3.12.10-embed-amd64;%~dp0\myCobotRTC
set PYTHONHOME=%~dp0\python-3.12.10-embed-amd64
set PATH=%~dp0\python-3.12.10-embed-amd64;%PATH%
cd %~dp0\myCobotRTC
%~dp0\python-3.12.10-embed-amd64\python.exe %~dp0\myCobotRTC\myCobot.py -f %~dp0\myCobotRTC\rtc.conf
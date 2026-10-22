@echo off
title 宝贝学习乐园 - 手机访问
cd /d "%~dp0"
set "PY=C:/Users/Charles Qiu\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
if exist "%PY%" goto run
where py >nul 2>nul && set "PY=py -3" && goto run
where python >nul 2>nul && set "PY=python" && goto run
echo.
echo [x] 没找到 Python 运行环境。
echo     你仍然可以直接双击 index.html 在电脑上玩（全部功能可用）。
echo     想用手机访问，请先安装 Python 3：https://www.python.org/downloads/
echo.
pause
exit /b 1
:run
%PY% serve_phone.py
echo.
pause

@echo off
FOR /F "tokens=*" %%i in ('type %~dp0token.txt') do set TOKEN=%%i
python bot.py %*
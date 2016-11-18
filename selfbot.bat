@echo off
:start
echo ~~~~~~~~~~~~NEW INSTANCE~~~~~~~~~~~~~~~~
python selfbot.py
ping -n 5 127.0.0.1>NUL
goto start
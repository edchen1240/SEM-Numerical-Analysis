@echo off
set "dir_current=%~dp0"
set "dir_current=%dir_current:~0,-1%"
set "bsn_suffix=_Dashboard"

:loop
cd /d "D:\01_Floor\a_Ed\09_EECS\10_Python\00_Classes and Functions\01_Independent Scripts"
python "IS_format screenshot filenames.py" "%dir_current%" "%bsn_suffix%"

echo.
echo Press ENTER to run again, or Ctrl+C to exit.
pause >nul
goto loop


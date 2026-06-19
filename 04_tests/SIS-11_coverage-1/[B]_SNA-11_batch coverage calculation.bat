@echo off
set "dir_current=%~dp0"

:loop
cd /d "D:\01_Floor\a_Ed\09_EECS\10_Python\04_Ready\2024-0828_SEM Numerical Analysis\02_scripts"
python "SNA-11_batch coverage calculation.py" "%dir_current%"

echo.
echo Press ENTER to run again, or Ctrl+C to exit.
pause >nul
goto loop

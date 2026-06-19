@echo off
set "dir_current=%~dp0"

:loop
cd /d "D:\01_Floor\a_Ed\09_EECS\10_Python\04_Ready\2026-0617_PresentationIntegration\02_scripts"
python "03_Convert PPT to MD.py" "%dir_current%"

echo.
echo Press ENTER to run again, or Ctrl+C to exit.
pause >nul
goto loop


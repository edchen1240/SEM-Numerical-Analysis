@echo off
set "dir_current=%~dp0"
cd /d "D:\01_Floor\a_Ed\09_EECS\10_Python\04_Ready\2024-0828_SEM Numerical Analysis\02_scripts"
python "SNA-30_Remove all generated files.py" "%dir_current%"
exit
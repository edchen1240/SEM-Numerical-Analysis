@echo off
set "dir_current=%~dp0"
cd /d "D:\01_Floor\a_Ed\09_EECS\10_Python\05_Complete\2022-0603_Personal Media Organizer\02_scripts"
python "PMO-14_convert everything to JPG - Single Folder.py" "%dir_current%"
exit
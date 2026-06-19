@echo off
set "dir_current=%~dp0"
cd /d "D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2022-0603_Media Date Sorting"
python "MDS-15_convert image to JPG (skip PNG) - Single Folder.py" "%dir_current%"
exit
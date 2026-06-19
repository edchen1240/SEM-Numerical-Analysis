"""
[BLK-0_sandbox.py]
Purpose: 
Author: Meng-Chi Ed Chen
Date: 
Reference:
    1.
    2.

Status: Complete.
"""
import os, sys, cv2, time
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SEMNumericalAnalysis import SNA_M1_Utility as M1UTIL
from SEMNumericalAnalysis import SNA_M2_Image as M2IMG


#[1] Get the directory path from the command-line arguments
if len(sys.argv) < 2:
    message = (
        f"\nlen(sys.argv) = {len(sys.argv)}. sys.argv = {sys.argv}.\n"
        "This code is designed to be run from the terminal using a batch file and requires an input argument (typically a directory address).\n"
        "Please run the code using the batch file (.bat), or comment out this check if you are running it in a different environment.\n"
    )
    print(message)
    raise ValueError(message)
    sys.exit()

#[2] Remove trailing double-quote and slash if any
dir_current = sys.argv[1].rstrip('\"').rstrip('/')      
print(f'\nCurrent directory: {dir_current}')


#[1] Assign path.
#dir_sort = r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-16_Extract Scale (batch)'
dir_sort = dir_current

#[2] Filter files.
list_remove = ['scale', '_(', ').', 'col', 'mean']
list_keep = ['.bat']
list_paths, list_bsns = M1UTIL.batch_file_relocate(dir_sort, list_remove, list_keep, '01_dump', True)

print('\nCompleted. Close in 5 seconds.')
time.sleep(5)
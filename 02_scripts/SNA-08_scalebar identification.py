"""
[BLK-0_sandbox.py]
Purpose: 
Author: Meng-Chi Ed Chen
Date: 
Reference:
    1.
    2.

Status: Working.
"""
import os, sys, cv2
import numpy as np
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SEMNumericalAnalysis import SNA_M1_Utility as M1UTIL
from SEMNumericalAnalysis import SNA_M2_Image as M2IMG
from SEMNumericalAnalysis import SNA_M3_Scalebar as M3SCB


"""
Small test of calculating circumference
"""


#[1] Set dir.
dir_sample  = r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-01_Scalebar examples\01_Ready'
dir_check   = r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-01_Scalebar examples'

#[3] Read files.
list_paths_check, list_bsns_check = M1UTIL.filter_file_in_dir_with_keywords(dir_check, ['.jpg'], [], False)
list_paths_sample, list_bsns_sample = M1UTIL.filter_file_in_dir_with_keywords(dir_sample, ['.jpg'], [], False)

#[5] Read scalebar sample images into list of arraies.
list_scalbar_samples, list_sbar_text = M3SCB.read_scalebar_sample_images_into_list_of_arries(dir_sample)

# [10] Trim off edges in dir_sample
trim_off_edge_in_sample = False

if trim_off_edge_in_sample:
    for i, i_path_sample in enumerate(list_paths_sample):
        # [11] Read the image, trim, and overwrite
        arr_sample = cv2.imread(i_path_sample)
        print(f'-- Processing {list_bsns_sample[i]}. Shape: {arr_sample.shape}')
        
        #[12] Ensure trimming is applied correctly
        arr_trimmed = M3SCB.trim_off_white_edges_of_arrimg(arr_sample, white_tolerance=5, smooth_k=2, edge_pixel=1)

        #[15] Report if dimensions changed after trimming
        bsn, ext = os.path.splitext(list_bsns_sample[i])
        path_trimmed = os.path.join(dir_check, f'{bsn}_trimmed{ext}')
        cv2.imwrite(path_trimmed, arr_trimmed)
        h_orig, w_orig = arr_sample.shape[:2]
        h_trim, w_trim = arr_trimmed.shape[:2]
        if h_orig != h_trim or w_orig != w_trim:
            print(f'-- File {list_bsns_sample[i]} trimmed from {h_orig, w_orig} to {h_trim, w_trim}.')
        else:
            print(f'-- File {list_bsns_sample[i]} remains unchanged.')


        
diff_tolerance = 1
similarity_thr = 0.9

#[4] Iterate through files.
for i, i_path_check in enumerate(list_paths_check):
    
    #[5] Read image being check.
    print(f'\n\n[{i}] Checking {list_bsns_check[i]}')
    arr_check = cv2.imread(i_path_check)
    
    
    sclbar_text = M3SCB.identify_scalebar_text(arr_check, list_scalbar_samples, list_sbar_text, similarity_thr)
    print(f'-- {list_bsns_check[i]} = \t{sclbar_text}')
    
    
    
    if i>3:
        sys.exit()
    
    
    


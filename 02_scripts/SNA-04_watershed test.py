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
from SEMNumericalAnalysis import SNA_M4_Segmentation as M4SEG

"""
Small test of calculating circumference
"""

dir_img = r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-08_watershed-2'


#[2] Filter files.
list_paths, list_bsns = M1UTIL.filter_file_in_dir_with_keywords(dir_img, ['TM92_A-Sapp', '(2-elrg)'], ['scal', 'mean', '5-bnrz','6-ovlp', '7-wtsd', 'C-D-'], True)

#[3] Initiate empty lists.
list_circumf = []
list_area = []
list_GV = []




for i, iter_path in enumerate(list_paths):
    
    #[10] Binerize and invert color.
    path_img_5bnrz, arrimg_5bnrz, otsu_threshold = M2IMG.binerize_image(iter_path, tag_bnrz='5-bnrz', invert=True)
    
    bnry_sm_k = 31
    arrimg_5bnrz_sm = M2IMG.quick_binary_smoothing(arrimg_5bnrz, bnry_sm_k)
    bsn_ext = os.path.basename(path_img_5bnrz)
    path_img_5bnrz_sm = M2IMG.replace_pattern_in_filename_and_save(dir_img, bsn_ext, '5-bnrz-1sm', arrimg_5bnrz_sm)
    
    
    
    #[12] Watershed.
    frgd_thrs_ratio = 0.45
    frgd_GB_k = 31
    morph_kernel = 3
    dist_transform_mask = 5
    
    tag_ovlp=f'6-ovlp[bsmk{bnry_sm_k}, fthr{frgd_thrs_ratio}, fGBk{frgd_GB_k}, mk{morph_kernel}, dtm{dist_transform_mask}]'
    tag_wtsd=f'7-wtsd[bsmk{bnry_sm_k}, fthr{frgd_thrs_ratio}, fGBk{frgd_GB_k}, mk{morph_kernel}, dtm{dist_transform_mask}]'
    save_interm = True
    thick_boundary = True
    
    
    path_img_6wtsd, arrimg_inpt = M2IMG.watershed_image(path_img_5bnrz_sm,
                                                        tag_ovlp,
                                                        tag_wtsd,
                                                        frgd_thrs_ratio,
                                                        frgd_GB_k,
                                                        morph_kernel,
                                                        dist_transform_mask,
                                                        save_interm,
                                                        thick_boundary)
    
    
    



sys.exit()


#[5] Collect into dataframe.
df_segs = pd.DataFrame({'list_bsns': list_bsns,
                        'list_circumf': list_circumf,
                        'list_area': list_area, 
                        'cir/area': [c / a if a != 0 else 0 for c, a in zip(list_circumf, list_area)],
                        'cir^2/area': [c**2 / a if a != 0 else 0 for c, a in zip(list_circumf, list_area)]})


print(tabulate(df_segs, headers="keys", tablefmt="orgtbl"))


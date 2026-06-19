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
import os, sys, cv2, torch
import numpy as np
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt

sys.path.insert(1, r'D:\01_Floor\a_Ed\09_EECS\10_Python\00_Classes and Functions')
import F02_File as F02_File # type: ignore

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SEMNumericalAnalysis import SNA_M1_Utility as M1UTIL
from SEMNumericalAnalysis import SNA_M2_Image as M2IMG
from SEMNumericalAnalysis import SNA_M4_Segmentation as M4SEG



#[2] Settings
crop_image = False
pixels_per_um = 450 * 3  # The 3 is that we enlarge the image before processing.

#[2] Assign path.
path_img = r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-09_seg basic\B859_wtsd.jpg'
arrimg = cv2.imread(path_img)
dir_img = os.path.dirname(path_img)
bsn_ext = os.path.basename(path_img)
bsn, ext = os.path.splitext(bsn_ext)

#[4] Crop image
if crop_image:
    length = 500
    path_bsn, ext = os.path.splitext(path_img)
    path_img_crop = f'{path_bsn}_crop_{ext}'
    M1UTIL.crop_image_center_square(path_img, length, path_img_crop)
    path_img = path_img_crop


#[8] Iterate two list together.
arr3d_seg_masks, cnt_seg = M4SEG.segment_image_black_bkgd(path_img)

#[9] Overlap result
edge_pixel = 3
font_size = 1
tag_ovlp = f'_7-ovlp(basic seg)'
output_path, df_segs, dict_nd_gs_cf\
    = M4SEG.overlap_every_segmentation_results_as_a_single_image(arr3d_seg_masks, 
                                                                path_img, 
                                                                edge_pixel, 
                                                                font_size, 
                                                                tag_ovlp,
                                                                save_segs=True)


#[12] Convert unit from pixel to nm.
nucle_dsty_psqum = dict_nd_gs_cf['nucle_dsty_psqpx'] * (pixels_per_um**2)
avg_grain_size_squm =  dict_nd_gs_cf['avg_grain_size_sqpx'] / (pixels_per_um**2)
std_grain_size_squm =  dict_nd_gs_cf['std_grain_size_sqpx'] / (pixels_per_um**2)
avg_circumf_um =  dict_nd_gs_cf['avg_circumf_px'] / (pixels_per_um)
std_circumf_um =  dict_nd_gs_cf['std_circumf_px'] / (pixels_per_um)

print(f'-- [Nucleation density]        \t{nucle_dsty_psqum:.3e} (crystal / um^2)')
print(f'-- [Grain size (mean, std)]    \t{avg_grain_size_squm:.3f} (um^2), \t {std_grain_size_squm:.3f} (um^2)')
print(f'-- [Circumference (mean, std)] \t{avg_circumf_um:.3f} (um), \t {std_circumf_um:.3f} (um)')

#[15] Save segmentation result.
path_xlsx = os.path.join(dir_img, f'{bsn}_seg.xlsx')
sheet_name = 'seg'
M1UTIL.save_df_as_excel_overwrite(df_segs, path_xlsx, sheet_name)
M1UTIL.adjust_multiple_column_widths(path_xlsx, sheet_name, ['B', 'C', 'D', 'E', 'F', 'G'], [15, 15, 15, 15, 15, 15])











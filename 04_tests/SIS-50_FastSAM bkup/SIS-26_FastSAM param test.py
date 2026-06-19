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
from SEMNumericalAnalysis import SNA_M1_Utility as M1UTIL
from SEMNumericalAnalysis import SNA_M2_Image as M2IMG
import SIS_M3_Segmentation as M3SEG



#[2] Settings
crop_image = False

#[2] Assign path.
path_FastSAM_model_pt = r'D:\01_Floor\a_Ed\09_EECS\10_Python\weights\FastSAM-x.pt'
path_img = r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-09_seg\B859_wtsd.jpg'

#[4] Crop image
if crop_image:
    length = 500
    path_bsn, ext = os.path.splitext(path_img)
    path_img_crop = f'{path_bsn}_crop_{ext}'
    M1UTIL.crop_image_center_square(path_img, length, path_img_crop)
    path_img = path_img_crop

#[7] Segmentation setting list.  
list_conf = [0.01, 0.05, 0.10, 0.20]
list_ioui = [0.05, 0.05, 0.05, 0.05]

#[8] Iterate two list together.
for iter_conf, iter_ioui in zip(list_conf, list_ioui):
    segmentation_results, cnt_seg = M3SEG.segment_single_image(path_img, path_FastSAM_model_pt, iter_conf, iter_ioui)

    #[9] Overlap result
    font_size = 1
    tag_ovlp = f'_7-ovlp(C{iter_conf}, I{iter_ioui}; S{cnt_seg})'
    M3SEG.overlap_every_segmentation_results_as_a_single_image(segmentation_results, path_img, font_size, tag_ovlp)




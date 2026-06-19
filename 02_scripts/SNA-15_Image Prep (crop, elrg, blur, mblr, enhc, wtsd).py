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
import os, sys, cv2, torch, time
import numpy as np
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt


from SEMNumericalAnalysis import SNA_M1_Utility as M1UTIL
from SEMNumericalAnalysis import SNA_M2_Image as M2IMG
import SIS_M3_Segmentation as M4SEG

#[2] Settings
crop_image = True
tag_crop='1-crop'
enlarge_image = True
tag_elrg='2-elrg'
correct_image = True
tag_mblr='3-mblr'
medblur_k = 7
tag_enhc='4-enhc'
enh_cliplmt = 1.5
enh_tileGrid = 12
binerize_image = True
tag_bnrz='5-bnrz'
water_shed = True
tag_ovlp='6-ovlp'
tag_wtsd='7-wtsd'
frgd_thrs_ratio = 0.4
frgd_GB_k = 37
morph_kernel=3
dist_transform_mask=5

#[2] Assign path.
path_img = r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-08_watershed\B845_btm_10.jpg'

#[4] Crop image
if crop_image:
    length = 500
    path_bsn, ext = os.path.splitext(path_img)
    path_img_crop = f'{path_bsn}_crop_{ext}'
    path_img_1crop, arrimg_1crop = M2IMG.crop_image_center_square(path_img, 
                                                                    tag_crop, 
                                                                    length=length,)
    path_img = path_img_1crop

#[5] Enlarge image
if enlarge_image:
    path_img_2elrg, arrimg_2elrg = M2IMG.enlarge_image(path_img, 
                                                        tag_elrg, ratio_magnify=3)
    path_img = path_img_2elrg

#[6] Enhance image
if correct_image:
    path_img_3enhc, arrimg_3enhc = M2IMG.quick_image_correction(path_img, 
                                                                tag_mblr, medblur_k, 
                                                                tag_enhc, enh_cliplmt, enh_tileGrid)
    path_img = path_img_3enhc

#[7] Binerize image
if binerize_image:
    path_img_5bnrz, arrimg_5bnrz, otsu_threshold = M2IMG.binerize_image(path_img, tag_bnrz)
    path_img = path_img_5bnrz


#[8] Watershed image
if water_shed:
    path_img_6wtsd, arrimg_6wtsd = M2IMG.watershed_image(path_img,
                                                        tag_ovlp,
                                                        tag_wtsd,
                                                        frgd_thrs_ratio,
                                                        frgd_GB_k,
                                                        morph_kernel,
                                                        dist_transform_mask,
                                                        save_interm=True,
                                                        thick_boundary=True)
    
    path_img = path_img_6wtsd
    
    
    
    


print('\nCompleted. Close in 5 seconds.')
time.sleep(5)

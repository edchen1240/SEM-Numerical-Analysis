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
import os, sys, cv2, gc
import numpy as np
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.signal import convolve2d

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SEMNumericalAnalysis import SNA_M1_Utility as M1UTIL
from SEMNumericalAnalysis import SNA_M2_Image as M2IMG
from SEMNumericalAnalysis import SNA_M4_Segmentation as M4SEG


"""
Small test of calculating circumference
"""



dir_img = r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-11_coverage-4'


#[2] Filter files.
list_paths, list_bsns = M1UTIL.filter_file_in_dir_with_keywords(dir_img, [], ['_p', '3-mblr', '4-enhc'], True)

#[3] Initiate empty lists.
list_brightest_1 = []
list_brightest_2 = []
list_GV = []






use_MB = False
blur_k = 31
enh_cliplmt = 1.5
enh_tileGrid = 10
tag_mblr=f'3-blr({blur_k})'
tag_enhc=f'4-enhc({enh_cliplmt}, {enh_tileGrid})'
lm_gbk = 51
lm_wdk = 100
lm_wds = 40
lm_pad = 20
lm_edge = 5
lm_cr = 5
lm_mark_original = True

for i, iter_path in enumerate(list_paths):
    
    arrimg = cv2.imread(iter_path)
    brightest_pixel_value = arrimg.max() 
    
    
    list_brightest_1.append(brightest_pixel_value)
    print(brightest_pixel_value)
    
    #[8] Quick blur and enhance.
    path_img_3mblr, path_img_4enhc, arrimg_4enhc \
        = M2IMG.quick_image_correction_path_img(iter_path, use_MB, 
                                                tag_mblr, blur_k, tag_enhc, 
                                                enh_cliplmt, enh_tileGrid)
    
    
    #[10] Mark local maximum.
    arrimg_local_max = M2IMG.mark_local_max_on_dt(path_img_4enhc
                                      , lm_gbk, lm_wdk, lm_wds, lm_pad, lm_edge, lm_cr
                                      , lm_mark_original)
    
    #[11] Add the two images together and clip the values to stay within [0, 255]
    #arrimg_4enhc = cv2.cvtColor(arrimg_4enhc, cv2.COLOR_BGR2GRAY)
    #arrimg_local_max = np.clip(arrimg_local_max + arrimg_4enhc, 0, 255).astype(np.uint8)
    
    bsn, ext = os.path.splitext(list_bsns[i])
    path_image = os.path.join(dir_img, f'{bsn}_p({lm_gbk}, {lm_wdk}, {lm_wds}){ext}')
    cv2.imwrite(path_image, arrimg_local_max)
    
    
    
    brightest_pixel_value = arrimg_local_max.max() 
    list_brightest_2.append(brightest_pixel_value)
    
    

gc.collect()



#[5] Collect into dataframe.
df_segs = pd.DataFrame({'list_bsns': list_bsns,
                        'list_brightest_1': list_brightest_1,
                        'list_brightest_2': list_brightest_2,
                        })


print(tabulate(df_segs, headers="keys", tablefmt="orgtbl"))




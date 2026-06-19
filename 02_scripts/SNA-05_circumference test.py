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

dir_img = r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-05_Circumf'


#[2] Filter files.
list_paths, list_bsns = M1UTIL.filter_file_in_dir_with_keywords(dir_img, [], ['scal', 'mean'], True)

#[3] Initiate empty lists.
list_circumf = []
list_area = []
list_GV = []



for i, iter_path in enumerate(list_paths):
    arr_img = cv2.imread(iter_path)
    circumf_px, area_px = M4SEG.circumference_and_edge_roughness(arr_img, obj_is_white=True)
    list_circumf.append(circumf_px)
    list_area.append(area_px)


#[5] Collect into dataframe.
df_segs = pd.DataFrame({'list_bsns': list_bsns,
                        'list_circumf': list_circumf,
                        'list_area': list_area, 
                        'cir/area': [c / a if a != 0 else 0 for c, a in zip(list_circumf, list_area)],
                        'cir^2/area': [c**2 / a if a != 0 else 0 for c, a in zip(list_circumf, list_area)]})


print(tabulate(df_segs, headers="keys", tablefmt="orgtbl"))


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
from scipy.signal import convolve2d

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SEMNumericalAnalysis import SNA_M2_Image as M2IMG


"""
Small test of calculating circumference
"""




# [8] Example usage
path_img = r"D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-15_Extract Scale (single)\B626_center_00_test ext_(9-sbar-1).jpg"
arrimg_sbar_1 = cv2.imread(path_img, cv2.IMREAD_GRAYSCALE)

#arrimg_sbar_1 = M2IMG.rotate_image_clockwise(arrimg_sbar_1, -5)
arrimg_sbar_1 = M2IMG.trim_off_white_edges_of_arrimg(arrimg_sbar_1, 5, smooth_k=3, edge_pixel=10)
arrimg_sbar_1 = M2IMG.rotate_image_clockwise(arrimg_sbar_1, -5, 3)
arrimg_sbar_1 = M2IMG.img_enlarge_and_enhance(arrimg_sbar_1, 5, 7, 2, 8)



# [9] Save the trimmed image
output_path = path_img.replace('.jpg', '_trim.jpg')
cv2.imwrite(output_path, arrimg_sbar_1)
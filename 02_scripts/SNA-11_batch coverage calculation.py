"""
[SNA-11_batch coverage calculation.py]
Purpose: 
Author: Meng-Chi Ed Chen
Date: 
Reference:
    1.
    2.

Status: Working.
"""
import os, sys, cv2, time, gc
import numpy as np
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SEMNumericalAnalysis import SNA_M1_Utility as M1UTIL
from SEMNumericalAnalysis import SNA_M2_Image as M2IMG





#[1] Set directory
prep_for_stage = 'coverage'
dir_path, dir_bsn = M1UTIL.get_working_dir_from_sysargv()
M1UTIL.fully_remove_previous_test_files(dir_path, prep_for_stage)



#[1] Assign directories or paths.
list_kwd_yes_or_1=['jpg', 'png']
list_kwd_no_or_2=['binary', 'histg', 'mblr', 'enhc']
list_paths, list_bsns = M1UTIL.filter_file_in_dir_with_keywords(dir_path, list_kwd_yes_or_1, list_kwd_no_or_2, True)

#[2] Conversion settings.
image_correction = True
medblur_k = 3
enh_cliplmt = 1.5
enh_tileGrid = 12
cvrg_spl_rt = 0.05


#[3] Initiate empty lists.
list_threshold = []
list_original_size = []
list_reduced_size = []
list_pct_black, list_pct_white = [], []

#[4] Plot graysca
for i, iter_path in enumerate(list_paths):
    
    #[8] Quick Image correction
    if image_correction:
        path_img_3mblr, path_img_4enhc, arrimg_4enhc \
            = M2IMG.quick_image_correction_path_img(iter_path, 
                tag_mblr='3-mblr', 
                blur_k=medblur_k, 
                tag_enhc='4-enhc', 
                enh_cliplmt=enh_cliplmt, 
                enh_tileGrid=enh_tileGrid)

    else:
        path_img_4enhc = iter_path
        
    #[5] Plot intensity_histogram.
    tag_previous='_3-enhc'
    tag_binary='_4-binary'
    tag_hist='_5-histg'
    otsu_threshold, path_img_5bnrz, arrimg_5bnrz, path_histg, list_coverage_info\
        = M2IMG.plot_intensity_histogram_for_grayscale_image(path_img_4enhc, 
                                                                        tag_previous, 
                                                                        tag_binary, 
                                                                        tag_hist, 
                                                                        cvrg_spl_rt)
    [h, w], [cpsd_w, cpsd_h], pct_black, pct_white = list_coverage_info
    
    #[8] Append lists.
    list_threshold.append(otsu_threshold)
    list_original_size.append([h, w])
    list_reduced_size.append([cpsd_w, cpsd_h])
    list_pct_black.append(pct_black)
    list_pct_white.append(pct_white)
    
    #[10] Release memory after processing each image
    del arrimg_4enhc, arrimg_5bnrz, list_coverage_info  # Delete large variables
    gc.collect()  # Force garbage collection
    
    
#[12] Organize lists into dataframe.
df_coverage = pd.DataFrame({'file name': list_bsns,
                        'threshold': list_threshold,
                        'original_size': list_original_size,
                        'reduced_size': list_reduced_size,
                        'pct_black': list_pct_black,
                        'pct_white': list_pct_white})
print(f'--[Coverage]\n{tabulate(df_coverage, headers="keys", tablefmt="orgtbl")}\n\n')
                           
#[15] Save dataframe as excel
timestamp = datetime.now().strftime("%Y-%m%d-%H%M%S")
path_xlsx = os.path.join(dir_path, f'{timestamp}_coverage.xlsx')
sheet_name = 'coverage'
M1UTIL.save_df_as_excel_overwrite(df_coverage, path_xlsx, sheet_name)
M1UTIL.adjust_multiple_column_widths(path_xlsx, sheet_name, ['B', 'C', 'D', 'E', 'F', 'G'], [30, 15, 15, 15, 15, 15])

#[18] Add image process setting info into excel.
text_to_add = f'image_correction\t{image_correction}\n'\
                f'medblur_k\t{medblur_k}\n'\
                f'enh_cliplmt\t{enh_cliplmt}\n'\
                f'enh_tileGrid\t{enh_tileGrid}\n'
M1UTIL.add_text_after_the_last_row_in_an_excel_sheet(path_xlsx, sheet_name, text_to_add, row_gap=2, col='B')


print('\nCompleted. Close in 5 seconds.')
time.sleep(5)


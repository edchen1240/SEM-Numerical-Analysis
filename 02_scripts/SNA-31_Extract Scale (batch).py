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
dir_sort = dir_current

#[1] Assign path.
#dir_sort= r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-16_Extract Scale (batch)'
dir_scalebars = r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-01_Scalebar examples\01_Ready'

#[2] Filter files.
list_paths, list_bsns = M1UTIL.filter_file_in_dir_with_keywords(dir_sort, [], ['scal', 'mean', 'xlsx', 'bat', 'sbar', 'col', 'mean'], False)

#[3] Turn on all to True for debug.
debug_scale_bar_extraction = False
if debug_scale_bar_extraction:
    plot_graph, print_msg, save_img = False, False, True
else:
    plot_graph, print_msg, save_img = False, False, False

#[3] Initiate empty lists.
list_sclbar_text, list_pixel_length_sclbar, list_pixels_per_um = [], [], []

for i, iter_path in enumerate(list_paths):

    #[3] Extract scale mark, measure length, and add text to image.
    path_img_scal, arrimg_scal = M2IMG.extract_scale_mark_in_image(iter_path, 
                                                                    tag_scle='8-scal', 
                                                                    plot_graph=plot_graph, 
                                                                    print_msg=print_msg,
                                                                    save_img=save_img)
    
    pixel_length_sclbar, sclbar_text = M2IMG.extract_scale_bar_only_and_measure_length(path_img_scal, 
                                                                                       dir_scalebars, 
                                                                                        tag_scle='9-sbar', 
                                                                                        scale_bar_adj=-1,
                                                                                        plot_graph=plot_graph,
                                                                                        print_msg=print_msg,
                                                                                        save_img=save_img)
    
    M2IMG.add_text_to_image(path_img_scal,f'{sclbar_text.replace("µ", "u")}', 0.5, 2, 10, 35) 
    M2IMG.add_text_to_image(path_img_scal,f'{pixel_length_sclbar}px', 0.5, 2, 10, 50)    
    
    pixels_per_um = M2IMG.turn_text_and_pixel_into_pixels_per_um(pixel_length_sclbar, sclbar_text)

    print(f'\n[{i:04d}] Result: {pixel_length_sclbar} pixel for {sclbar_text}. Pixel per um: {pixels_per_um}')
    list_sclbar_text.append(sclbar_text)
    list_pixel_length_sclbar.append(pixel_length_sclbar)
    list_pixels_per_um.append(pixels_per_um)



#[5] Create df_segs.
print(f'list_bsns: \t {len(list_bsns)}')
print(f'list_sclbar_text: \t {len(list_sclbar_text)}')
print(f'list_pixel_length_sclbar: \t {len(list_pixel_length_sclbar)}')
print(f'list_pixels_per_um: \t {len(list_pixels_per_um)}')

df_scale = pd.DataFrame({'bsns': list_bsns,
                        'sclbar_text': list_sclbar_text,
                        'pixel_length_sclbar': list_pixel_length_sclbar,
                        'pixels_per_um': list_pixels_per_um})

#[15] Save scale result.
timestamp = datetime.now().strftime("%Y-%m%d-%H%M%S")
path_xlsx = os.path.join(dir_sort, f'{timestamp}_scale.xlsx')
sheet_name = '01_Scale'
M1UTIL.save_df_as_excel_overwrite(df_scale, path_xlsx, sheet_name)
M1UTIL.adjust_multiple_column_widths(path_xlsx, sheet_name, ['B', 'C', 'D', 'E'], [20, 20, 20, 20])


print('\nCompleted. Close in 5 seconds.')
time.sleep(5)


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
import os, sys, cv2, time
from datetime import datetime
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SEMNumericalAnalysis import SNA_M1_Utility as M1UTIL
from SEMNumericalAnalysis import SNA_M2_Image as M2IMG
from SEMNumericalAnalysis import SNA_M4_Segmentation as M4SEG



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




#[1] Assign path.
#dir_sort= r'D:\01_Floor\a_Ed\09_EECS\10_Python\03_MatureTools\2024-0828_SEM image segmentation\SIS-16_Extract Scale (batch)'
dir_sort = dir_current

#[2] Find the scale excel file.
path_scale_xlsx = M1UTIL.find_scale_excel_file_in_folder(dir_sort)
df_scale = M1UTIL.read_excel_into_df(path_scale_xlsx, sheet_name='01_Scale')

#[3] Unpack dataframe.
list_bsns = df_scale['bsns'].tolist()
list_sclbar_text = df_scale['sclbar_text'].tolist()
list_pixel_length_sclbar = df_scale['pixel_length_sclbar'].tolist()
list_pixels_per_um_norm = df_scale['pixels_per_um'].tolist()
list_paths = [os.path.join(dir_sort, basename) for basename in list_bsns]

#[3] Settings - image_prep
ratio_magnify = 3
prep_use_MB = True
prep_blur_k = 13
prep_enh_cliplmt = 1.2
prep_enh_tileGrid = 30
cvrg_spl_rt = 0.05
morph_k=3
dt_mask=5
dt_blur_k=31
dt_enh_cliplmt=1.5
dt_enh_tileGrid=10
lm_gbk=51
lm_wdk=100
lm_wds=40
lm_pad=50
lm_edge=5
lm_cr=5
lm_mark_original = True
frgd_thrs_ratio = 0.4
frgd_GB_k = 37
#[3] Settings - process_single_image_segmentation
edge_pixel = 3
font_size = 1
r_seg_area_lim_lu = [0.001, 0.9]

#[3] Initiate empty lists. (nd = nucleoation density, gs = grain size.)
list_pixels_per_um_w_mag = [pixels_per_um * (1/ratio_magnify) for pixels_per_um in list_pixels_per_um_norm]
list_pct_black, list_pct_white = [], []
list_cnt_seg, list_nd_per_sqnm = [], []
list_avg_gs_squm, list_std_gs_squm = [], []
list_avg_circumf_um, list_std_circumf_um = [], []
list_avg_csar, list_std_csar = [], []
list_avg_bkgd_pixel, list_std_bkgd_pixel = [], []
    
for i, iter_path in enumerate(list_paths):
    #[5] Image preparation.
    path_img, list_path_interms, list_coverage_info \
        = M2IMG.image_prep(iter_path, 
                            ratio_magnify,
                            prep_use_MB,
                            prep_blur_k, prep_enh_cliplmt, prep_enh_tileGrid,
                            cvrg_spl_rt,
                            morph_k, dt_mask, dt_blur_k, dt_enh_cliplmt, dt_enh_tileGrid,
                            lm_gbk, lm_wdk, lm_wds, 
                            lm_pad, lm_edge, lm_cr, lm_mark_original,
                            frgd_thrs_ratio, frgd_GB_k)

    
    #[6] Unpack coverage data.
    [h, w], [cpsd_w, cpsd_h], pct_black, pct_white = list_coverage_info
    
    #[8] Iterate two list together.
    arr3d_seg_masks, cnt_seg_raw \
        = M4SEG.segment_single_image_black_bkgd(path_img)

    #[9] Overlap result
    output_path, df_single_img, dict_nd_gs_cf \
        = M4SEG.process_single_image_segmentation(arr3d_seg_masks, 
                                                path_img, 
                                                edge_pixel, 
                                                font_size, 
                                                f'_8-ovlp(basic seg)',
                                                r_seg_area_lim_lu,
                                                save_segs=True)
    
    #[10] Call out variables in dict_nd_gs_cf.
    cnt_seg_success = dict_nd_gs_cf.get('cnt_seg_success')
    nucle_dsty_psqpx = dict_nd_gs_cf.get('nucle_dsty_psqpx')
    avg_grain_size_sqpx = dict_nd_gs_cf.get('avg_grain_size_sqpx')
    std_grain_size_sqpx = dict_nd_gs_cf.get('std_grain_size_sqpx')
    avg_circumf_px = dict_nd_gs_cf.get('avg_circumf_px')
    std_circumf_px = dict_nd_gs_cf.get('std_circumf_px')
    avg_csar = round(dict_nd_gs_cf.get('avg_csar'), 3)
    std_csar = round(dict_nd_gs_cf.get('std_csar'), 3)
    avg_bkgd_pixel = dict_nd_gs_cf.get('avg_bkgd_pixel')
    std_bkgd_pixel = dict_nd_gs_cf.get('std_bkgd_pixel')
    
    #[12] Convert unit from pixel to nm.
    iter_pixel_per_um = round(list_pixels_per_um_w_mag[i], 3)
    nucle_dsty_psqum = round(nucle_dsty_psqpx * (iter_pixel_per_um**2), 3)
    avg_gs_squm =  round(avg_grain_size_sqpx / (iter_pixel_per_um**2), 3)
    std_gs_squm =  round(std_grain_size_sqpx / (iter_pixel_per_um**2), 3)
    avg_circumf_um =  round(avg_circumf_px / (iter_pixel_per_um), 3)
    std_circumf_um =  round(std_circumf_px / (iter_pixel_per_um), 3)
    print(f'\n[{i:04d}] {list_bsns[i]}')
    print(f'-- [Black percentage]      \t{pct_black * 100:.3f} (%)')
    print(f'-- [White percentage]      \t{pct_white * 100:.3f} (%)')
    print(f'-- [Count of Segmentation] \t{cnt_seg_success:.0f} (cnt)')
    print(f'-- [Nucleation Density]    \t{nucle_dsty_psqum:.3f} (crystal / um^2)')
    print(f'-- [Average Grain Size]    \t{avg_gs_squm:.3f} (um^2)')
    print(f'-- [STD of Grain Size]     \t{std_gs_squm:.3f} (um^2)')
    print(f'-- [Average Circumference] \t{avg_circumf_um:.3f} (um)')
    print(f'-- [STD of Circumference]  \t{std_circumf_um:.3f} (um)')
    print(f'-- [Average CSAR]          \t{avg_csar:.3f} (no unit)')
    print(f'-- [STD of CSAR]           \t{std_csar:.3f} (no unit)')
    print(f'-- [Average Bkdg Noise]    \t{avg_bkgd_pixel:.3f} (no unit)')
    print(f'-- [STD of Bkdg Noise]     \t{std_bkgd_pixel:.3f} (no unit)')
    
    #[14] Collect data into lists.
    list_pct_black.append(pct_black)
    list_pct_white.append(pct_white)
    list_cnt_seg.append(cnt_seg_success)
    list_nd_per_sqnm.append(nucle_dsty_psqum)
    list_avg_gs_squm.append(avg_gs_squm)
    list_std_gs_squm.append(std_gs_squm)
    list_avg_circumf_um.append(avg_circumf_um)
    list_std_circumf_um.append(std_circumf_um)
    list_avg_csar.append(avg_csar)
    list_std_csar.append(std_csar)
    list_avg_bkgd_pixel.append(avg_bkgd_pixel)
    list_std_bkgd_pixel.append(std_bkgd_pixel)
    
#[5] Create df_segs.
df_scale = pd.DataFrame({'bsns': list_bsns
                        ,'sclbar_text': list_sclbar_text
                        ,'pixel_length_sclbar': list_pixel_length_sclbar
                        ,'pixels_per_um': list_pixels_per_um_norm
                        ,'pct_black': list_pct_black
                        ,'pct_white': list_pct_white
                        ,'cnt_seg_success': list_cnt_seg
                        ,'nd_per_sqnm': list_nd_per_sqnm
                        ,'avg_gs_squm': list_avg_gs_squm
                        ,'std_gs_squm': list_std_gs_squm
                        ,'avg_circumf_um': list_avg_circumf_um
                        ,'std_circumf_um': list_std_circumf_um
                        ,'avg_csar': list_avg_csar
                        ,'std_csar': list_std_csar
                        ,'avg_bkgd_pixel': list_avg_bkgd_pixel
                        ,'std_bkgd_pixel': list_std_bkgd_pixel})

#[15] Save scale result.
sheet_name = '03_Stat'
M1UTIL.save_df_as_excel_overwrite(df_scale, path_scale_xlsx, sheet_name)
M1UTIL.adjust_multiple_column_widths(path_scale_xlsx, sheet_name
                                     , ['B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q']
                                     , [ 10, 10, 15, 15, 15, 15, 10, 15, 15, 15, 15, 15, 15, 15, 15, 15])
M1UTIL.adjust_multiple_column_to_pct(path_scale_xlsx, sheet_name, ['F', 'G'])

#[12] Add image process setting info into excel.
text_setting = f'ratio_magnify\t{ratio_magnify}\n'\
                f'prep_use_MB\t{prep_use_MB}\n'\
                f'prep_blur_k\t{prep_blur_k}\n'\
                f'prep_enh_cliplmt\t{prep_enh_cliplmt}\n'\
                f'prep_enh_tileGrid\t{prep_enh_tileGrid}\n'\
                f'cvrg_spl_rt\t{cvrg_spl_rt}\n'\
                f'morph_k\t{morph_k}\n'\
                f'cvrg_spl_rt\t{cvrg_spl_rt}\n'\
                f'dt_mask\t{dt_mask}\n'\
                f'dt_blur_k\t{dt_blur_k}\n'\
                f'dt_enh_cliplmt\t{dt_enh_cliplmt}\n'\
                f'dt_enh_tileGrid\t{dt_enh_tileGrid}\n'\
                f'lm_gbk\t{lm_gbk}\n'\
                f'lm_wdk\t{lm_wdk}\n'\
                f'lm_wds\t{lm_wds}\n'\
                f'lm_pad\t{lm_pad}\n'\
                f'lm_edge\t{lm_edge}\n'\
                f'lm_cr\t{lm_cr}\n'\
                f'lm_mark_original\t{lm_mark_original}\n'\
                f'frgd_thrs_ratio\t{frgd_thrs_ratio}\n'\
                f'frgd_GB_k\t{frgd_GB_k}\n'\
                f'edge_pixel\t{edge_pixel}\n'\
                f'font_size\t{font_size}\n'\
                f'r_seg_area_lim_lu\t{r_seg_area_lim_lu}\n'
M1UTIL.add_text_after_the_last_row_in_an_excel_sheet(path_scale_xlsx, sheet_name, text_setting, row_gap=2, col='B')

print('\nCompleted. Close in 5 seconds.')
time.sleep(5)









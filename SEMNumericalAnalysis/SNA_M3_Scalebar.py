"""
[Module_1_Blank_Module_One.py]
Purpose: 
Author: Meng-Chi Ed Chen
Date: 
Reference:
    1.
    2.

Status: Working.
"""
import os, sys, cv2, re
import numpy as np
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt


from SEMNumericalAnalysis import SNA_M1_Utility as M1UTIL
from SEMNumericalAnalysis import SNA_M2_Image as M2IMG



#[6] Extraction image process - Start

def trim_off_white_edges_of_arrimg(arrimg, white_tolerance=5, smooth_k=2, edge_pixel=1):
    # [1] Compute row and column mean with smoothing
    if len(arrimg.shape) == 3:  # Ensure grayscale.
        return cv2.cvtColor(arrimg, cv2.COLOR_BGR2GRAY)
    _, arrimg = cv2.threshold(arrimg, 127, 255, cv2.THRESH_BINARY)
    col_mean = np.mean(arrimg, axis=0)
    row_mean = np.mean(arrimg, axis=1)
    print(f'col_mean: {col_mean}')
    col_smooth = np.convolve(col_mean, np.ones(smooth_k) / smooth_k, mode='valid')
    row_smooth = np.convolve(row_mean, np.ones(smooth_k) / smooth_k, mode='valid')
    white_val = np.max([col_smooth.max(), row_smooth.max()]) - white_tolerance
    
    # [2] Initialize boundaries
    top_row, bottom_row = 0, arrimg.shape[0]
    left_col, right_col = 0, arrimg.shape[1]
    
    # [3] Find left column boundary
    for i, val in enumerate(col_smooth):
        if val < white_val:
            left_col = i
            break
    
    # [4] Find right column boundary
    for i, val in enumerate(reversed(col_smooth)):
        if val < white_val:
            right_col = arrimg.shape[1] - i - 1
            break
    
    # [5] Find top row boundary
    for i, val in enumerate(row_smooth):
        if val < white_val:
            top_row = i
            break
    
    # [6] Find bottom row boundary
    for i, val in enumerate(reversed(row_smooth)):
        if val < white_val:
            bottom_row = arrimg.shape[0] - i - 1
            break
    
    # [7] Trim and add edge padding if needed
    trimmed_img = arrimg[top_row:bottom_row+1, left_col:right_col+1]
    if edge_pixel > 0:
        trimmed_img = cv2.copyMakeBorder(trimmed_img, edge_pixel, edge_pixel, edge_pixel, edge_pixel, cv2.BORDER_CONSTANT, value=255)
    
    return trimmed_img



def img_enlarge_and_enhance(arrimg, scale_factor=2, GB_k=5, cliplmt=2.0, tileGrid=8):
    # [1] Enlarge the image using interpolation
    height, width = arrimg.shape[:2]
    enlarged_img = cv2.resize(
        arrimg, 
        (int(width * scale_factor), int(height * scale_factor)), 
        interpolation=cv2.INTER_CUBIC)
    #[2] Blur image.
    enlarged_img = cv2.GaussianBlur(enlarged_img, (GB_k, GB_k), 0)
    
    # [2] Enhance the image contrast using CLAHE
    if len(enlarged_img.shape) == 2:  # Grayscale image
        clahe = cv2.createCLAHE(clipLimit=cliplmt, tileGridSize=(tileGrid, tileGrid))
        enhanced_img = clahe.apply(enlarged_img)
    elif len(enlarged_img.shape) == 3:  # Color image
        lab = cv2.cvtColor(enlarged_img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=cliplmt, tileGridSize=(tileGrid, tileGrid))
        l = clahe.apply(l)
        enhanced_img = cv2.merge((l, a, b))
        enhanced_img = cv2.cvtColor(enhanced_img, cv2.COLOR_LAB2BGR)
    else:
        raise ValueError("Unsupported image format. Ensure the image is grayscale or color.")

    return enhanced_img


def add_pixel_around_the_four_edges(arrimg, edge_pixel=1):
    if len(arrimg.shape) == 3:  # Color image
        h, w, c = arrimg.shape
        white_row = np.ones((edge_pixel, w, c), dtype=arrimg.dtype) * 255  # Rows of white pixels
        white_col = np.ones((h + 2 * edge_pixel, edge_pixel, c), dtype=arrimg.dtype) * 255  # Columns of white pixels
    else:  # Grayscale image
        h, w = arrimg.shape
        white_row = np.ones((edge_pixel, w), dtype=arrimg.dtype) * 255  # Rows of white pixels
        white_col = np.ones((h + 2 * edge_pixel, edge_pixel), dtype=arrimg.dtype) * 255  # Columns of white pixels

    #[1] Add white rows at the top and bottom
    arrimg = np.vstack((white_row, arrimg, white_row))

    #[3] Add white columns on the left and right
    arrimg = np.hstack((white_col, arrimg, white_col))

    return arrimg

def rotate_image_clockwise(arrimg, degree, white_edge=3):
    # [1] Get image dimensions
    height, width = arrimg.shape[:2]
    # [2] Compute the rotation matrix
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, -degree, 1.0)
    # [3] Perform the rotation
    rotated_img = cv2.warpAffine(arrimg, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    # [4] Force white_edge number of pixels at the edge to be white
    rotated_img[:white_edge, :] = 255  # Top edge
    rotated_img[-white_edge:, :] = 255  # Bottom edge
    rotated_img[:, :white_edge] = 255  # Left edge
    rotated_img[:, -white_edge:] = 255  # Right edge
    return rotated_img
#[6] Extraction image process - End






#[7] Extract - Start

def find_second_group_of_white_row_or_col_idx(path_img
                                              , gray_img
                                              , along_col_find_row_idx=True
                                              , smooth_k=5
                                              , white_tolerence=1
                                              , delay_stop=5
                                              , print_msg=False
                                              , plot_graph=False):
    bsn_ext = os.path.basename(path_img)
    print(f'\n[find_second_group_of_white_row_or_col_idx] {bsn_ext}')
    
    #[1] Check if the image is grayscale.
    if len(gray_img.shape) >= 3:
        raise ValueError('Input image should be grayscale.')
    _, binary_img = cv2.threshold(gray_img, 240, 255, cv2.THRESH_BINARY)
    
    #[2] Along row or column?
    if along_col_find_row_idx:
        idx_axis = 0
        mean_axis = 1
        text_dir = 'Row-wise'
    else:
        idx_axis = 1
        mean_axis = 0
        text_dir = 'Column-wise'

    #[3] Calculate mean along axis.
    if binary_img is None:
        raise ValueError(f'Please make sure {bsn_ext} have scalebar to be extracted.')
    arr_mean = np.mean(binary_img, axis=mean_axis).astype(int)
    arr_smooth = np.convolve(arr_mean, np.ones(smooth_k)/smooth_k, mode='valid')
    
    #[4] Show a plot with x as index and y as arr_row_mean
    if plot_graph:
        plt.figure(figsize=(15, 5)) 
        plt.plot(np.arange(len(arr_mean)), arr_mean, color='black', label='Mean', linewidth=1)
        plt.plot(np.arange(len(arr_smooth)), arr_smooth, color='blue', label='Smoothed Mean', linewidth=1)
        plt.title(f'{text_dir} Mean Values of {bsn_ext}', fontsize=16)
        plt.xlabel('Row Index', fontsize=14)
        plt.ylabel('Mean Pixel Value', fontsize=14)
        #plt.axvline(x=idx_diff_max, color='r', linestyle='--', label='Diff Max', linewidth=0.5)
        #plt.axvline(x=idx_diff_min, color='r', linestyle='--', label='Diff Min', linewidth=0.5)
        plt.legend()
        dir_bsn, ext = os.path.splitext(path_img)
        path_save = f'{dir_bsn}_2-col mean{ext}'
        plt.savefig(path_save)
    
    #[5] Find the second group of white columns.
    white_val = np.max(arr_smooth) - white_tolerence
    s1_reached_1st_white_group = False 
    s2_reached_1st_black_group = False
    s3_reached_2nd_white_group = False
    cnt_reached_2nd_white_group = 0
    idx_1st_white = None
    idx_2nd_white= None
    print(f'-- white_val: {white_val}')
    for i, iter_mean_axis in enumerate(arr_smooth):
        
        #[6] First group should be white columns.
        if iter_mean_axis > white_val and s2_reached_1st_black_group is False:
            s1_reached_1st_white_group = True 
            if print_msg:
                print(f'[(pos, val) = ({i:03d}, {iter_mean_axis:.2f})] s1_reached_1st_white_group.')
            if not idx_1st_white:
                idx_1st_white = i
        
        #[7] Second gourp should be black columns.
        elif iter_mean_axis < white_val and s1_reached_1st_white_group is True:
            s2_reached_1st_black_group = True
            if print_msg:
                print(f'[(pos, val) = ({i:03d}, {iter_mean_axis:.2f})] s2_reached_1st_black_group.')
        
        #[8] Found second group of white columns.  
        elif iter_mean_axis > white_val and s2_reached_1st_black_group is True:
            idx_2nd_white = i
            cnt_reached_2nd_white_group += 1
            s3_reached_2nd_white_group = True
            if print_msg:
                print(f'[(pos, val) = ({i:03d}, {iter_mean_axis:.2f})] s3_reached_2nd_white_group.')
            if cnt_reached_2nd_white_group > delay_stop:
                break
    
    #[9] If fail to locate scale bar.
    if idx_1st_white is None or idx_2nd_white is None:
        raise ValueError(f'\n Failed to locate scalebar, please check the image. (idx_1st_white={idx_1st_white}; idx_2nd_white={idx_2nd_white})')
    return idx_1st_white, idx_2nd_white









def plot_row_wise_mean_value(arr_row_mean, arr_row_diff, idx_diff_max, idx_diff_min, path_img):

    #[4] Show a plot with x as index and y as arr_row_mean
    plt.figure(figsize=(10, 3)) 
    plt.plot(np.arange(len(arr_row_mean)), arr_row_mean, color='black', label='Mean', linewidth=1)
    plt.plot(np.arange(len(arr_row_diff)), arr_row_diff, color='blue', label='Diif of Mean', linewidth=1)
    plt.title('Row-wise Mean Values of Grayscale Image', fontsize=16)
    plt.xlabel('Row Index', fontsize=14)
    plt.ylabel('Mean Pixel Value', fontsize=14)
    plt.ylim(-260, 260)
    plt.axvline(x=idx_diff_max, color='r', linestyle='--', label='Diff Max', linewidth=0.5)
    plt.axvline(x=idx_diff_min, color='r', linestyle='--', label='Diff Min', linewidth=0.5)
    plt.legend()
    dir_bsn, ext = os.path.splitext(path_img)
    path_save = f'{dir_bsn}_1-row mean{ext}'
    plt.savefig(path_save)








def extract_scale_mark_in_image(path_img, tag_scle='8-scal', plot_graph=False, print_msg=False, save_img=False):
    #[1] Image dir and bsn
    arrimg = cv2.imread(path_img)
    dir_img = os.path.dirname(path_img)
    bsn_ext = os.path.basename(path_img)
    print(f'\n[extract_scale_mark_in_image] Processing: {bsn_ext}')
    
    #[2] Convert to grayscale and compute row-wise mean.
    gray_img = cv2.cvtColor(arrimg, cv2.COLOR_BGR2GRAY)
    h, w = gray_img.shape
    arr_row_mean = np.mean(gray_img, axis=1) 
    arr_row_diff = np.diff(arr_row_mean)
    
    #[3] Find the row with largest color change.
    idx_diff_max = np.argmax(arr_row_diff)
    idx_diff_min = np.argmin(arr_row_diff) 
    if print_msg:
        print(f'-- Diff Max: {idx_diff_max}, \t value: {np.max(arr_row_diff)}.')
        print(f'-- Diff Min: {idx_diff_min}, \t value: {np.min(arr_row_diff)}.')
        
    #[4] First cut: horizontal.
    arrimg_scal = gray_img[idx_diff_max + 1:idx_diff_min - 1, :]
    if plot_graph:
        plot_row_wise_mean_value(arr_row_mean, arr_row_diff, idx_diff_max, idx_diff_min, path_img)

    #[5] Find the second group of white columns.

    idx_1st_white,  idx_2nd_white = find_second_group_of_white_row_or_col_idx(path_img
                                                                                , arrimg_scal
                                                                                , along_col_find_row_idx=False
                                                                                , smooth_k=5
                                                                                , white_tolerence=1
                                                                                , delay_stop=5
                                                                                , print_msg=False
                                                                                , plot_graph=False)
    
    #[7] Second cut: vertical.
    arrimg_scal = arrimg_scal[:, idx_1st_white:idx_2nd_white]

    #[28] Save the processed image.
    if save_img:
        path_img_scal = M2IMG.replace_pattern_in_filename_and_save(dir_img, bsn_ext, tag_scle, arrimg_scal)
        print(f'-- Processed image saved at {path_img_scal}')
    else:
        path_img_scal = M2IMG.replace_pattern_in_filename_and_save(dir_img, bsn_ext, tag_scle, None)
    
    return path_img_scal, arrimg_scal



def check_if_valid_bar_is_found(gray_img, scale_bar_adj, bsn_ext):
    #[6] Compute col mean, remove element larger than 250, and compute length.
    arr_col_mean = np.mean(gray_img, axis=0).astype(int)
    valid_cols = np.where(arr_col_mean < 180)[0]
    if valid_cols.size > 0:
        pixel_length_sclbar = valid_cols[-1] - valid_cols[0] + scale_bar_adj
    else:
        pixel_length_sclbar = 0  # No valid scale bar found
        print(f'\n-- No valid scale bar found for {bsn_ext}.')
        
        
def correct_italic_text_image(arrimg):
    #[1] Find the most right non-white column
    _, arrimg = cv2.threshold(arrimg, 127, 255, cv2.THRESH_BINARY)
    non_white_columns = np.where(arrimg < 255)[1]
    if len(non_white_columns) == 0:
        return arrimg  # If no non-white pixels, return original image
    right_most_col = non_white_columns.max()
    #[2] Count from top to bottom. At the place where black turned white,
    h, w = arrimg.shape
    for row in range(h):
        #[3] Check transition from black (0) to white (255) within the right-most column
        if (arrimg[row, right_most_col] < 255) \
            and (row + 1 < h) \
            and (arrimg[row + 1, right_most_col] == 255)\
            and (arrimg[row + 1, right_most_col - 1] != 255):       # Make sure it's not the end of "m".
            #[5] Shift remaining part below this row to the right by 1 pixel
            arrimg[row+1:, 1:] = arrimg[row+1:, :-1] 
            arrimg[row+1:, 0] = 255
            break
    arrimg_adj = arrimg[:, :-1]  # Crop extra pixel on the right
    return arrimg_adj

def read_scalebar_sample_images_into_list_of_arries(dir_sample):
    print('\n[read_scalebar_sample_images_into_list_of_arries]')
    list_paths_sample, list_bsns_sample \
        = M1UTIL.filter_file_in_dir_with_keywords(dir_sample, ['.jpg'], [], False)
    list_sbar_samples, list_sbar_text = [], []
    for i, i_path_sample in enumerate(list_paths_sample):
        # [11] Read the image, trim, and overwrite
        arr_sample = cv2.imread(i_path_sample, cv2.IMREAD_GRAYSCALE)
        _, arr_sample = cv2.threshold(arr_sample, 127, 255, cv2.THRESH_BINARY)
        list_sbar_samples.append(arr_sample) 
        #[12] Get sbar_text from "[500nm]B619_center_00_(9-sbar-1).jpg" to "500nm".
        sbar_text = list_bsns_sample[i].split(']')[0].replace('[', '')
        list_sbar_text.append(sbar_text)
        
    print(f'Read all {len(list_sbar_samples)} scalebar sample images into list of arraies.\n{list_sbar_text}')
    return list_sbar_samples, list_sbar_text





def image_matching_original(arr_check, arr_sample, diff_tolerance):
    h_sam, w_sam = arr_sample.shape[:2]
    h_chk, w_chk = arr_check.shape[:2]
    h_diff = h_chk - h_sam
    w_diff = w_chk - w_sam
    #[1] Ensure arr_sample fits within arr_check
    if h_diff < 0 or w_diff < 0 or h_diff > 10:
        print(f'\t Size differes too much, skip. h_diff = {h_diff}, w_diff = {w_diff}.')
        return False
    else:
        print()
    #[2] Initialize arr_diff to store differences
    arr_diff = np.full((h_chk - h_sam + 1, w_chk - w_sam + 1), np.inf, dtype=np.float32)
    
    #[2] Slide arr_sample over arr_check
    for y in range(h_chk - h_sam + 1):  # Vertical sliding
        for x in range(w_chk - w_sam + 1):  # Horizontal sliding
            #[3] Extract the corresponding region from arr_check
            region = arr_check[y:y + h_sam, x:x + w_sam]

            #[4] Calculate absolute difference
            abs_diff = np.average(np.abs(region.astype(np.float32) - arr_sample.astype(np.float32)))
            arr_diff[y, x] = round(abs_diff, 2)

    #[5] Check if the minimum of arr_diff is within the tolerance
    print(f'[arr_diff]\n{arr_diff}')
    if np.min(arr_diff) <= diff_tolerance:
        print(f'-- The minimum in arr_diff is less than diff_tolerance {diff_tolerance}.')
        return True
    return False


def image_matching_with_cv2(arr_check, arr_sample, similarity_thr=0.9):
    h_sam, w_sam = arr_sample.shape[:2]
    h_chk, w_chk = arr_check.shape[:2]
    h_diff = h_chk - h_sam
    w_diff = w_chk - w_sam

    #[1] Ensure arr_sample fits within arr_check
    if h_diff < 0 or w_diff < 0 or h_diff > 10:
        print(f'\t Size differs too much, skip. h_diff = {h_diff}, w_diff = {w_diff}.')
        return False

    #[2] Perform template matching using cv2.matchTemplate
    result = cv2.matchTemplate(arr_check, arr_sample, cv2.TM_CCOEFF_NORMED)

    #[3] Find the best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    #[5] Check if the best match exceeds the threshold
    if max_val >= similarity_thr:
        print(f'\t Match found with similarity {max_val:.2f} (similarity_thr = {similarity_thr}).')
        return True
    else:
        print(f'\t No sufficient match found. Best similarity = {max_val:.2f}, similarity_thr = {similarity_thr}.')
        return False


def identify_scalebar_text(arr_sbar_1_text, list_sbar_samples, list_sbar_text, similarity_thr):
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    #[5] Additional image preparation.
    arr_sbar_1_text = trim_off_white_edges_of_arrimg(arr_sbar_1_text, 5, smooth_k=3, edge_pixel=1)
    
    #[6] Compare with known scalebar example bank.
    for i, i_sbar_samples in enumerate(list_sbar_samples):
        print(f'-- [{i}] Checking with sample {list_sbar_text[i]}', end='')
        #[5] Read sample image. (Keep these comments.)
        #if image_matching_original(arr_sbar_1_text, i_sbar_samples, diff_tolerance):
        if image_matching_with_cv2(arr_sbar_1_text, i_sbar_samples, similarity_thr):
            sclbar_text = list_sbar_text[i]
            print(f'-- Found match with {sclbar_text} via comparison.')
            return sclbar_text
        
    #[7] Identify if sample cannot be found.
    print(f'-- Failed to found text using comparision. Now use OCR.')
    sclbar_text = None
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789µunm'
    sclbar_text = pytesseract.image_to_string(arr_sbar_1_text, config=custom_config).rstrip('\n').rstrip('\n')
    print(f'-- OCR result return {sclbar_text}')
    
    return sclbar_text



def extract_scale_bar_only_and_measure_length(path_img, dir_scalebars, tag_scle='9-sbar', scale_bar_adj=-1, 
                                              plot_graph=False, print_msg=False, save_img=False):
    
    
    #[1] Image dir and bsn.
    arrimg = cv2.imread(path_img)
    dir_img = os.path.dirname(path_img)
    bsn_ext = os.path.basename(path_img)
    print(f'\n[extract_scale_bar_only_and_measure_length] Processing: {bsn_ext}')

    #[2] Convert to grayscale and calculate row-wise mean
    gray_img = cv2.cvtColor(arrimg, cv2.COLOR_BGR2GRAY)
    idx_1st_white,  idx_2nd_white = find_second_group_of_white_row_or_col_idx(path_img
                                                                                , gray_img
                                                                                , along_col_find_row_idx=True
                                                                                , smooth_k=2
                                                                                , white_tolerence=12
                                                                                , delay_stop=1
                                                                                , print_msg=print_msg
                                                                                , plot_graph=plot_graph)
    
    #[4] Additional image processing.
    arr_sbar_1_text = gray_img[idx_1st_white: idx_2nd_white, :] 
    arr_sbar_2_ruler = gray_img[idx_2nd_white:, :]  # Ruler of scale bar.
    arr_sbar_2_ruler = trim_off_white_edges_of_arrimg(arr_sbar_2_ruler, 5, smooth_k=3, edge_pixel=5)
    check_if_valid_bar_is_found(gray_img, scale_bar_adj, bsn_ext)

    
    #[8] Scale image and extract text.
    sclbar_text = identify_scalebar_text(arr_sbar_1_text, dir_scalebars)

    #[10] Save the processed image of the scale bar
    if save_img:
        replace_pattern_in_filename_and_save(dir_img, bsn_ext, f'{tag_scle}-1', arr_sbar_1_text)
        #replace_pattern_in_filename_and_save(dir_img, bsn_ext, f'{tag_scle}-2', arr_sbar_2_ruler)
        
    """#[12] Check scale bar text
    print(f'\n-- Scale bar = {pixel_length_sclbar} pixel for {sclbar_text}.\n')
    sclbar_digits = ("".join(filter(str.isdigit, sclbar_text))).strip()
    if sclbar_digits == '':
        raise ValueError (f'-- Could not extract a valid info from sclbar_text: {sclbar_text}')"""
    return pixel_length_sclbar, sclbar_text
    

def turn_text_and_pixel_into_pixels_per_um(pixel_length_sclbar, sclbar_text):
    """
    Convert the pixel length of the scale bar into pixels per micrometer (um).
    - pixel_length_sclbar (int): Length of the scale bar in pixels.
    - sclbar_text (str): Text on the scale bar indicating the physical length, e.g., '100 nm' or '1 um'.
    """
    
    #[1] Extract numeric value and unit from the scale bar text
    sclbar_text = sclbar_text.strip().lower()
    try:
        sclbar_value = float(''.join([c for c in sclbar_text if c.isdigit() or c == '.']))
    except ValueError:
        raise ValueError(f'Could not extract a valid number from scale bar text: {sclbar_text}')
    
    #[2] Determine unit and convert accordingly
    if 'nm' in sclbar_text:
        pixels_per_um = (pixel_length_sclbar * 1000) / sclbar_value
    elif 'um' or 'µm' in sclbar_text:
        pixels_per_um = pixel_length_sclbar / sclbar_value
    else:
        raise ValueError(f'Invalid unit in scale bar text: {sclbar_text}. Expected "nm" or "um".')
    
    return pixels_per_um











def add_text_to_image(path_image, text, font_size=1, font_thk_int=3, pos_x=0, pos_y=0):
    #[2] Add text to the image
    arrimg = cv2.imread(path_image)
    arr_img_text = cv2.putText(
        arrimg.copy(),                  # Image to draw on
        str(text),                   # The number to draw
        (pos_x, pos_y),           # Position to draw the number
        cv2.FONT_HERSHEY_SIMPLEX,       # Font type
        font_size,                      # Font scale (adjusted for better sizing)
        [240, 150, 50],                # Color (255 for white in grayscale)
        thickness=font_thk_int,                    # Thickness of the text (must be integer)
        lineType=cv2.LINE_AA            # Anti-aliased line
    )
    cv2.imwrite(path_image, arr_img_text)
    
    return arr_img_text



#[7] Extract - End


"""
    #[5] Additional image preparation.
    #arr_sbar_1_text = correct_italic_text_image(arr_sbar_1_text)
    #arr_sbar_1_text = add_pixel_around_the_four_edges(arr_sbar_1_text, 3)
    arr_sbar_1_text = trim_off_white_edges_of_arrimg(arr_sbar_1_text, 5, smooth_k=3, edge_pixel=1)
    #arr_sbar_1_text = rotate_image_clockwise(arr_sbar_1_text, -6, 3)
    #arr_sbar_1_text = img_enlarge_and_enhance(arr_sbar_1_text, 5, 7, 2, 8)

"""

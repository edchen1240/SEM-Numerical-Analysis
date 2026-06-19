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




def replace_pattern_in_filename_and_save(dir_img, bsn_ext, new_tag, arrimg=None):
    """
    Replace the _(*). pattern in the filename with a new tag.
    If pattern cannot be found, add f'_{new_tag}' just before the file ext.
    """
    #[1] Split the base name and extension
    bsn, ext = os.path.splitext(bsn_ext)
    
    #[2] Regular expression to match the _(*) pattern
    pattern = r'\_\([^)]+\)$'  # This matches _ followed by ( and any characters except ) until ) at the end
    
    #[3] Check if the pattern exists and is properly formatted
    match = re.search(pattern, bsn)
    if match:
        #[4] Replace the matched pattern with the new tag
        new_bsn_ext = f'{re.sub(pattern, f"_({new_tag})", bsn)}{ext}'
    else:
        #[5] Append the new tag if pattern is not found
        new_bsn_ext = f'{bsn}_({new_tag}){ext}'
    
    #[8] Save image.
    path_img = os.path.join(dir_img, new_bsn_ext)
    if arrimg is not None:
        cv2.imwrite(path_img, arrimg)

    return path_img




def quick_binary_smoothing(arrimg_inpt, ksize=5):
    """
    Apply Gaussian blur and then Otsu's thresholding to binarize the image.
    """
    #[1] Blur the input image
    arrimg_inpt_blur = cv2.GaussianBlur(arrimg_inpt, (ksize, ksize), 0)
    
    #[2] Ensure the image is in the correct type (8-bit unsigned) for thresholding
    if arrimg_inpt_blur.dtype != 'uint8':
        arrimg_inpt_blur = cv2.normalize(arrimg_inpt_blur, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
    
    #[3] Binarize the image using Otsu's thresholding
    otsu_threshold, arrimg_oupt = \
        cv2.threshold(arrimg_inpt_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    print(f'\n[quick_binary_smoothing] otsu_threshold: {otsu_threshold}')

    return arrimg_oupt






#[1] Image Resizing - Start


def crop_image_center_square(path_img, 
                             cvt_grayscale=True,
                             tag_crop='1-crop', length=500):
    """
    Crop an image centered at the center into a square.
    """
   
    #[1] Validate the length.
    length = int(length)
    
    #[2] Load the image.
    arr_img = cv2.imread(path_img)
    dir_img = os.path.dirname(path_img)
    bsn_ext = os.path.basename(path_img)
    print(f'\n[crop_image_center_square] Processing image: {bsn_ext}')
    
    #[3] Check if image exist.
    if arr_img is None:
        raise FileNotFoundError(f"Image at {path_img} could not be loaded.")
    
    #[4] Convert to grayscale.
    if cvt_grayscale:
        arrimg = cv2.imread(path_img)
        arrimg = cv2.cvtColor(arrimg, cv2.COLOR_BGR2GRAY)
    
    #[6] Get image dimensions.
    h, w = arr_img.shape[:2]
    smaller_side = min(h, w)
    
    #[7] Check if length is valid.
    if length > smaller_side:
        raise ValueError(f'Provided length ({length}) exceeds the smaller side ({smaller_side}) of the image.')
    
    #[8] Calculate crop coordinates.
    shift_w = (w - length) // 2
    shift_h = (h - length) // 2
    
    #[9] Crop the image to the center square.
    arrimg_1crop = arr_img[shift_h:shift_h + length, shift_w:shift_w + length]
    
    #[10] Save the cropped image.
    path_img_1crop = replace_pattern_in_filename_and_save(dir_img, bsn_ext, tag_crop, arrimg_1crop)
    print(f'[crop_image_center_square] Cropped image saved at {path_img_1crop}')
    return path_img_1crop, arrimg_1crop



def enlarge_image(path_img, 
                  tag_elrg='2-elrg', ratio_magnify=2):
    """
    Crop an image centered at the center into a square.
    """
   
    #[1] Validate the ratio_magnify.
    ratio_magnify = float(ratio_magnify)
    if ratio_magnify >= 5:
        raise ValueError(f'ratio_magnify ({ratio_magnify}) larger than 5. Might not have good result.')
    
    #[2] Load the image.
    arr_img = cv2.imread(path_img)
    dir_img = os.path.dirname(path_img)
    bsn_ext = os.path.basename(path_img)
    print(f'\n[enlarge_image] Processing image: {bsn_ext}')
    
    #[3] Check if image exist.
    if arr_img is None:
        raise FileNotFoundError(f"Image at {path_img} could not be loaded.")
    
    #[4] Get image dimensions.
    h, w = arr_img.shape[:2]
    
    #[5] Calculate the new dimensions.
    new_h = int(h * ratio_magnify)
    new_w = int(w * ratio_magnify)
    
    #[6] Resize the image using the new dimensions.
    arrimg_2elrg = cv2.resize(arr_img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    #[7] Save the enlarged image.
    path_img_2elrg = replace_pattern_in_filename_and_save(dir_img, bsn_ext, tag_elrg, arrimg_2elrg)
    print(f'[enlarge_image] Enlarged image saved at {path_img_2elrg}')
    
    return path_img_2elrg, arrimg_2elrg



#[1] Image Resizing - End

















# [2] Coverage - Start


def plot_intensity_histogram_for_grayscale_image(path_img, 
                                                 tag_previous=None, 
                                                 tag_binary='5-binary', 
                                                 tag_hist='6-histg', 
                                                 cvrg_spl_rt=0.1):
    
    #[3] Set directories and extract base names
    dir_img = os.path.dirname(path_img)
    bsn_ext = os.path.basename(path_img)
    bsn, ext = os.path.splitext(bsn_ext)
    bsn_original = bsn.replace(tag_previous, '')

    #[5] Status report.
    print(f'\n[plot_intensity_histogram_for_grayscale_image] {bsn_ext}')
    
    #[20] Collect text on plot and save plot. (Color was inverted here.)
    #path_histg = replace_pattern_in_filename_and_save(dir_img, bsn_ext, tag_hist, None)
    otsu_threshold, path_img_5bnrz, arrimg_5bnrz, path_histg, list_coverage_info\
        = create_histogram_plot(path_img, cvrg_spl_rt, 
                                tag_binary='5-binary', 
                                tag_hist='6-histg')
    
    #return otsu_threshold, [h, w], [cpsd_w, cpsd_h], pct_black, pct_white
    return otsu_threshold, path_img_5bnrz, arrimg_5bnrz, path_histg, list_coverage_info


def create_histogram_plot(path_img, cvrg_spl_rt, 
                            tag_binary='5-binary', 
                            tag_hist='6-histg'):
    
    #[1] Image size and resize
    arrimg = cv2.imread(path_img)
    arrimg = cv2.cvtColor(arrimg, cv2.COLOR_BGR2GRAY)
    if len(arrimg.shape) != 2:
        raise ValueError("Input array must be a grayscale image.")
    h, w = arrimg.shape
    cnt_pixel = h * w
    
    #[2] Resize the image (cpsd = compresed, cvrg_spl_rt = coverage sampling ratio.)
    cpsd_w, cpsd_h = int(w * cvrg_spl_rt), int(h * cvrg_spl_rt)
    arrimg_reduced = cv2.resize(arrimg, (cpsd_w, cpsd_h), interpolation=cv2.INTER_NEAREST)
    cpsd_w, cpsd_h = arrimg_reduced.shape
    cnt_pixel_reduced = cpsd_w * cpsd_h
    if cnt_pixel_reduced > 20000:
        raise ValueError(f'Pixel count is currently {cnt_pixel_reduced}. Consider keeping it less than 10000 before making intensity histogram.')
    
    #[3] Set directories and extract base names
    dir_img = os.path.dirname(path_img)
    bsn_ext = os.path.basename(path_img)
        
    #[4] Binerize image (color was inverted here in the function "binerize_image".)
    path_img_5bnrz, arrimg_5bnrz, otsu_threshold = binerize_image(path_img, tag_binary, True)
        
    #[5] Calculate histogram
    arr_histg = cv2.calcHist([arrimg_reduced], [0], None, [256], [0, 256])[:, 0]
    
    #[6] Separate histogram for black and white regions and population
    arr_histg_black = arr_histg[:otsu_threshold+1] # This is correct. The index count from 0 not 1.
    arr_histg_white = arr_histg[otsu_threshold+1:]
    pct_black, pct_white = sum(arr_histg_black)/cnt_pixel_reduced, sum(arr_histg_white)/cnt_pixel_reduced
    
    #[8] Pack info
    list_coverage_info = [h, w], [cpsd_w, cpsd_h], pct_black, pct_white
    
    #[10] Add additional text on plot.
    text_on_plot =  f'{bsn_ext}, {h}x{w} = {cnt_pixel} pixels\n'\
                    f'Sampling rate: {cvrg_spl_rt*100:.2f}%, {cpsd_h}x{cpsd_w} = {cnt_pixel_reduced} pixels\n'\
                    f'Threshold: {otsu_threshold}\n'\
                    f'Population (black, white): {pct_black*100:.0f}%, {pct_white*100:.0f}%'
    
    #[11] Plot histogram (not curved line). Plot a vertical line at otsu_threshold+0.5.
    fs_title, fs_axis, fs_info = 20, 16, 10
    plt.figure(figsize=(8, 6))
    plt.bar(range(otsu_threshold+1), arr_histg_black, color='dimgray', width=1.0)
    plt.bar(range(otsu_threshold+1, 256), arr_histg_white, color='darkgray', width=1.0)
    plt.axvline(x=otsu_threshold + 0.5, color='gray', linestyle='--')
    plt.title(f'Pixel Intensity Distribution', fontsize = fs_title)
    plt.text(0.02, 0.98, text_on_plot, fontsize=fs_info, ha='left', va='top', transform=plt.gca().transAxes)
    plt.xlabel('Pixel Intensity', fontsize = fs_axis)
    plt.ylabel('Pixel Count', fontsize = fs_axis)
    plt.ylim([0, max(arr_histg)*1.2])
    
    #[13] Save binary image and histogram plot
    #[7] Optionally save arrimg_binary.
    if tag_hist:
        path_histg = replace_pattern_in_filename_and_save(dir_img, bsn_ext, tag_hist, None)
        plt.savefig(path_histg)
    plt.close()
    print(f"Histogram saved at: {path_histg}")
    
    
    return otsu_threshold, path_img_5bnrz, arrimg_5bnrz, path_histg, list_coverage_info

# [2] Coverage - End





#[3] Image Process - Start


#[] boxBlur, gray scale, binary, medianBlur

def quick_GaussianBlur_and_enh_arrimg(arrimg, GB_k=5, enh_cliplmt=2, enh_tileGrid=8):
    """
    Applies Gaussian Blur and CLAHE (Contrast Limited Adaptive Histogram Equalization) to an image.
    Handles both 2-channel grayscale and 3-channel color images.
    
    Parameters:
        arrimg: numpy array, the input image (grayscale or color).
        GB_k: int, kernel size for Gaussian Blur (must be odd).
        enh_cliplmt: float, clip limit for CLAHE.
        enh_tileGrid: int, grid size for CLAHE.

    Returns:
        tuple: (Gaussian blurred image, CLAHE-enhanced image)
    """
    #[1] Apply Gaussian Blur
    arrimg_3gblr = cv2.GaussianBlur(arrimg, (GB_k, GB_k), 0)
    print(f"Blurred image shape: {arrimg_3gblr.shape}")

    #[2] Check if the image is grayscale or color
    if len(arrimg.shape) == 2:  # Grayscale image
        #[3] Ensure type is uint8 for CLAHE
        if arrimg_3gblr.dtype != np.uint8:
            arrimg_3gblr = arrimg_3gblr.astype(np.uint8)

        #[4] Apply CLAHE directly to the blurred grayscale image
        clahe = cv2.createCLAHE(clipLimit=enh_cliplmt, tileGridSize=(enh_tileGrid, enh_tileGrid))
        arrimg_4enhc = clahe.apply(arrimg_3gblr)
        print(f"Grayscale enhanced image shape: {arrimg_4enhc.shape}")
    elif len(arrimg.shape) == 3 and arrimg.shape[2] == 3:  # Color image
        #[6] Convert to LAB color space
        lab = cv2.cvtColor(arrimg_3gblr, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)

        print(f"L-channel type: {l_channel.dtype}, shape: {l_channel.shape}")
        if l_channel.dtype != np.uint8:  # Ensure the data type is uint8
            l_channel = l_channel.astype(np.uint8)

        #[7] Apply CLAHE to the L-channel
        clahe = cv2.createCLAHE(clipLimit=enh_cliplmt, tileGridSize=(enh_tileGrid, enh_tileGrid))
        cl = clahe.apply(l_channel)

        #[8] Merge the CLAHE enhanced L-channel with the original a and b channels
        limg = cv2.merge((cl, a, b))
        arrimg_4enhc = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)  # Convert back to BGR
        print(f"Color enhanced image shape: {arrimg_4enhc.shape}")
    else:
        raise ValueError("Input image must be either grayscale or color (BGR).")

    
    
    
    
    return arrimg_3gblr, arrimg_4enhc

def quick_MedianBlur_and_enh_arrimg(arrimg, medblur_k=5, enh_cliplmt=2, enh_tileGrid=8):
    #[3] MedianBlur image
    arrimg_3mblr = cv2.medianBlur(arrimg, medblur_k)
    
    #[5] Enhance image
    lab = cv2.cvtColor(arrimg_3mblr, cv2.COLOR_BGR2LAB) # Converting to LAB color space
    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=enh_cliplmt, tileGridSize=(enh_tileGrid, enh_tileGrid)) # clipLimit = 2, tileGridSize = 8
    cl = clahe.apply(l_channel)
    limg = cv2.merge((cl, a, b)) # Merge the CLAHE enhanced L-channel with the a and b channel
    arrimg_4enhc = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR) # Converting from LAB Color model to BGR color space
    
    return arrimg_3mblr, arrimg_4enhc

def quick_image_correction_path_img(path_img, use_MB=True,
                           tag_mblr='3-mblr', blur_k=5, 
                           tag_enhc='4-enhc', enh_cliplmt=2, enh_tileGrid=8):
    #[1] Image dir and bsn
    arrimg = cv2.imread(path_img)
    dir_img = os.path.dirname(path_img)
    bsn_ext = os.path.basename(path_img)
    print(f'\n[quick_image_correction_path_img] {bsn_ext}')
    
    #[2] Check if image exist.
    if arrimg is None:
        raise FileNotFoundError(f"Image at {path_img} could not be loaded.")

 
    #[6] Process and save image.
    if use_MB:
        arrimg_3mblr, arrimg_4enhc \
            = quick_MedianBlur_and_enh_arrimg(arrimg, blur_k, enh_cliplmt, enh_tileGrid)
    else:
        arrimg_3mblr, arrimg_4enhc \
            = quick_GaussianBlur_and_enh_arrimg(arrimg, blur_k, enh_cliplmt, enh_tileGrid)
        
    path_img_3mblr = replace_pattern_in_filename_and_save(dir_img, bsn_ext, tag_mblr, arrimg_3mblr)
    path_img_4enhc = replace_pattern_in_filename_and_save(dir_img, bsn_ext, tag_enhc, arrimg_4enhc)

    return path_img_3mblr, path_img_4enhc, arrimg_4enhc




def binerize_image(path_img, tag_bnrz='5-bnrz', invert=True):
    
    #[1] Image dir and bsn
    arr_img = cv2.imread(path_img)
    dir_img = os.path.dirname(path_img)
    bsn_ext = os.path.basename(path_img)
    bsn, ext = os.path.splitext(bsn_ext)
    print(f'\n[binerize_image] Processing: {bsn_ext}')
    
    #[2] Check if image exists.
    if arr_img is None:
        raise FileNotFoundError(f"Image at {path_img} could not be loaded.")
    
    #[4] Ensure the image is in grayscale before performing further operations.
    if len(arr_img.shape) > 2:
        arr_img = cv2.cvtColor(arr_img, cv2.COLOR_BGR2GRAY)
    else:
        arr_img = arr_img  # Image is already single-channel
    
    #[8] Apply Otsu's binarization and get the threshold value
    otsu_threshold, arrimg_5bnrz = cv2.threshold(arr_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    otsu_threshold = round(otsu_threshold)
    
    #[9] Invert the binary image if invert=True
    if invert:
        arrimg_5bnrz = cv2.bitwise_not(arrimg_5bnrz)
    
    #[6] Save processed image.
    path_img_5bnrz = replace_pattern_in_filename_and_save(dir_img, bsn_ext, tag_bnrz, arrimg_5bnrz)
    print(f'[binerize_image] otsu_threshold: {otsu_threshold}. Binerized image saved at {path_img_5bnrz}')
    
    return path_img_5bnrz, arrimg_5bnrz, otsu_threshold




def process_input_path_or_arr_img(input_image):
    #[1] Check if the input is a string (path to an image file)
    if isinstance(input_image, str):
        #[2] Load the image from the given path
        image = cv2.imread(input_image)
        if image is None:
            raise ValueError(f"Could not load image from path: {input_image}")
        print(f'-- The input image is a path in {input_image}.')
    elif isinstance(input_image, np.ndarray):
        #[3] Use the input as it is (already an image array)
        print(f'-- The input image is an {len(input_image)}D array.')
        image = input_image
    else:
        raise TypeError("Input must be a file path (str) or an image array (numpy.ndarray)")

    return image



def mark_local_max_on_dt(path_or_arr_img
                         , lm_gbk, lm_wdk, lm_wds, lm_pad=20, lm_edge=5, lm_cr=5, 
                         lm_mark_original=True):
    """
    lm_gbk: Initial large-k Gaussian blur.
    lm_wdk: Sampling window to find local maxima.
    lm_wds: WIndow stride.
    lm_pad=20: Image padding. Must larger than lm_edge so that edge local maximum can be found.
    lm_edge=5: Do not mark local maximum if it's too close to the edge.
    lm_cr=5: Radius of the circle.
    """
    lm_pad = 20
    lm_edge = 5 # This is important, it removed unwanted double dot.
    lm_cr = 5
        
    #[1] Validate the input image dimensions
    arrimg = process_input_path_or_arr_img(path_or_arr_img)
    if len(arrimg.shape) > 2:
        arrimg = cv2.cvtColor(arrimg, cv2.COLOR_BGR2GRAY)
        print('-- Convert to gray scale.')
        
    #[3] Large k Gaussian blur to remove noise
    arrimg = cv2.GaussianBlur(arrimg, (lm_gbk, lm_gbk), 0)
        
    #[4] Add black lm_pad to the input image
    arrimg = cv2.copyMakeBorder(arrimg, lm_pad, lm_pad, lm_pad, lm_pad, cv2.BORDER_CONSTANT, value=0)

    #[8] Get the shape of the input image
    img_height, img_width = arrimg.shape

    #[10] Create a blank image of the same szie to mark the local maxima.
    if lm_mark_original:
        arrimg_local_max = arrimg.copy()
    else:
        arrimg_local_max = np.zeros_like(arrimg)

    #[11] Iterate through the image with the given window size and stride
    for i in range(0, img_height - lm_wdk + 1, lm_wds):
        for j in range(0, img_width - lm_wdk + 1, lm_wds):
            #[12] Extract the window
            window = arrimg[i:i + lm_wdk, j:j + lm_wdk]
            
            #[14] Find the maximum value. If black, continue next.
            local_max_value = np.max(window)
            if local_max_value == 0:
                continue
            
            #[15] Find its position in the window
            local_max_position = np.unravel_index(np.argmax(window), window.shape)

            #[18] Check if the local maximum is at the edge of the window
            if 0 + lm_edge < local_max_position[0] < lm_wdk - 1  - lm_edge \
                and 0 + lm_edge < local_max_position[1] < lm_wdk - 1 - lm_edge:
                #[19] Draw a white circle at the local maximum position
                center_x = j + local_max_position[1]
                center_y = i + local_max_position[0]
                cv2.circle(arrimg_local_max, (center_x, center_y), lm_cr, 255, -1)
                
    #[20] Remove the lm_pad before returning the result
    arrimg_local_max = arrimg_local_max[lm_pad:-lm_pad, lm_pad:-lm_pad]

    return arrimg_local_max







def watershed_image(path_img,
                    tag_ovlp='6-ovlp',
                    tag_wtsd='7-wtsd',
                    morph_k = 3,
                    dt_mask=5,
                    dt_blur_k=31, 
                    dt_enh_cliplmt=1.5, 
                    dt_enh_tileGrid=10,
                    lm_gbk=51, lm_wdk=100, lm_wds=40, 
                    lm_pad=50, lm_edge=5, lm_cr=5, 
                    lm_mark_original = True,
                    frgd_thrs_ratio = 0.6,
                    frgd_GB_k = 27,
                    save_interm=True,
                    thick_boundary=True):
    
    #[1] Image dir and bsn
    arrimg_inpt = cv2.imread(path_img)
    dir_img = os.path.dirname(path_img)
    bsn_ext = os.path.basename(path_img)
    bsn, ext = os.path.splitext(bsn_ext)
    print(f'\n[watershed_image] Processing: {bsn_ext}')
    
    #[2] Check if image exists.
    if arrimg_inpt is None:
        raise FileNotFoundError(f"Image at {path_img} could not be loaded.")
    
    #[3] Ensure the image is grayscale (single-channel)
    if len(arrimg_inpt.shape) > 2:  # Convert to grayscale if it isn't already
        arrimg_inpt_gray = cv2.cvtColor(arrimg_inpt, cv2.COLOR_BGR2GRAY)
        print(f'\t Input image was not binerized. Changed from {arrimg_inpt.shape} to {arrimg_inpt_gray.shape}.')
    
    #[4] Apply Otsu's binarization if not already binary
    _, arrimg_inpt_gray = cv2.threshold(arrimg_inpt_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    #[5] Perform morphological operations to remove noise and separate touching objects
    kernel = np.ones((morph_k, morph_k), np.uint8)
    arrimg_open = cv2.morphologyEx(arrimg_inpt_gray, cv2.MORPH_OPEN, kernel, iterations=2)

    #[6] Ensure the image is still binary and in uint8 format after morphological operations
    arrimg_open = np.uint8(arrimg_open)
    
    #[7] Dilate the image to enhance segmentation of objects
    arrimg_bkgd = cv2.dilate(arrimg_open, kernel, iterations=3)
    
    #[8] Compute the distance transform
    dist_transform = cv2.distanceTransform(arrimg_open, cv2.DIST_L2, dt_mask)   
    _, dist_transform = quick_GaussianBlur_and_enh_arrimg(dist_transform, 
                                                       dt_blur_k, 
                                                       dt_enh_cliplmt, 
                                                       dt_enh_tileGrid)
    
    #[9] Find local maxima.
    dist_transform = np.float32(dist_transform)
    dist_transform = cv2.normalize(dist_transform, None, 0, 255, cv2.NORM_MINMAX)
    dist_transform = mark_local_max_on_dt(dist_transform
                                      , lm_gbk, lm_wdk, lm_wds, lm_pad, lm_edge, lm_cr
                                      , lm_mark_original)
    
    #[10] and threshold to find the foreground.
    _, arrimg_frgd = cv2.threshold(dist_transform, frgd_thrs_ratio * dist_transform.max(), 255, 0)
    arrimg_frgd = quick_binary_smoothing(arrimg_frgd, frgd_GB_k)
    
    #[11] Ensure foreground is uint8 and define markers.
    arrimg_frgd = np.uint8(arrimg_frgd)
    arrimg_unk = cv2.subtract(arrimg_bkgd, arrimg_frgd)
    
    #[12] Save intermediate images.
    if save_interm: 
        #[13]
        replace_pattern_in_filename_and_save(dir_img, bsn_ext, f'{tag_ovlp}-1b', arrimg_bkgd)
        replace_pattern_in_filename_and_save(dir_img, bsn_ext, f'{tag_ovlp}-2d', dist_transform)
        replace_pattern_in_filename_and_save(dir_img, bsn_ext, f'{tag_ovlp}-3f', arrimg_frgd)
        replace_pattern_in_filename_and_save(dir_img, bsn_ext, f'{tag_ovlp}-4u', arrimg_unk)
        
        #[15] Adjust black-white image to black-gray image.
        arrimg_inpt_gray = np.where(arrimg_inpt_gray == 255, 160, arrimg_inpt_gray)
        arrimg_open_gray = np.where(arrimg_open == 255, 80, arrimg_open)
        arrimg_bkgd_gray = np.where(arrimg_bkgd == 255, 80, arrimg_bkgd)
        arrimg_frgd_gray = np.where(arrimg_frgd == 255, 80, arrimg_frgd)
        
        #[15] Overlap these images together and save.
        print(f'arrimg_inpt_gray: {arrimg_inpt_gray.shape}')
        print(f'arrimg_open_gray: {arrimg_open_gray.shape}')
        print(f'arrimg_bkgd_gray: {arrimg_bkgd_gray.shape}')
        print(f'arrimg_frgd_gray: {arrimg_frgd_gray.shape}')
        arrimg_ovlp = arrimg_inpt_gray - arrimg_open_gray + arrimg_bkgd_gray + arrimg_frgd_gray
        path_img_6wtsd = replace_pattern_in_filename_and_save(dir_img, bsn_ext, f'{tag_ovlp}', arrimg_ovlp)
    
    #[20] Mark the regions of the foreground with different markers.
    _, markers = cv2.connectedComponents(arrimg_frgd)
    
    #[21] Add one to all markers so that the unknown region gets the value 0.
    markers = markers + 1
    markers[arrimg_unk == 255] = 0
    
    #[22] Apply the watershed algorithm.
    cv2.watershed(arrimg_inpt, markers)
    
    #[23] Create thicker boundary for better segmentation result if thick_boundary is True.
    if thick_boundary: 
        #[25] Create a binary mask where the boundary is
        boundary_mask = np.zeros_like(markers, dtype=np.uint8)
        boundary_mask[markers == -1] = 255

        #[26] Dilate the boundary to make it thicker
        kernel_thickness = np.ones((2, 2), np.uint8)  # Adjust size for thickness
        thick_boundary_mask = cv2.dilate(boundary_mask, kernel_thickness, iterations=1) 
        
        #[27] Apply the thick boundary to the input image
        arrimg_inpt[thick_boundary_mask == 255] = [0, 0, 0]
    else: 
        arrimg_inpt[markers == -1] = [0, 0, 0]
    
    #[28] Save the processed image.
    path_img_6wtsd = replace_pattern_in_filename_and_save(dir_img, bsn_ext, tag_wtsd, arrimg_inpt)
    print(f'[watershed_image] Watershed image saved at {path_img_6wtsd}')
    
    return path_img_6wtsd, arrimg_inpt








#[3] Image Process - End








#[8] Integration - Start

def image_prep(path_img, 
                ratio_magnify = 3,
                prep_use_MB = True, 
                prep_blur_k = 7, prep_enh_cliplmt = 1.5, prep_enh_tileGrid = 12,
                cvrg_spl_rt = 0.1,
                morph_k=3, dt_mask=5, dt_blur_k=31, dt_enh_cliplmt=1.5, dt_enh_tileGrid=10,
                lm_gbk=51, lm_wdk=100, lm_wds=40, 
                lm_pad=50, lm_edge=5, lm_cr=5, lm_mark_original = True,
                frgd_thrs_ratio = 0.4, frgd_GB_k = 37):

    #[1] Initiate list_path_interms.
    list_path_interms = []
    dir_img = os.path.dirname(path_img)
    bsn_ext = os.path.basename(path_img)
    
    #[2] Convert to grayscale.
    arrimg = cv2.imread(path_img)
    arrimg = cv2.cvtColor(arrimg, cv2.COLOR_BGR2GRAY)
    
    #[4] Crop image
    length = 500
    #path_bsn, ext = os.path.splitext(path_img)
    path_img_1crop, arrimg_1crop = crop_image_center_square(path_img, 
                                                            cvt_grayscale=True, 
                                                            tag_crop='1-crop', 
                                                            length=length,)
    path_img = path_img_1crop
    list_path_interms.append(path_img_1crop)

    #[5] Enlarge image
    path_img_2elrg, arrimg_2elrg = enlarge_image(path_img, 
                                                        tag_elrg='2-elrg', ratio_magnify=ratio_magnify)
    path_img = path_img_2elrg
    list_path_interms.append(path_img_2elrg)

    #[6] Enhance image
    prep_tag_mblr='3-mblr'
    prep_tag_enhc='4-enhc'
    path_img_3mblr, path_img_4enhc, arrimg_4enhc \
        = quick_image_correction_path_img(path_img, prep_use_MB,
                                        prep_tag_mblr, prep_blur_k, 
                                        prep_tag_enhc, prep_enh_cliplmt, prep_enh_tileGrid)
    

    path_img = path_img_4enhc
    list_path_interms.extend([path_img_3mblr, path_img_4enhc])

    #[8] Collect coverage data.
    otsu_threshold, path_img_5bnrz, arrimg_5bnrz, path_histg, list_coverage_info\
        = plot_intensity_histogram_for_grayscale_image(path_img, 
                                                        prep_tag_enhc, 
                                                        '_5-binary', 
                                                        '_6-histg', 
                                                        cvrg_spl_rt)
    path_img = path_img_5bnrz
    list_path_interms.extend([path_img_5bnrz, path_histg])


    #[10] Watershed image
    tag_ovlp='6-ovlp'
    tag_wtsd='7-wtsd'
    save_interm=True
    thick_boundary=True
    path_img_6wtsd, arrimg_6wtsd = watershed_image(path_img,
                                                    tag_ovlp,
                                                    tag_wtsd,
                                                    morph_k,
                                                    dt_mask,
                                                    dt_blur_k, 
                                                    dt_enh_cliplmt, 
                                                    dt_enh_tileGrid,
                                                    lm_gbk, lm_wdk, lm_wds, 
                                                    lm_pad, lm_edge, lm_cr, 
                                                    lm_mark_original,
                                                    frgd_thrs_ratio,
                                                    frgd_GB_k,
                                                    save_interm,
                                                    thick_boundary)
    
    path_img = path_img_6wtsd
    list_path_interms.append(path_img_6wtsd)

    return path_img, list_path_interms, list_coverage_info



#[8] Integration - End































"""
[F15_Char.py]
Purpose: Organize media data
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import os, sys, cv2, datetime, serial, time, glob, shutil
import numpy as np
import pandas as pd

#[] For plot
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
import matplotlib.colors as colors

#[] For Font
import freetype

#[] For Image
from PIL import Image




def invt_binarize_blur_grayscale(input_img, k, b, c, invt=True):
    """
    k: increase blur and lose detail, 3~5 are good, 7 will lose detail.
    b: Increate thinkness, 20~80 are good.
    c: Reduce noise without losing detail, 20~30 are good, 15 will have some noise. 
    Best (k, b, c) = 3, 43, 30    
    """
    print('\n[grayscale_blur_binarize]')
    #[1] Handle different types of input (file path, PIL image, or NumPy array)
    if isinstance(input_img, str):  # if input is a file path
        arrimg_0_BGR = cv2.imread(input_img)
    elif isinstance(input_img, Image.Image):  # if input is a PIL image
        arrimg_0_BGR = np.array(input_img.convert('RGB'))[..., ::-1]  # Convert to BGR
    elif isinstance(input_img, np.ndarray):  # if input is already a NumPy array
        arrimg_0_BGR = input_img
    else:
        raise ValueError("Input type not supported. Provide a file path, PIL image, or NumPy array.")
    #[2] Process image
    print(f'--[arrimg_0_BGR] (Max, min, avg, std) = {arrimg_0_BGR.max()}, {arrimg_0_BGR.min()}, {round(arrimg_0_BGR.mean(),2)}, {round(np.std(arrimg_0_BGR),2)}')
    arrimg_1_gray = cv2.cvtColor(arrimg_0_BGR, cv2.COLOR_BGR2GRAY) 
    print(f'--[arrimg_1_gray] (Max, min, avg, std) = {arrimg_1_gray.max()}, {arrimg_1_gray.min()}, {round(arrimg_1_gray.mean(),2)}, {round(np.std(arrimg_1_gray),2)}')
    arrimg_2_blur = cv2.medianBlur(arrimg_1_gray, ksize=k)
    print(f'--[arrimg_2_blur] (Max, min, avg, std) = {arrimg_2_blur.max()}, {arrimg_2_blur.min()}, {round(arrimg_2_blur.mean(),2)}, {round(np.std(arrimg_2_blur),2)}')
    arrimg_3_binary = cv2.adaptiveThreshold(arrimg_2_blur
                                           , 255
                                           , cv2.ADAPTIVE_THRESH_GAUSSIAN_C
                                           , cv2.THRESH_BINARY
                                           , blockSize = b
                                           , C = c)
    if invt:
        arrimg_4_invt = cv2.bitwise_not(arrimg_3_binary)  # Inverting the image colors
    else:
        arrimg_4_invt = arrimg_3_binary
    print(f'--[arrimg_3_binary] (Max, min, avg, std) = {arrimg_3_binary.max()}, {arrimg_3_binary.min()}, {round(arrimg_3_binary.mean(),2)}, {round(np.std(arrimg_3_binary),2)}')
    return arrimg_4_invt




def crop_excess_edge(path_image, k, b, c):
    print('\n[crop_excess_edge]')
    #[1] Image process
    img_1 = invt_binarize_blur_grayscale(path_image, k, b, c, invt=True)
    H, W = img_1.shape   # Must be grayscale or binary image.
    #[2] Sum rows and columns
    sum_col, sum_row = np.sum(img_1,axis=0).tolist(), np.sum(img_1,axis=1).tolist()
    avg_col, avg_row = np.mean(sum_col), np.mean(sum_row)
    print(f'(avg_col, avg_row) = ({avg_col:.2f}, {avg_row:.2f})')
    #[3] Show 1 if the element is larger than average.
    arr_col_larger = [1 if x > avg_col else 0 for x in sum_col]
    arr_row_larger = [1 if x > avg_row else 0 for x in sum_row]
    #[4] Find frist and last non zero.
    idx_col_first_1, idx_col_last_1 = np.min(np.nonzero(arr_col_larger)),  np.max(np.nonzero(arr_col_larger))
    idx_row_first_1, idx_row_last_1 = np.min(np.nonzero(arr_row_larger)),  np.max(np.nonzero(arr_row_larger))
    print(f'[Index of first/last non-zero element in Column] {idx_col_first_1} / {idx_col_last_1}')
    print(f'[Index of first/last non-zero element in Row]    {idx_row_first_1} / {idx_row_last_1}')
    #[5] Crop.
    r = 0.05
    W_start, W_end = idx_col_first_1 - r*W, idx_col_last_1 + r*W
    H_start, H_end = idx_row_first_1 - r*H, idx_row_last_1 + r*H
    W_start, W_end = int(W_start if W_start >= 0 else 0) , int(W_end if W_end <= W else W)
    H_start, H_end = int(H_start if H_start >= 0 else 0) , int(H_end if H_end <= H else H) 
    print(f'(H_start, H_end) = ({H_start}, {H_end})')
    print(f'(W_start, W_end) = ({W_start}, {W_end})')
    img_2 = img_1[H_start:H_end, W_start:W_end]
    return img_2





def average_length_of_ones(arr):
    print('\n[average_length_of_ones]')
    total_length = 0
    current_length = 0
    list_lengths = []
    #[1] Iterate through elements
    for ele in arr:
        if ele == 1:
            current_length += 1
        else:
            if current_length > 0:
                list_lengths.append(current_length)
                total_length += current_length  # Correct the position of this line
                current_length = 0  
                
    #[2] Check if the last element of the array was part of a sequence
    if current_length > 0:
        list_lengths.append(current_length)
        total_length += current_length  # Ensure this is also included
    print(f'--[list_lengths] {list_lengths}')

    #[3] Remove outlier
    max_length = np.max(list_lengths)
    avg_length = np.mean(list_lengths)
    std_length = np.std(list_lengths)
    print(f'--[length] (max, avg, std) = {max_length}, {avg_length:.2f}, {std_length:.2f}')
    if list_lengths and std_length > 0.1 * avg_length:  # Ensure list_lengths is not empty
        k_std = 1
        list_filtered = [x for x in list_lengths if (avg_length + k_std*std_length <= x)]
        sequence_count = len(list_filtered)
        total_length_filtered = sum(list_filtered)
        print(f'--[list_filtered] {list_filtered}')
        #[4] Calculate the average. Protect against division by zero.
        avg_length = total_length_filtered / sequence_count if sequence_count else 0
    print()
    return avg_length



def find_average_font_size(arrimg):
    print('\n[find_average_font_size]')
    print(f'--[shape](H, W) = {arrimg.shape}')
    #[1] Sum rows and columns
    sum_col, sum_row = np.sum(arrimg,axis=0).tolist(), np.sum(arrimg,axis=1).tolist()
    max_col, med_col, avg_col, std_row = np.max(sum_col), np.median(sum_col), np.mean(sum_col), np.std(sum_col)
    max_row, med_row, avg_row, std_row = np.max(sum_row), np.median(sum_col), np.mean(sum_row), np.std(sum_row)
    print(f'--Col (max, med, avg, std)= ({max_col:.2f}, {med_col:.2f}, {avg_col:.2f}, {std_row:.2f})')
    print(f'--Row (max, med, avg, std)= ({max_row:.2f}, {med_row:.2f}, {avg_row:.2f}, {std_row:.2f})')
    #[2] Show 1 if the element is larger than average.
    r_avg = 0.7
    arr_col_larger = [1 if x > avg_col * r_avg else 0 for x in sum_col]
    arr_row_larger = [1 if x > avg_row * r_avg else 0 for x in sum_row]
    #print(f'\n[arr_col_larger]\n{arr_col_larger}')
    #print(f'\n[arr_row_larger]\n{arr_row_larger}')
    #[3] Calculate average font size from row and column
    avg_len_col, avg_len_row = average_length_of_ones(arr_col_larger), average_length_of_ones(arr_row_larger)
    print(f'--(avg_len_col, avg_len_row) = ({avg_len_col:.2f}, {avg_len_row:.2f})')
    avg_font_size = np.mean([avg_len_col, avg_len_row])
    if abs(avg_len_col - avg_len_row) < 0.1 * avg_font_size:
        avg_font_size = avg_font_size
    avg_font_size = round(avg_font_size * 1.2)
    return avg_font_size
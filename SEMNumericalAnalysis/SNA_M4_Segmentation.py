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
import os, sys, cv2, torch, importlib
import numpy as np
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt



from SEMNumericalAnalysis import SNA_M1_Utility as M1UTIL



sys.path.insert(1, r'D:\01_Floor\a_Ed\09_EECS\10_Python\90_Online Tools\FastSAM')
from fastsam import FastSAM, FastSAMPrompt      # type: ignore



#[1] Overlay segmentation result - Start



def compute_edge_roughness_with_gradient_variance(binary_img):
    """
    Ease of Implementation: Easy to moderate. Requires gradient computation (e.g., Sobel) and variance calculation, both of which are straightforward.
    Resolution Invariance: Not invariant. Different resolutions will yield different gradient values and variances due to pixel-level changes in the edge details.
    """
    # [4] Compute gradients using the Sobel operator
    sobel_x = cv2.Sobel(binary_img, cv2.CV_64F, 1, 0, ksize=3)  # Gradient in x-direction
    sobel_y = cv2.Sobel(binary_img, cv2.CV_64F, 0, 1, ksize=3)  # Gradient in y-direction
    # [5] Compute gradient magnitude and Mask out the background
    gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    gradient_magnitude[binary_img == 0] = 0
    # [7] Extract gradients along the edges by selecting non-zero values in the gradient magnitude
    edge_gradients = gradient_magnitude[gradient_magnitude > 0]
    # [8] Calculate the variance of the gradient magnitudes along the edges
    rough_GV = np.var(edge_gradients) if edge_gradients.size > 0 else 0
    return rough_GV



def circumference_and_edge_roughness(arr_img, obj_is_white=True):
    """
    Calculates the circumference of objects in a binary image.
    
    Parameters:
    arr_img (numpy array): The input binary image (0 or 255). 
    obj_is_white (bool): If True, white (255) is considered the object, black (0) is the background.
                         If False, black (0) is considered the object, white (255) is the background.
    
    Returns:
    float: The total circumference (in pixels) of the detected objects.
    
    Note: 
    If there is more than one object, the circumf_px will be the sum of these objects.
    """
    
    # [1] Ensure the image is single-channel (grayscale)
    if len(arr_img.shape) == 3:  # If the image is not already grayscale
        arr_img = cv2.cvtColor(arr_img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

    # [2] Invert image if the object is black and background is white
    if not obj_is_white:
        
        
        arr_img = cv2.bitwise_not(arr_img) 

    # [3] Ensure the image is binary (0 and 255 values)
    _, binary_img = cv2.threshold(arr_img, 127, 255, cv2.THRESH_BINARY)

    # [4] Convert the image to the required 8-bit single-channel format
    binary_img = np.uint8(binary_img)

    # [5] Find contours from the binary image
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # [6] Calculate the circumference (perimeter) of all the contours
    circumf_px = round(sum(cv2.arcLength(cnt, True) for cnt in contours),3)
    area_px_255 = np.sum(binary_img == 255)
    
    return circumf_px, area_px_255


    

def process_single_image_segmentation(arr3d_seg_masks, 
                                        path_original_img,
                                        edge_pixel, 
                                        font_size, 
                                        tag_ovlp,
                                        r_seg_area_lim_lu = [0.001, 0.9],
                                        save_segs=True):
    #[1] Set directories and extract base names.
    dir_img = os.path.dirname(path_original_img)
    bsn_ext = os.path.basename(path_original_img)
    bsn, ext = os.path.splitext(bsn_ext)
    arrimg_orig = cv2.imread(path_original_img) # This should be a binary img.
    print(f'\n[overlap_every_segmentation_results_as_a_single_image] Processing: {bsn_ext}')
    
    #[2] Ensure arr3d_seg_masks is a numpy array
    if not isinstance(arr3d_seg_masks, np.ndarray):
        arr3d_seg_masks = np.array(arr3d_seg_masks)
    
    #[3] Initialize an empty canvas to overlap the segmentation results.
    height, width = arr3d_seg_masks.shape[1:]  
    overlapped_img = np.zeros((height, width, 3), dtype=np.uint8)
    arrimg_orig_gray = np.where(arrimg_orig == 255, 60, arrimg_orig)
    overlapped_img_for_num = cv2.bitwise_or(overlapped_img, arrimg_orig_gray)
    overlapped_img_for_noise = cv2.bitwise_or(overlapped_img, arrimg_orig_gray)
    
    #[4] Create folder to save segmentation.
    if save_segs:
        dir_save_seg = f'{os.path.splitext(path_original_img)[0]}_Seg{tag_ovlp}'
        print(f'dir_save_seg: {dir_save_seg}')
        os.makedirs(dir_save_seg, exist_ok=True)
    

    #[6] Initiate empty lists.
    list_x_center, list_y_center = [], []
    list_area = []
    list_circumf = []
    list_csar = []  # Circumference Squared to Area Ratio
    list_at_edge = []
    list_success = []
    cnt_seg_raw = len(arr3d_seg_masks)
    
    #[10] Iterate through segmentation results and save images.
    for i, iter_seg in enumerate(arr3d_seg_masks):
        
        #[12] Segmentation area check.
        total_area = height * width
        seg_area = np.sum(iter_seg == 255)  # Count white pixels
        r_seg_area = seg_area / total_area
        r_seg_area_lower_limit, r_seg_area_upper_limit = r_seg_area_lim_lu
        
        #[15] Collect data.
        print(f'\n-- [S-{i:04d}/{cnt_seg_raw:04d}] \t {r_seg_area:.2%} = ( {seg_area}/{total_area} ) ', end='')
        if r_seg_area > r_seg_area_upper_limit:
            print(f'\n   Removing unreasonably large segmentation. \t[S{i:03d}] {seg_area} pixel \t({r_seg_area:.3%}).')
            continue
        elif r_seg_area < r_seg_area_lower_limit:
            print(f'\n   Removing unreasonably small segmentation. \t[S{i:03d}] {seg_area} pixel \t({r_seg_area:.3%}).')
            continue
        
        #[16] Calculate circumference and CSAR (Circumference Squared to Area Ratio)
        circumf_px, _ = circumference_and_edge_roughness(iter_seg, obj_is_white=True)
        
        #[17] Create color mask
        iter_seg_color = np.zeros((height, width, 3), dtype=np.uint8)
        iter_seg_color[iter_seg == 255] = [255, 255, 255]  # White for segmented area
        
        #[18] Add number to the mask.
        text_on_mask = f'{i}({r_seg_area:.2%})\n{circumf_px:.0f}'
        iter_seg_color_num = add_number_to_mask(iter_seg_color, text_on_mask, font_size)
        
        #[19] Find position, area, and check edge.
        x_center, y_center, area, at_edge = find_position_area_and_check_if_at_edge(iter_seg_color, edge_pixel)
        list_success.append(i)
        list_x_center.append(x_center)
        list_y_center.append(y_center)
        list_area.append(area)
        list_at_edge.append(at_edge)
        list_circumf.append(circumf_px)
        list_csar.append(circumf_px**2/area)
    
        #[22] Overlap the segmentation result.
        overlapped_img_for_num = cv2.bitwise_or(overlapped_img_for_num, iter_seg_color_num)
        overlapped_img_for_noise = cv2.bitwise_or(overlapped_img_for_noise, iter_seg_color_num)

        #[23] Save segmentations.
        if save_segs:
            path_iter_seg = os.path.join(dir_save_seg, f'{bsn_ext}_seg{i:04d}.jpg')
            cv2.imwrite(path_iter_seg, iter_seg_color)
    
    
    #[25] Compute and Save background noise representation.
    arrimg_orig_1D = arrimg_orig.ravel()
    noise_1D = overlapped_img_for_noise.ravel()
    bkgd_pixel_1D = arrimg_orig_1D[noise_1D != 255]
    avg_bkgd_pixel = np.mean(bkgd_pixel_1D)
    std_bkgd_pixel = np.std(bkgd_pixel_1D)
    path_bkgd_noise = os.path.join(dir_save_seg, f'{bsn_ext}_bkgd noise.jpg')
    cv2.imwrite(path_bkgd_noise, overlapped_img_for_noise)
    
    #[27] Calculation nucleation density.
    cnt_seg_success = len(list_success)
    nucle_dsty_psqpx = cnt_seg_success/total_area
    avg_grain_size_sqpx = np.mean(list_area)
    std_grain_size_sqpx = np.std(list_area)
    avg_circumf_px = np.mean(list_circumf)
    std_circumf_px = np.std(list_circumf)
    avg_csar = np.mean(list_csar)
    std_csar = np.std(list_csar)
    print(f'-- [Nucleation density]        \t{nucle_dsty_psqpx:.3e} (crystal / pixel^2)')
    print(f'-- [Grain size (mean, std)]    \t{avg_grain_size_sqpx:.3f} (pixel^2), \t {std_grain_size_sqpx:.3f} (pixel^2)')
    print(f'-- [Circumference (mean, std)] \t{avg_circumf_px:.3f} (pixel), \t {std_circumf_px:.3f} (pixel)')
    dict_nd_gs_cf = {'cnt_seg_success': cnt_seg_success,
                    'nucle_dsty_psqpx': nucle_dsty_psqpx,
                    'avg_grain_size_sqpx': avg_grain_size_sqpx,
                    'std_grain_size_sqpx': std_grain_size_sqpx,
                    'avg_circumf_px': avg_circumf_px,
                    'std_circumf_px': std_circumf_px,
                    'avg_csar': avg_csar,
                    'std_csar': std_csar,
                    'avg_bkgd_pixel': avg_bkgd_pixel,
                    'std_bkgd_pixel': std_bkgd_pixel}

    #[28] Create df_single_img to collect segmentations of single image.
    df_single_img = pd.DataFrame({'list_success': list_success,
                                'pos_x': list_x_center,
                                'pos_y': list_y_center,
                                'area': list_area,
                                'circumf': list_circumf,
                                'csar': list_csar,
                                'at_edge': list_at_edge})
    
    
    #[29] Save df_single_img as excel.
    path_xlsx = os.path.join(dir_save_seg, f'{bsn}_segs.xlsx')
    sheet_name = '02_Segs'
    M1UTIL.save_df_as_excel_overwrite(df_single_img, path_xlsx, sheet_name)
    
    
    #[31] Save the final overlapped image.
    output_path = os.path.join(dir_img, f'{bsn}{tag_ovlp}{ext}')
    cv2.imwrite(output_path, overlapped_img_for_num)
    print(f'-- Overlapped image saved to {output_path}\n')

    return output_path, df_single_img, dict_nd_gs_cf


             
#[1] Overlay segmentation result - Start




#[2] FastSAm segmentation - Start

def segment_single_image(path_img, path_FastSAM_model_pt, conf=0.2, iou=0.5):
    """
    Perform segmentation using FastSAM model.
    ref: https://docs.ultralytics.com/models/fast-sam/
    thld_conf (threshold of confidence, 0-1): how confident the model needs to be about a detection to keep it.
    thld_ioui (threshold of intersection over union, 0-1): overlap to union ratio for model to recognize it as an union.
    """
    print(f'\n[segment_single_image]')
    #[5] Process the image
    img = cv2.imread(path_img)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    #[6] Run inference on an image
    model = FastSAM(path_FastSAM_model_pt)
    everything_results = model(img, device=device, retina_masks=True, imgsz=1024, conf=conf, iou=iou)
    prompt_process = FastSAMPrompt(path_img, everything_results, device=device)
    segmentation_results = prompt_process.everything_prompt()
    cnt_seg_raw = len(segmentation_results) if segmentation_results is not None else 0
    
    #[2] Convert all segmentation results to numpy arrays in one go (if necessary).
    if isinstance(segmentation_results, torch.Tensor):
        segmentation_results = segmentation_results.cpu().numpy()
        print('--Converting all segmentation results to numpy array.')
    
    return segmentation_results, cnt_seg_raw




def find_position_area_and_check_if_at_edge(arrimg, edge_pixel = 3):
    #[1] Calculate the center of mass of the mask
    mask_indices = np.where(arrimg > 0)
    if mask_indices[0].size == 0:  # If there are no positive values in the mask
        x_center, y_center = arrimg.shape[1] // 2, arrimg.shape[0] // 2
        area = 0  # No mask area
        at_edge = False  # No mask, so not at edge
    else:
        x_center = int(np.mean(mask_indices[1]))
        y_center = int(np.mean(mask_indices[0]))
        
        #[2] Calculate the area of the mask (non-zero pixels)
        area = mask_indices[0].size
        
        #[3] Check if the mask is at the edge
        img_height, img_width = arrimg.shape[:2]
        
        at_edge = (
            np.any(mask_indices[0] <= edge_pixel) or  # Near top edge (within padding)
            np.any(mask_indices[0] >= img_height - edge_pixel) or  # Near bottom edge
            np.any(mask_indices[1] <= edge_pixel) or  # Near left edge
            np.any(mask_indices[1] >= img_width - edge_pixel)  # Near right edge
        )

    #[4] Return the center, area, and edge status
    return x_center, y_center, area, at_edge






def add_number_to_mask(arrimg, text_on_mask, font_size=1, line_spacing=30, xy_shit = [-30, 10]):
    #[1] Calculate the center of mass of the mask to place the text
    mask_indices = np.where(arrimg > 0)
    if mask_indices[0].size == 0:  # If there are no positive values in the mask
        x_center, y_center = arrimg.shape[1] // 2, arrimg.shape[0] // 2
    else:
        x_center = int(np.mean(mask_indices[1])) + xy_shit[0]
        y_center = int(np.mean(mask_indices[0])) + xy_shit[1]
    
    #[2] Split text by new lines
    lines = text_on_mask.split('\n')
    
    #[3] Add each line of text to the image, adjusting y_center for each line
    arr_img_text = arrimg.copy()
    for i, line in enumerate(lines):
        y_offset = y_center + i * line_spacing  # Adjust y position for each line
        arr_img_text = cv2.putText(
            arr_img_text,              # Image to draw on
            line,                      # The line of text to draw
            (x_center, y_offset),      # Position to draw the text
            cv2.FONT_HERSHEY_SIMPLEX,  # Font type
            font_size,                 # Font scale
            [250, 100, 100],           # Color
            thickness=3,               # Thickness of the text
            lineType=cv2.LINE_AA        # Anti-aliased line
        )
    
    return arr_img_text


#[2] FastSasm Segmentation - End




#[4] Normal Segmentation - Start


import cv2
import numpy as np

def segment_single_image_black_bkgd(path_img): 
    #[1] Load the image, ensure it's binary.
    binary_image = cv2.imread(path_img, cv2.IMREAD_GRAYSCALE)
    _, binary_image = cv2.threshold(binary_image, 127, 255, cv2.THRESH_BINARY)
    
    #[2] Perform connected component analysis (background is 0, foreground is 255).
    num_labels, labels = cv2.connectedComponents(binary_image)

    list_seg_masks = []

    #[3] Iterate through each label (excluding background, label=0).
    for label in range(1, num_labels):
        #[4] Create a mask for the current segment.
        segment_mask = np.zeros(binary_image.shape, dtype=np.uint8)
        segment_mask[labels == label] = 255

        #[5] Optionally, find contours of the segment (can be used for additional processing).
        contours, _ = cv2.findContours(segment_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #[6] If contours are found, add the mask to the list (mask has 255 for segment).
        if len(contours) > 0:
            list_seg_masks.append(segment_mask)

    #[7] Convert list of 2D masks to a 3D numpy array.
    if len(list_seg_masks) > 0:
        arr3d_seg_masks = np.stack(list_seg_masks, axis=0)
    else:
        arr3d_seg_masks = np.array([])  # Handle case where no segments are found.

    cnt_seg_raw = len(list_seg_masks)

    return arr3d_seg_masks, cnt_seg_raw


#[4] Normal Segmentation - End











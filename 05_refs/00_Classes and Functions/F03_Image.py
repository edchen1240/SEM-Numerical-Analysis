"""
[F03_Image.py]
Purpose: Image manipulation.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import os, sys, cv2, xlsxwriter
import numpy as np
import pandas as pd
from PIL import Image

#[1] Basic Image Processing - Start

def reduce_image_size(path_img, resize_ratio=None, path_save=None):
    print(f'\n[reduce_image_size] \t{os.path.basename(path_img)}, \tresize_ratio = {resize_ratio},', end='')
    #[1] Read the image using cv2
    arrimg = cv2.imread(path_img)
    if arrimg is None:
        raise FileNotFoundError(f"Image at path '{path_img}' not found.")

    #[2] Resize the image
    if resize_ratio:
        if not resize_ratio < 2:
            raise ValueError(f'It is advisible to have resize_ratio less than 2. Please check. {resize_ratio}')
        h, w = arrimg.shape[:2]
        new_width = int(w * resize_ratio)
        new_height = int(h * resize_ratio)
        new_pixel = new_width * new_height
        print(f'\t(new_width, new_height, new_pixel) = {new_width}, {new_height}, {new_pixel}')
        arrimg_reduced = cv2.resize(arrimg, (new_width, new_height), interpolation=cv2.INTER_NEAREST)

    #[3] Save the image
    if path_save:
        cv2.imwrite(path_save, arrimg_reduced)
    return arrimg_reduced



#[] boxBlur, gray scale, binary, medianBlur
def image_quick_correction(arrimg, path_img, save_output=False):
    #[1] Image dir and bsn
    dir = os.path.dirname(path_img)
    bsn_ext = os.path.basename(path_img)
    bsn, ext = os.path.splitext(bsn_ext)
    
    #[3] medianBlur
    arrimg_2mb = cv2.medianBlur(arrimg, ksize=5)
    if save_output:
        path_img_2mb = os.path.join(dir, f'{bsn}_2-mb{ext}')
        cv2.imwrite(path_img_2mb, arrimg_2mb)

    #[5] Grayscale
    arrimg_3gray = cv2.cvtColor(arrimg_2mb, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    blur_metric = round(cv2.Laplacian(arrimg_3gray, cv2.CV_64F).var(),0)
    if blur_metric <= 50:
        print(bsn_ext, f'The image {bsn_ext} is too blur ({blur_metric}). Now apply furthur enhancement.')
        arrimg_3gray = cv2.convertScaleAbs(arrimg_3gray, alpha=2.5, beta=-10)
        # GoodValue: alpha=2.5, beta=-20 
    if save_output:
        path_img_3gray = os.path.join(dir, f'{bsn}_3-gray{ext}')
        cv2.imwrite(path_img_3gray, arrimg_3gray)

    # [8] Apply adaptive thresholding (binary)
    arrimg_4binary = cv2.adaptiveThreshold(arrimg_3gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, blockSize=17, C=3)
    if save_output:
        path_img_4binary = os.path.join(dir, f'{bsn}_4-binary{ext}')
        cv2.imwrite(path_img_4binary, arrimg_4binary)
        
    # [10] Apply median blur to the binary image
    arrimg_5mb = cv2.medianBlur(arrimg_4binary, ksize=3)
    path_img_5mb = os.path.join(dir, f'{bsn}_5-mb{ext}')
    if save_output:
        cv2.imwrite(path_img_5mb, arrimg_5mb)

    return arrimg_5mb, path_img_5mb, blur_metric


def crop_to_same_size(path_img_t1, path_img_t2):
    print('\n[crop_to_same_size] sometime, size missed by a few pixel, and it makes ')
    global img1_cropped
    global img2_cropped
    img1 = cv2.imread(path_img_t1)
    img2 = cv2.imread(path_img_t2)
    img1_height, img1_width = img1.shape[:2]
    img2_height, img2_width = img2.shape[:2]
    if img1_width == img2_width and img1_height == img2_height:
        print('--Two images have the same size.', img1_width, ' x ', img1_height)
        path_img_t1_cropped = path_img_t1
        path_img_t2_cropped = path_img_t2
        
    else:
        print('--Two images have different size. Image_1:', img1_width, ' x ', img1_height, '; Image_2:', img2_width, 'x', img2_height)
        width_min =  min(img1_width, img2_width)
        height_min = min(img1_height, img2_height)
        img1_cropped = img1[0:width_min, 0:height_min]
        img2_cropped = img2[0:width_min, 0:height_min]
        img1_width, img1_height = img1_cropped.shape[:2]
        img2_width, img2_height = img2_cropped.shape[:2]
        print('--After crop. Image_1:', img1_width, ' x ', img1_height, '; Image_2:', img2_width, 'x', img2_height)
        path_img_t1_cropped = path_img_t1.replace('.png', '_1-crop.png')
        path_img_t2_cropped = path_img_t2.replace('.png', '_1-crop.png')
        cv2.imwrite(path_img_t1_cropped, img1_cropped) 
        cv2.imwrite(path_img_t2_cropped, img2_cropped) 
        
    return path_img_t1_cropped, path_img_t2_cropped

def print_arrimg_stat(path_or_arr_img, kstd=3, name='Color Statistics', print_status=False):
    #[1] Check if input is a path or an array
    if isinstance(path_or_arr_img, str):
        arr_img = cv2.imread(path_or_arr_img)
    else:
        arr_img = path_or_arr_img

    #[2] Check dimension
    if arr_img.ndim != 3 or arr_img.shape[2] != 3:
        raise ValueError("Input array must be a 3-channel image array (BGR).")

    #[3] Calculate statistics for each channel
    b_channel = arr_img[:,:,0]
    g_channel = arr_img[:,:,1]
    r_channel = arr_img[:,:,2]

    b_max, b_mean, b_min, b_std = np.max(b_channel), np.mean(b_channel), np.min(b_channel), np.std(b_channel)
    g_max, g_mean, g_min, g_std = np.max(g_channel), np.mean(g_channel), np.min(g_channel), np.std(g_channel)
    r_max, r_mean, r_min, r_std = np.max(r_channel), np.mean(r_channel), np.min(r_channel), np.std(r_channel)
    b_pks, b_nks = b_mean + kstd*b_std, b_mean - kstd*b_std
    g_pks, g_nks = g_mean + kstd*g_std, g_mean - kstd*g_std
    r_pks, r_nks = r_mean + kstd*r_std, r_mean - kstd*r_std

    #[4] Create a DataFrame to organize the statistics
    data = {
        'Channel': ['B', 'G', 'R'],
        'Max': [b_max, g_max, r_max],
        'Mean': [b_mean, g_mean, r_mean],
        'Min': [b_min, g_min, r_min],
        'Std': [b_std, g_std, r_std],
        f'Mean + {kstd} Std': [b_pks, g_pks, r_pks],
        f'Mean - {kstd} Std': [b_nks, g_nks, r_nks]
    }

    df_stat = pd.DataFrame(data)
    df_stat.set_index('Channel', inplace=True)
    
    #[5] Print the DataFrame
    if print_status:
        print(f'\n[{name}]')
        print(df_stat.to_string(float_format='%.2f'))
    
    #[6] Round the stds we need.
    b_pks, b_nks = int(b_pks), int(b_nks)
    g_pks, g_nks = int(g_pks), int(g_nks)
    r_pks, r_nks = int(r_pks), int(r_nks)
    
    return df_stat, b_pks, b_nks, g_pks, g_nks, r_pks, r_nks

#[1] Basic Image Processing - End







#[5] Find Hough Line - Start

def draw_a_line(rho, theta_rad, color, thickness, arrimg):
    cos_theta = np.cos(theta_rad)
    sin_theta = np.sin(theta_rad)
    x0 = rho * cos_theta
    y0 = rho * sin_theta
    x1 = int(x0 + 1000 * (-sin_theta))
    y1 = int(y0 + 1000 * cos_theta)
    x2 = int(x0 - 1000 * (-sin_theta))
    y2 = int(y0 - 1000 * cos_theta)
    cv2.line(arrimg, (x1, y1), (x2, y2), color, thickness)
    return arrimg


def polar_coordinate_normalization(list_line):
    # [1] Initiate an empty list to store normalized lines.
    normalized_lines = []
    
    # [2] Iterate through each line in the provided list of lines.
    for line in list_line:
        # [5] Unpack the line coordinates if necessary.
        if len(line) == 2:
            rho, theta_rad = line
        elif len(line) == 1:
            rho, theta_rad = line[0]
        else:
            print('Check list type:', line)
        
        # [6] If rho is negative, convert theta_rad by subtracting pi and make rho positive.
        if rho < 0:
            rho = -rho
            theta_rad = theta_rad - np.pi
        
        # [8] Add the normalized coordinates to the new list.
        normalized_lines.append([rho, theta_rad])
    
    # Return the array of normalized lines.
    return np.array(normalized_lines)


def cross_line_check(normalized_lines):
    # [1] Initialize variables to store average sets
    avg_set_with_larger_rad = ''
    avg_set_with_smaller_rad = ''
    
    # [2] Calculate average rho and theta_rad
    avg_theta_rad = [round(x, 2) for x in np.average(normalized_lines, axis=0)]
    
    # [3] Initialize sets for larger and smaller theta_rad
    set_with_larger_rad = []
    set_with_smaller_rad = []
    
    # [4] Iterate through normalized lines
    for iter_line in normalized_lines:
        if iter_line[1] >= avg_theta_rad[1]:
            set_with_larger_rad.append(iter_line.tolist())
            avg_set_with_larger_rad = [round(x, 2) for x in np.average(set_with_larger_rad, axis=0)]
        else:
            set_with_smaller_rad.append(iter_line.tolist())
            avg_set_with_smaller_rad = [round(x, 2) for x in np.average(set_with_smaller_rad, axis=0)]
    
    # [5] Count lines in each set
    cnt_line_larger_rad = len(set_with_larger_rad)
    cnt_line_smaller_rad = len(set_with_smaller_rad)
    
    # [6] Print the counts for debugging
    sys.stdout.flush()
    print('cnt_larger:', cnt_line_larger_rad)
    print('cnt_smaller:', cnt_line_smaller_rad)
    
    # [7] Return the average sets
    return avg_set_with_larger_rad, avg_set_with_smaller_rad


def find_Hough_Line_on_single_arrimg(arrimg, img_path, arrimg_draw=None):
    
    #[1] Image dir and bsn
    dir = os.path.dirname(img_path)
    bsn_ext = os.path.basename(img_path)
    bsn, ext = os.path.splitext(bsn_ext)

    # [2] Convert to grayscale if the image is in color
    if len(arrimg.shape) == 3 and arrimg.shape[2] == 3:
        gray_img = cv2.cvtColor(arrimg, cv2.COLOR_BGR2GRAY)
    else:
        gray_img = arrimg
        
    edges = cv2.Canny(arrimg, 200, 200)  
    # Fine results: (image, 1000, 200), (image, 500, 500), (image, 500, 100), (image, 1500, 100).
    
    #[8] Perform Hough Line Transform
    lines = cv2.HoughLines(edges, rho=1, theta=np.pi / 180, threshold = 30)  
    # GoodValue: 28-30. Threshold 20 too much noise, 40 missing detailes.
    
    # [5] Initialize or validate arrimg_draw as a color image
    if arrimg_draw is None:
        arrimg_draw = cv2.cvtColor(np.zeros_like(gray_img), cv2.COLOR_GRAY2BGR)
    else:
        if arrimg.shape[:2] != arrimg_draw.shape[:2]:
            raise ValueError(f'arrimg_draw {arrimg_draw.shape} should have the same size as arrimg {arrimg.shape[:2]}.')

    #[10] Initiate variables
    num_lines = 0
    is_corner = 0
    line_v_deg = None
    std_theta_deg = None
    lined_image = arrimg_draw
    
    #[12] Draw the detected lines on the original image
    if lines is not None:
        num_lines = len(lines)  #Calculate the number of lines.
        normalized_lines = polar_coordinate_normalization(lines)
        
        #[15] Draw every line in red.
        for line in normalized_lines:
            rho, theta_rad = line
            lined_image = draw_a_line(rho, theta_rad, (0, 255, 255), 1, arrimg_draw)
                
        #[18] Extract theta_rad part from the list, convert to theta_deg, and store to new list.
        list_theta_deg = [int(np.rad2deg(line[1])) for line in normalized_lines]
        std_theta_deg = int(np.std(list_theta_deg))
        
        #[20] Calculate average rho and theta_rad.    
        line_avg_rho_theta = [round(x, 2) for x in np.average(normalized_lines, axis=0)]
        avg_rho, avg_theta_rad = line_avg_rho_theta        
        
        #[23] Corner check. Standard deviation of the theta(deg) to perform corner check.
        if std_theta_deg > 20: 
            is_corner = 1
            print(f'--std_theta_deg larger than 20. {bsn_ext} is a possible corner.')
            avg_set_with_larger_rad, avg_set_with_smaller_rad = cross_line_check(normalized_lines)
            avg_rho_smaller, avg_theta_rad_smaller = avg_set_with_smaller_rad
            lined_image = draw_a_line(avg_rho_smaller, avg_theta_rad_smaller, (0, 0, 255), 3, lined_image)
            avg_rho_larger, avg_theta_rad_larger = avg_set_with_larger_rad
            lined_image = draw_a_line(avg_rho_larger, avg_theta_rad_larger, (0, 0, 255), 3, lined_image)
            num1 = str(int(90 - np.rad2deg(avg_theta_rad_smaller)))
            num2 = str(int(90 - np.rad2deg(avg_theta_rad_larger)))
            line_v_deg = f'{num1}, {num2}'
                
        #[25] Convert rad to degree, and convert coordinate.
        else:
            avg_theta_deg = np.rad2deg(avg_theta_rad)
            line_v_deg = int(90 - avg_theta_deg) # Right is 0 deg, and top is 90 deg.
            lined_image = draw_a_line(avg_rho, avg_theta_rad, (0, 0, 255), 3, lined_image)

    #[30] Save image
    path_img_lined = os.path.join(dir, f'{bsn}_6-lined_C{is_corner}_{line_v_deg}{ext}')
    cv2.imwrite(path_img_lined, lined_image)
    return num_lines, std_theta_deg, line_v_deg, is_corner


def batch_Hough_line_detection(list_path_img, save_output=True):
    #[1] Initiate lists
    list_num_lines = []
    list_blur_metric = [] = []
    list_bsn = []
    list_line_v_deg = []
    list_std_theta_deg = []
    list_is_corner = []

    #[3] Iterate through files.
    for iter_path in list_path_img:
        #[4] Collect basename.
        bsn = os.path.basename(iter_path)
        print(f'--{bsn}')
        
        #[5] Crop, compress, and save.
        arrimg_rdc, img_path_rdc = reduce_image_size(iter_path, 10, save_output)

        #[6] boxBlur, gray scale, binary, medianBlur
        arrimg_5mb, path_img_5mb, blur_metric = image_quick_correction(arrimg_rdc, iter_path, save_output)
        
        #[8] Line detection
        num_lines, std_theta_deg, \
        line_v_deg, is_corner= find_Hough_Line_on_single_arrimg(arrimg_5mb, path_img_5mb, arrimg_rdc)
        
        #[10] Collect lists
        list_bsn.append(bsn)
        list_num_lines.append(num_lines)
        list_blur_metric.append(blur_metric)
        list_std_theta_deg.append(std_theta_deg)
        list_line_v_deg.append(line_v_deg)
        list_is_corner.append(is_corner)
        
    # [12] Combine lists into df_img_lines
    df_img_lines = pd.DataFrame({
        'bsn': list_bsn,
        'num_lines': list_num_lines,
        'blur_metric': list_blur_metric,
        'std_theta_deg': list_std_theta_deg,
        'line_v_deg': list_line_v_deg,
        'is_corner': list_is_corner,
    })
    
    return df_img_lines



#[5] Find Hough Line - End










"""
[2023-09-29] This function is used to truncate the image matrix to a square matrix.
"""
def ndarray_to_square(matrix):
      global shape
      row, col = matrix.shape     # m, n = 9, 12
      length = min(row, col)        # 9
      half_row, half_col = row//2, col//2   # row, col = 4, 6
      half_length = length // 2   # 4
      # Calculate the slice indices for the submatrix
      row_start = half_row - half_length             #= max(0, row - half_size)
      row_end = half_row + half_length               #= min(m, row + half_size + 1)
      col_start = half_col - half_length             #= max(0, col - half_size)
      col_end = half_col + half_length               #= min(n, col + half_size + 1)
      # Extract the submatrix
      square_matrix = matrix[row_start:row_end, col_start:col_end]
      shape = square_matrix.shape[0]
      print('square_matrix.shape:\n', square_matrix.shape)
      return square_matrix



"""
[2023-09-29] Generate a simple square matrix with center 1s.
"""
def square_matrix_center_1s(n):
      v_min, v_max = 0, 1
      gradient_matrix = np.full((n, n), v_min, dtype=int)
      center = (n + 1) // 2
      center_range = max(center//2, 1)
      gradient_matrix[center, center] = v_min
      for m in range(center - center_range, center + center_range):
            for n in range(center - center_range, center + center_range):
                  gradient_matrix[m, n] += v_max
      return gradient_matrix


"""
[2023-] Convert between two image opened format.
cv2.imread(image_path): NumPy array in BGR format
image.open(image_path): Pillow library in RGB format.
"""
def convert_opened_image_format(opened_image):
      return opened_image


"""
[2023-1012] crop_area_on_two_sides_of_line
After finding a line with certain degree on the image, this code will assume the line is 
across the center, and crop out two patches from two sides of the line.
"""

def crop_area_on_two_sides_of_line(path_image, angel_of_line_across_center):
      array_image_BGR = cv2.imread(path_image)
      h, w, c = array_image_BGR.shape
      print('[Image Shape] (H, W, C):', h, w, c, end='\n')
      if max(h, w) > 500:
            raise ValueError('One of the length of the image is longer than 500.',
                             'Consider compress the image before continue.')
      short_length = min(h, w)
      patch_size = short_length




def translate_image(arrimg, x_dir, y_dir):
    #[1] Define translation matrix 
    M = np.float32([[1, 0, x_dir], [0, 1, y_dir]])
    #[1] Shift image
    translated_image = cv2.warpAffine(arrimg, M, (arrimg.shape[1], arrimg.shape[0]))
    return translated_image



def rotate_image(arrimg, x_ctr_rot, y_ctr_rot, rot_theta):   # rot_theta is defined as counter-clockwise
    #[1] Define the center of rotation
    center = (x_ctr_rot, y_ctr_rot)
    #[2] Calculate the rotation matrix
    M = cv2.getRotationMatrix2D(center, rot_theta, 1.0)
    #[3] Rotate the image
    rotated_image = cv2.warpAffine(arrimg, M, (arrimg.shape[1], arrimg.shape[0]))
    return rotated_image










def add_text_to_opencv_image(cv2image, text, start_x=30, start_y=60, line_spacing=40, 
                             font_scale=1, font_color=(13, 130, 240), thickness=2):
    """
    Adds text to an OpenCV image at specified coordinates with customizable options
    for line spacing, font scale, color, and thickness.

    Args:
        cv2image (numpy.ndarray): The image to which text will be added.
        text (str): The text to add. Supports multiline separated by '\n'.
        start_x (int): The x-coordinate of the start position for the text.
        start_y (int): The y-coordinate of the start position for the text.
        line_spacing (int): The spacing between lines of text.
        font_scale (float): The scale factor that is multiplied by the font-specific base size.
        font_color (tuple): Color of the text in BGR (blue, green, red).
        thickness (int): Thickness of the text lines.

    Returns:
        numpy.ndarray: The image with text added.
    """
    # Font settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    lines = text.split('\n')

    y = start_y
    for line in lines:
        cv2.putText(cv2image, line, (start_x, y), font, font_scale, font_color, thickness, lineType=cv2.LINE_AA)
        y += line_spacing

    return cv2image








def add_bleed_to_batch_of_images(dir_img, list_dimesnsion, dir_output):
    #[1] Extract JPG and PNG files in the directory.
    list_path_img = [os.path.join(dir_img, file) for file in os.listdir(dir_img) 
                    if file.lower().endswith(('.jpg', '.jpeg', '.png'))]    
    cnt_img = len(list_path_img)
    
    #[2] Unpack list_dimesnsion.
    add_top, add_bottom, add_left, add_right = list_dimesnsion
    
    #[4] Iterate through images.
    for i, path_img in enumerate(list_path_img):
        #[5] Load the image.
        bsn_img = os.path.basename(path_img)
        print(f'\t[{i:04d}/{cnt_img:04d}] Processing {bsn_img}')
        try:
            img = Image.open(path_img)
            width, height = img.size
            
            #[6] Calculate new dimensions with bleed.
            new_width = width + add_left + add_right
            new_height = height + add_top + add_bottom
            
            #[7] Create a new image with the new dimensions and white background.
            new_img = Image.new('RGB', (new_width, new_height), (255, 255, 255))
            
            #[8] Paste the original image onto the new image.
            new_img.paste(img, (add_left, add_top))
            
            #[9] Save the new image to the output directory.
            path_output_img = os.path.join(dir_output, bsn_img)
            new_img.save(path_output_img)
            #print(f'\t-- Saved to {path_output_img}')
        
        except Exception as e:
            print(f'\t-- Error processing {bsn_img}: {str(e)}')
    
    return



def retrieve_datetime_of_single_media_files(path_media, 
                                            datetime_format = '%Y-%m-%d, %H:%M:%S'):
    #[2] Get file extension
    bsn_ext = os.path.basename(path_media)
    bsn, ext = os.path.splitext(bsn_ext)
    ext = ext.upper()
    
    #[3] Check file type for image
    if ext in ['.JPG', '.JPEG', '.PNG', '.GIF', '.TIF']:
        try:
            media_datetime = datetime.strptime(Image.open(path_media)._getexif()[36867], 
                                                '%Y:%m:%d %H:%M:%S').strftime(datetime_format)
            method = '[1] get_date_taken(image)'
        except (KeyError, UnidentifiedImageError, TypeError, AttributeError):
            media_datetime = datetime.fromtimestamp(os.path.getmtime(path_media)).strftime(datetime_format)
            method = '[2] os.path.getmtime(image)'
    
    #[3.1] Check file type for HEIC
    elif ext == '.HEIC':
        try:
            # Try to get EXIF data from HEIC
            img = Image.open(path_media)
            if hasattr(img, '_getexif') and img._getexif():
                media_datetime = datetime.strptime(img._getexif()[36867], 
                                                    '%Y:%m:%d %H:%M:%S').strftime(datetime_format)
                method = '[1] get_date_taken(HEIC)'
            else:
                raise AttributeError("No EXIF data")
        except (KeyError, UnidentifiedImageError, TypeError, AttributeError):
            media_datetime = datetime.fromtimestamp(os.path.getmtime(path_media)).strftime(datetime_format)
            method = '[2] os.path.getmtime(HEIC)'
                
    #[4] Check file type for video
    elif ext in ['.MP4', '.MOV']:
        media_datetime = datetime.fromtimestamp(os.path.getmtime(path_media)).strftime(datetime_format)
        method = '[3] os.path.getmtime(video)'
    
    #[5] Handle unknown file types
    else:
        media_datetime, method = None, None
        print(f'Unknown file type {bsn_ext}, usually AAE or other unsupported format.')
    return ext, media_datetime, method












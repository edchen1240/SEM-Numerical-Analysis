"""
[F09_OMcam.py]
Purpose: OM camera functions.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import os, sys, cv2, datetime, serial, time
import numpy as np



def capture_image(frame, dir_captured_images): 
    global just_captured_image_path
    now = datetime.datetime.now()       # Get current date and time.
    current_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{current_datetime}.png"  # This will generate names like '2023-09-01_101530.jpg'
    just_captured_image_path = f"{dir_captured_images}\\{filename}"
    cv2.imwrite(just_captured_image_path, frame)
    print(f"Saved frame as {just_captured_image_path}")
    return just_captured_image_path


def calculate_blur_metric(frame):
    #frame = np.asarray(frame)
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur_metric = round(cv2.Laplacian(gray_image, cv2.CV_64F).var(),0)
    print('blur_metric_1:', blur_metric)
    return blur_metric




def crop_to_same_size(path_img_t1, path_img_t2):
    print('\n[crop_to_same_size] sometimes, sizes differ by a few pixels, causing issues.')

    # [1] Read images
    img1 = cv2.imread(path_img_t1)
    img2 = cv2.imread(path_img_t2)
    
    # [2] Check size
    img1_height, img1_width = img1.shape[:2]
    img2_height, img2_width = img2.shape[:2]
    
    # [3] Two images have the same size.
    if img1_width == img2_width and img1_height == img2_height:
        print('--Two images have the same size.', img1_width, ' x ', img1_height)
        path_img_t1_cropped = path_img_t1
        path_img_t2_cropped = path_img_t2
    
    # [4] Need to crop the image.
    else:
        print(f'--Two images have different sizes. Image_1: {img1_width}x{img1_height}; Image_2: {img2_width}x{img2_height}.')
        width_min = min(img1_width, img2_width)
        height_min = min(img1_height, img2_height)
        img1_cropped = img1[0:height_min, 0:width_min]
        img2_cropped = img2[0:height_min, 0:width_min]
        img1_height, img1_width = img1_cropped.shape[:2]
        img2_height, img2_width = img2_cropped.shape[:2]
        print(f'--After crop. Image_1: {img1_width}x{img1_height}; Image_2: {img2_width}x{img2_height}.')
        path_img_t1_cropped = path_img_t1.replace('.png', '_crop.png')
        path_img_t2_cropped = path_img_t2.replace('.png', '_crop.png')
        cv2.imwrite(path_img_t1_cropped, img1_cropped) 
        cv2.imwrite(path_img_t2_cropped, img2_cropped) 
        
    return path_img_t1_cropped, path_img_t2_cropped


def enhance_image(path_img, clipLimit, tileGridSize):
    #[1] Read image
    arrimg = cv2.imread(path_img, 1)
    if arrimg is None:
        print(f"Error: Image at {path_img} could not be loaded.")
        
    #[2] Enhance image
    lab = cv2.cvtColor(arrimg, cv2.COLOR_BGR2LAB) # Converting to LAB color space
    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(tileGridSize, tileGridSize)) # clipLimit = 2, tileGridSize = 8
    cl = clahe.apply(l_channel)
    limg = cv2.merge((cl, a, b)) # Merge the CLAHE enhanced L-channel with the a and b channel
    arrimg_enh = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR) # Converting from LAB Color model to BGR color space
    
    #[3] Save enhanced image.
    img_ext = os.path.splitext(path_img)[1] # Find file extension so that it works with different image files.
    path_img_enhanced = path_img.replace(img_ext, '_2-enh' + img_ext)
    cv2.imwrite(path_img_enhanced, arrimg_enh)
    #print('--Image enhanced:', os.path.basename(path_img_enhanced))
    return path_img_enhanced





def calculate_displacement_sift(img1, img2):
    print('\n[calculate_displacement_sift] (+x, +y) means img is moved right by x and down by y comparing with img1.')
    sift = cv2.SIFT_create()       # Initialize SIFT detector
    #[1] Detect SIFT features and compute descriptors.
    key_point_info = []
    keypoints1, descriptors1 = sift.detectAndCompute(img1, None)
    num_kpt_1 = len(keypoints1)
    key_point_info.append(num_kpt_1)
    keypoints2, descriptors2 = sift.detectAndCompute(img2, None)
    num_kpt_2 = len(keypoints2)
    key_point_info.append(num_kpt_2)
    print(f'--Number of keypoints in (img1, img2): {num_kpt_1}, {num_kpt_2}')
    
    #[2] Initialize and use FLANN matcher
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(descriptors1, descriptors2, k=2)
    
    #[3] Filter matches using the Lowe's ratio test
    good_matches, list_distance = [], []
    for best_match, second_match in matches:
        if best_match.distance < 0.6 * second_match.distance:
            good_matches.append(best_match)
            text = f"{best_match.distance:.2f}"
            list_distance.append(text)
                
    #[5] Calculate statistics and round to 3 decimal places
    list_distance = [float(distance) for distance in list_distance]
    stat_max = np.max(list_distance)
    stat_min = np.min(list_distance)
    stat_mean = np.mean(list_distance)
    stat_med = np.median(list_distance)
    stat_std = np.std(list_distance)
    stats_text = f'--  Max: {stat_max:.2f}, Mean: {stat_mean:.2f}, Min: {stat_min:.2f}\n--  Median: {stat_med:.2f}, STD: {stat_std:.2f}'
    print(f'\n--[Match Statistics]\n{stats_text}')
    
    #[6] Calculate displacement
    len_good_matches = len(good_matches)
    key_point_info.append(len_good_matches)
    print(f'--Number of good matches: {len_good_matches}\n')
    if len_good_matches > 0:
        src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches])
        dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches])
        #[8] Calculate displacement as average of all good matches
        displacement = np.mean(dst_pts - src_pts, axis=0)
        return displacement, key_point_info
    else:
        raise ValueError(f'Not enough number of matches. {len_good_matches}')
        return (0, 0)




# Auto focus
def plot_z_and_bluriness(list_z_position_um, list_blur_metrics, path_plot_save):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    plt.scatter(list_blur_metrics, list_z_position_um, color='blue')
    # Label each dot
    shift = 0.04 * (max(list_blur_metrics) - min(list_blur_metrics))
    for i, (x, y) in enumerate(zip(list_blur_metrics, list_z_position_um)):
        plt.text(x + shift, y, str(i), fontsize=12, ha='right')
    # Set y limit
    # Corrected to calculate limits properly
    y_range = max(list_z_position_um) - min(list_z_position_um)
    lim_max_y = max(list_z_position_um) + y_range * 0.2
    lim_min_y = min(list_z_position_um) - y_range * 0.2
    plt.ylim(lim_min_y, lim_max_y)
    # Set x limit
    # Corrected for proper calculation and rounding
    #lim_max_x = round(max(list_blur_metrics) * 1.2, -1) # Adjusted calculation for a clearer rounding logic
    #plt.xlim(left=min(list_blur_metrics), right=lim_max_x)
    x_range = max(list_blur_metrics) - min(list_blur_metrics)
    lim_max_x = max(list_blur_metrics) + x_range * 0.2
    lim_min_x = min(list_blur_metrics) - x_range * 0.2
    plt.xlim(lim_min_x, lim_max_x)
    
    
    plt.title('Scatter Plot of Blur Metrics vs Z Position')
    plt.xlabel('Blur Metrics')
    plt.ylabel('Z Position (um)')
    plt.grid(True)
    plt.savefig(path_plot_save)  # Save the plot before showing it
    plt.show()








# Blurriness


def cal_blur_1(frame):
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur_metric = round(cv2.Laplacian(gray_image, cv2.CV_64F).var(), 3)
    #print('Blur Metric:', blur_metric)
    return blur_metric

def cal_blur_2(frame):
    # Convert to grayscale, Define the Modified Laplacian kernel
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kernel = np.array([[-1, 2, -1],
                       [2, -4, 2],
                       [-1, 2, -1]])
    # Apply the kernel to the grayscale image
    laplacian_img = cv2.filter2D(gray_image, cv2.CV_64F, kernel)
    # Compute the variance of the Laplacian (which is the focus measure)
    mlv = laplacian_img.var()
    return mlv

def cal_blur_3(frame):
    # Optionally, resize the image to reduce noise and computation
    # frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    # Convert to grayscale, Apply Gaussian blur, Compute the Laplacian
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred_gray = cv2.GaussianBlur(gray_image, (3, 3), 0)
    laplacian = cv2.Laplacian(blurred_gray, cv2.CV_64F)
    # Optionally, apply a threshold to set small values to zero
    _, laplacian_thresh = cv2.threshold(laplacian, 0.001, 0.01, cv2.THRESH_TOZERO)
    # Calculate the variance of the Laplacian
    blur_metric = round(laplacian_thresh.var(), 3)*1000
    return blur_metric



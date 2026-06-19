"""
[ILH_fuction_bank.py]
Purpose: store function for ILH project.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import os, sys, xlsxwriter, cv2, shutil, shutil, random
import numpy as np
from PIL import Image
from treelib import Node, Tree
from datetime import datetime


#dir = r'D:\01_Floor\a_Ed\09_EECS\10_Python\05_Complete\[LLM API]'
dir = r'D:\01_Floor\a_Ed\09_EECS\10_Python\04_OngoingTools\2024-0328_Image Data Agmentation'


#[1] Image data augmentation - Start








def DataAug_flip_image(list_path, dir_output, bsn_original=None, bsn_H_flipped=None, bsn_V_flipped=None, bsn_HV_flipped=None):
    """
    If bsn_H_flipped is provided, it means user want horizontal flip.
    If bsn_V_flipped is provided, it means user want vertical flip.
    
    """
    print('\n[DataAug_flip_image]')
    list_path_flipped = []
    cnt_total = len(list_path)
    #[1] Iterate through list.
    for i, iter_path in enumerate(list_path):
        bsn_ext = os.path.basename(iter_path)
        bsn = os.path.splitext(bsn_ext)[0]
        ext = os.path.splitext(bsn_ext)[1]
        
        #[2] Read the image.
        img = cv2.imread(iter_path)
        print(f'\n[{i:04d}/{cnt_total:04d}] {bsn_ext}', end='')
        
        #[5] Move original images there.
        if bsn_original:
            path_original = os.path.join(dir_output, f'{bsn}_{bsn_original}{ext}')
            shutil.copy2(iter_path, path_original)
            print(f'\t{bsn_original}', end='')
        
        #[8] If need horizontal flip.
        if bsn_H_flipped:
            path_H_flipped = os.path.join(dir_output, f'{bsn}_{bsn_H_flipped}{ext}')
            H_flipped_img = cv2.flip(img, 1)  # Horizontal flip
            cv2.imwrite(path_H_flipped, H_flipped_img)
            list_path_flipped.append(path_H_flipped)
            print(f'\t{bsn_H_flipped}', end='')
            
        #[10] If need vertical flip.
        if bsn_V_flipped:
            path_V_flipped = os.path.join(dir_output, f'{bsn}_{bsn_V_flipped}{ext}')
            V_flipped_img = cv2.flip(img, 0)  # Vertical flip
            cv2.imwrite(path_V_flipped, V_flipped_img)
            list_path_flipped.append(path_V_flipped)
            print(f'\t{bsn_V_flipped}', end='')
            
        #[12] If need vertical flip.
        if bsn_HV_flipped:
            path_HV_flipped = os.path.join(dir_output, f'{bsn}_{bsn_HV_flipped}{ext}')
            HV_flipped_img = cv2.flip(V_flipped_img, 1)  # Horizontal flip
            cv2.imwrite(path_HV_flipped, HV_flipped_img)
            list_path_flipped.append(path_HV_flipped)
            print(f'\t{bsn_HV_flipped}', end='')
        
    return list_path_flipped


def precise_shrink_ratio(angle_deg):
    if angle_deg % 90 == 0:
        shrink_ratio = 1.0
    else:
        #[4] Calculate the shrink_ratio (SR) depends on the rotational angle. SR <= 1/(sin(theta)+cos(theta)).
        angle_deg_SR = angle_deg % 90
        shrink_ratio = 1 / (np.sin(np.deg2rad(angle_deg_SR)) + np.cos(np.deg2rad(angle_deg_SR)))
    return shrink_ratio


def DataAug_rotate_image(list_path, dir_output, limit_rotate=150, step_deg = 30):
    print('\n[DataAug_rotate_image]')
    list_path_rotated = []
    len_list_path = len(list_path)
    
    #[1] Iterate through list.
    for i, iter_path in enumerate(list_path):
        #[3] Check the shape of image.
        bsn_ext = os.path.basename(iter_path)
        bsn, ext = os.path.splitext(bsn_ext)
        arrimg = cv2.imread(iter_path)

        #[2] Read the image.
        h, w = arrimg.shape[:2]

        #[3] Rotate the image.
        for angle_deg in range(0, limit_rotate + 1, step_deg):  # Rotate from -limit_rotate to +limit_rotate with step of 10 degrees
            
            # [4] Calculate the shrink ratio depending on the rotation angle.
            shrink_ratio = precise_shrink_ratio(angle_deg)
            
            #[4] Compute the rotation matrix.
            center = (w // 2, h // 2)
            rot_matrix = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
            
            #[5] Perform the rotation.
            rotated_img = cv2.warpAffine(arrimg, rot_matrix, (w, h))

            #[6] Calculate the crop dimensions to avoid black edges.
            #shrink_ratio = 0.7 # Avoid black edge after rotation (0.7 < 1/sqrt(2) ~ 0.707)
            crop_size = round(shrink_ratio * min(h, w))
            start_x = (w - crop_size) // 2
            start_y = (h - crop_size) // 2
            cropped_img = rotated_img[start_y:start_y + crop_size, start_x:start_x + crop_size]
            
            #[7] Save the rotated and cropped image.
            path_rotated = os.path.join(dir_output, f'{bsn}_rot({angle_deg:+03d}){ext}')
            cv2.imwrite(path_rotated, cropped_img)
            list_path_rotated.append(path_rotated)
        
            print(f'[{i:04d}/{len_list_path:04d}] {bsn_ext}\tRotated by {angle_deg:+03d} degree. Shrink by {shrink_ratio:03f}.')
    
    return list_path_rotated


def DataAug_crop_image(list_path, ratio_shrink=0.7):
    print('\n[DataAug_crop_image]')
    list_path_cropped = []
    
    #[1] Iterate through list.
    for cnt, iter_path in enumerate(list_path):
        
        #[3] Check the shape of image.
        iter_dir = os.path.dirname(iter_path)
        bsn_ext = os.path.basename(iter_path)
        bsn, ext = os.path.splitext(bsn_ext)
        arrimg = cv2.imread(iter_path)
        
        #[4] Calculate cropping lengthes.
        h, w = arrimg.shape[:2]
        asp_ratio = h / w
        smaller_side = min (h, w)
        length = int(ratio_shrink *  smaller_side)
        shift_w = (w - length) // 2
        shift_h = (h - length) // 2
        print(f'[{cnt}] {bsn_ext} \t{asp_ratio}')
        
        #[7] For every non-square image, generate a largest center crop.
        if not asp_ratio == 1:
            length_ctr = int(smaller_side)
            shift_w_ctr = (w - length_ctr) // 2
            shift_h_ctr = (h - length_ctr) // 2
            if w < h:
                cropped_img = arrimg[shift_h_ctr:shift_h_ctr+length_ctr, 0:length_ctr]
            if h < w:
                cropped_img = arrimg[0:length_ctr, shift_w_ctr:shift_w_ctr+length_ctr]
            path_cropped = os.path.join(iter_dir, f'{bsn}_crop_ctr{ext}')
            cv2.imwrite(path_cropped, cropped_img)
            list_path_cropped.append(path_cropped)
        
        #[5] For a square image, crop four smaller square images in a 2x2 array.
        if asp_ratio < 1.1 and asp_ratio > 0.9:
            for i in range(2):
                for j in range(2):
                    shift_s = int(smaller_side - length)
                    x, y = j * shift_s, i * shift_s
                    cropped_img = arrimg[y:y+length, x:x+length]
                    path_cropped = os.path.join(iter_dir, f'{bsn}_crop_arr{i}{j}{ext}')
                    cv2.imwrite(path_cropped, cropped_img)
                    list_path_cropped.append(path_cropped)
        
        #[9] For a vertical image, crop three vertical smaller square images.
        elif w < h:
            for i in range(3):
                y = i * shift_h
                cropped_img = arrimg[y:y+length, shift_w:shift_w+length]
                path_cropped = os.path.join(iter_dir, f'{bsn}_crop_vert{i}{ext}')
                cv2.imwrite(path_cropped, cropped_img)
                list_path_cropped.append(path_cropped)
        
        #[15] For a horizontal image, crop three horizontal smaller square images.
        elif h < w:
            for i in range(3):
                x = i * shift_w
                cropped_img = arrimg[shift_h:shift_h+length, x:x+length]
                path_cropped = os.path.join(iter_dir, f'{bsn}_crop_horz{i}{ext}')
                cv2.imwrite(path_cropped, cropped_img)
                list_path_cropped.append(path_cropped)
    
    return list_path_cropped




def DataAug_exposure_adjustment(list_path, value, delete_original=True):
    print('\n[DataAug_exposure_adjustment]')
    list_path_adjusted = []
    len_list_path = len(list_path)
    
    #[1] Check value.
    value = int(value)
    if value not in [-30, 30]:
        raise ValueError(f'Set value as an integer within -30 to +30. Current value: {value}')
    
    #[2] Iterate through the list of paths.
    for i, iter_path in enumerate(list_path):
        #[3] Read the image.
        img = cv2.imread(iter_path)
        
        #[4] Convert the image to HSV color space.
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        #[5] Adjust the exposure (Value channel) by adding the specified value.
        v = cv2.add(v, value)
        
        #[6] Merge the adjusted channels back into an HSV image.
        adjusted_hsv = cv2.merge((h, s, v))
        
        #[7] Convert the HSV image back to BGR color space.
        adjusted_img = cv2.cvtColor(adjusted_hsv, cv2.COLOR_HSV2BGR)
        
        #[8] Save the adjusted image.
        iter_dir = os.path.dirname(iter_path)
        bsn_ext = os.path.basename(iter_path)
        bsn, ext = os.path.splitext(bsn_ext)
        path_adjusted = os.path.join(iter_dir, f'{bsn}_exp({value:+03d}){ext}')
        cv2.imwrite(path_adjusted, adjusted_img)
        list_path_adjusted.append(path_adjusted)
        
        # [9] Optionally delete the original file.
        if delete_original:
            os.remove(iter_path)
            print(f'Deleted original file: {iter_path}')
        
        print(f'[{i:04d}/{len_list_path:04d}] {bsn_ext}\tExposure adjusted by {value:+03d}')
    
    return list_path_adjusted



#[2] Image data augmentation - End










#[3] Image data adjustment - End

def DataAdj_crop_if_not_square(list_path):
    print('\n[DataAdj_crop_if_not_square]')
    list_path_cropped = []
    
    #[1] Iterate through list.
    for iter_path in list_path:
        ext = os.path.splitext(iter_path)[1]
        base_name = os.path.basename(iter_path).replace(ext, '')
        
        #[3] Check the shape of image.
        arrimg = cv2.imread(iter_path)
        h, w = arrimg.shape[:2]
        
        #[4] Check if it's a square image.
        if h == w:
            continue
        
        #[5] Calculate cropping lengths.
        smaller_side = min(h, w)
        shift_h = (h - smaller_side) // 2
        shift_w = (w - smaller_side) // 2
        
        #[6] Crop the image to make it square.
        if w < h:
            cropped_img = arrimg[shift_h:shift_h+smaller_side, 0:w]
        elif h < w:
            cropped_img = arrimg[0:h, shift_w:shift_w+smaller_side]
        
        #[7] Save the cropped image.
        path_cropped = iter_path.replace(f'{ext}', f'_{base_name}_square{ext}')
        cv2.imwrite(path_cropped, cropped_img)
        list_path_cropped.append(path_cropped)
    
    return list_path_cropped






def create_photo_collage(dir_image, column_width, row_height, size_reduction, dir_collage):
    """
    Create a photo collage from a list of image paths.
    If there are more than 100 images, create additional collages.
    If there are fewer than 100 images, leave the extra space black.
    Use the size of the first image as standard.
    Resize images if their size is not the same. Print an error and append to the error log.
    """
    print('\n[create_photo_collage]')
    
    #[1] Validate column_width and row_height.
    if not (10 <= column_width <= 25) or not (10 <= row_height <= 25):
        raise ValueError(f'Please keep column_width ({column_width}) and row_height ({row_height}) between 10 to 25.')
    if not (0.01 <= size_reduction <= 1):
        raise ValueError(f'Please keep size_reduction ({column_width})  between 0.01 to 1.')
    
    #[2] Get only image files.
    acceptable_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    list_path_img = [os.path.join(dir_image, f) for f in os.listdir(dir_image) if os.path.splitext(f)[1].lower() in acceptable_formats]
    
    if not list_path_img:
        raise ValueError(f'No image files found in {dir_image}.')
    
    #[3] Create text error log.
    timestamp = datetime.now().strftime('%Y-%m%d-%H%M%S')
    text_log = f'{timestamp}\n\n'
    
    #[4] Use the size of the first image as standard to create a blank canvas for the collage.
    path_img_1st = list_path_img[0]
    arrimg_1st = cv2.imread(path_img_1st)
    
    if arrimg_1st is None:
        raise ValueError(f'Could not read the first image: {path_img_1st}')
    
    #[5] Reduce size.
    h_standard, w_standard = int(arrimg_1st.shape[0] * size_reduction), int(arrimg_1st.shape[1] * size_reduction)
    h_collage, w_collage = h_standard * row_height, w_standard * column_width
    collage_canvas = np.zeros((h_collage, w_collage, 3), dtype=np.uint8)
    
    #[5] Calculate the number of collages needed.
    num_images = len(list_path_img)
    num_collages = (num_images + (column_width * row_height - 1)) // (column_width * row_height)

    #[6] Loop through each collage.
    for idx_collage in range(num_collages):
        collage_canvas[:] = 0  # Reset the collage canvas for each new collage
        
        #[7] Place images in the collage.
        for i in range(column_width * row_height):
            #[8] Calculate the position of the current image.
            row = i // column_width
            col = i % column_width
            
            #[9] Calculate the overall index of the image in the list.
            img_index = idx_collage * (column_width * row_height) + i
            
            #[10] If there are still images left to add, read and resize the image.
            if img_index < num_images:
                try:
                    img = cv2.imread(list_path_img[img_index])
                    if img is None:
                        raise ValueError("Failed to read image.")
                    img = cv2.resize(img, (w_standard, h_standard))
                except Exception as e:
                    error_message = f'--Error processing image: {list_path_img[img_index]}, Error: {str(e)}'
                    print(error_message)
                    text_log += f'{error_message}\n'
                    img = np.zeros((h_standard, w_standard, 3), dtype=np.uint8)
            else:
                #[11] If there are no more images, use a black square.
                img = np.zeros((h_standard, w_standard, 3), dtype=np.uint8)
            
            #[12] Place the image on the collage.
            collage_canvas[row*h_standard:(row+1)*h_standard, col*w_standard:(col+1)*w_standard] = img
        
        #[13] Save the collage.
        path_collage = os.path.join(dir_collage, f'collage_{idx_collage:02d}.png')
        cv2.imwrite(path_collage, collage_canvas)
        text = f'--Saved collage: {path_collage}'
        print(text)
        text_log += f'{text}\n'

    #[14] Save the error log.
    path_log = os.path.join(dir_collage, f'collage_creation_log_{timestamp}.txt')
    with open(path_log, 'w') as log_file:
        log_file.write(text_log)
    text = f'--Saved error log: {path_log}'
    print(text)




def resize_all_image_in_dir(dir_input, size_h_w, dir_output=None):
    """
    This function is used to prepare images for model training.
    From dir_input, get only image files, resize them to size_h_w, and save them to dir_output.
    If collage is True, create a collage of resized images.
    """
    print('\n[resize_all_image_in_dir]')
    #[1] Get only image files.
    acceptable_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    list_path_img = [os.path.join(dir_input, f) for f in os.listdir(dir_input) if os.path.splitext(f)[1].lower() in acceptable_formats]
    
    #[2] Name the saving directory if not provided.
    if dir_output is None:
        dir_output = os.path.join(os.path.dirname(dir_input), f'{os.path.basename(dir_input)}_2-Output')
    
    #[3] Make saving directory if it does not exist.
    try:
        os.mkdir(dir_output)
        print(f'--Directory did not exist. Created one: {dir_output}')
    except FileExistsError:
        print(f'--Directory already exists. Skipping directory creation: {dir_output}')
    
    #[4] Resize images to size_h_w.
    h_desired, w_desired = size_h_w
    for path_img in list_path_img:
        try:
            #[5] Read and resize the image.
            img = cv2.imread(path_img)
            img_resized = cv2.resize(img, (w_desired, h_desired))
            
            #[6] Save the resized image to the output directory.
            filename = os.path.basename(path_img)
            path_output = os.path.join(dir_output, filename)
            cv2.imwrite(path_output, img_resized)
            print(f'--Saved resized image: {path_output}')
        except Exception as e:
            print(f'--Error processing image: {path_img}, Error: {str(e)}')
    
    return dir_output




#[3] Image data adjustment - End





#[4] Image data distribution -StartEnd

def distribute_images_to_several_folders(dir_input, list_pct=[80, 20]):
    """
    Distributes images in dir_input into several folders randomly based on the given percentages.
    
    Parameters:
    dir_input (str): The input directory containing image data.
    list_pct (list): A list of percentages to divide the images (e.g., [80, 20]).
    """
    
    #[1] Check if list_pct sums up to 100%. 
    if sum(list_pct) != 100:
        raise ValueError("The percentages in list_pct must sum up to 100.")
    
    #[2] Get all image files from dir_input.
    acceptable_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    list_images = [f for f in os.listdir(dir_input) if os.path.splitext(f)[1].lower() in acceptable_formats]
    if not list_images:
        raise ValueError("No image files found in the input directory.")
    
    #[3] Set up directory paths.
    dir_up = os.path.dirname(dir_input)
    folder_name = os.path.basename(dir_input)
    timestamp = datetime.now().strftime("%Y-%m%d-%H%M%S")
    
    #[5] Create a list to hold directory paths and number of images to allocate to each
    dir_list = []
    num_images = len(list_images)
    total_allocated = 0
    
    for i, i_pct in enumerate(list_pct):
        num_to_allocate = int(num_images * (i_pct / 100))
        dir_list.append((os.path.join(dir_up, f'{folder_name}_{i+1}-{i_pct}pct_{timestamp}'), num_to_allocate))
        total_allocated += num_to_allocate
    
    # Adjust for any rounding errors by adding remaining images to the first folder
    remaining_images = num_images - total_allocated
    if remaining_images > 0:
        dir_list[0] = (dir_list[0][0], dir_list[0][1] + remaining_images)
    
    #[8] Make directories for distribution.
    for i_dir, _ in dir_list:
        os.makedirs(i_dir, exist_ok=True)
    
    #[10] Shuffle the image list for random distribution.
    random.shuffle(list_images)
    
    #[12] Distribute the images.
    current_idx = 0
    for i_dir, num_images in dir_list:
        images_to_copy = list_images[current_idx:current_idx + num_images]
        
        for img in images_to_copy:
            src_path = os.path.join(dir_input, img)
            dst_path = os.path.join(i_dir, img)
            shutil.copy(src_path, dst_path)
        
        current_idx += num_images
    
    print(f'Images have been distributed to the following directories:')
    for i_dir, num_images in dir_list:
        print(f'{i_dir}: {num_images} images')



#[4] Image data distribution - End






#[5] Image data Plot - Start



def plot_files_count_in_dir_and_subdir_with_keywords_in_bsn(dir, list_kwd_yes_or_1):
    print('\n[plot_files_count_in_dir_and_subdir_with_keywords_in_bsn] [file_count, dir_count]')
    #[1] Check if directory exists.
    if not os.path.isdir(dir):
        raise FileNotFoundError(f"The directory '{dir}' was not found.")    
    #[2] Count path separator.
    cnt_layer_base = dir.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(dir):
        cnt_layer_iter = dirpath.rstrip(os.sep).count(os.sep)
        layer_diff = cnt_layer_iter - cnt_layer_base
        # [3] Calculate file_count and dir_count here
        file_count = len(filenames)
        dir_count = len(dirnames)
        indent = '    |' * layer_diff if layer_diff > 0 else ''
        print(f'{indent}  └── {os.path.basename(dirpath)} [{file_count}, {dir_count}]')
    #[5] Mark finish
    print()
    


def plot_files_count_in_dir_and_subdir_with_keywords_in_bsn_old(dir, list_kwd_yes_or_1):
    print('\n[plot_files_count_in_dir_and_subdir_with_keywords_in_bsn]')
    #[1] Check if directory exists
    if not os.path.isdir(dir):
        raise FileNotFoundError(f"The directory '{dir}' was not found.")
    print(f'{os.path.basename(dir)}')

    #[2] Initialize a list to hold the counts
    int_total_kwd = len(list_kwd_yes_or_1)
    list_kwd_count = [0] * (int_total_kwd + 2)

    #[3] Create a Tree object to store the directory structure
    tree = Tree()
    tree.create_node(os.path.basename(dir) + " [0, 0]", dir)  # root node

    #[4] Walk through the directory and its subdirectories
    for dirpath, dirnames, filenames in os.walk(dir):
        parent_node = tree.get_node(dirpath)
        
        #[5] Update the directory count
        if parent_node:
                parent_node.data = [0, len(dirnames)]  # [file_count, dir_count]
                
                #[6] Iterate through filenames
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    no_match = 0
                    #[7] Iterate through keywords
                    for cnt_kwd, iter_kwd in enumerate(list_kwd_yes_or_1):
                            if iter_kwd in filename:
                                list_kwd_count[cnt_kwd] += 1
                            else:
                                no_match += 1
                    if no_match == int_total_kwd:
                            list_kwd_count[int_total_kwd] += 1
                    list_kwd_count[int_total_kwd + 1] += 1
                    parent_node.data[0] += 1  # increment file count

    #[8] Update node tags with updated counts
    for node in tree.all_nodes():
                if node.is_leaf() and node.data:
                    file_count, dir_count = node.data
                    node.tag = f"{os.path.basename(node.identifier)} [{file_count}, {dir_count}]"

    tree.show(line_type='ascii-ex', idhidden=False)
    return list_kwd_count
        
      
      
#[5] Image data Plot - End

      
      
      
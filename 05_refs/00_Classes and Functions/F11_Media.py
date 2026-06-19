"""
[F11_Media.py]
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
from datetime import datetime
from PIL import UnidentifiedImageError, Image, ExifTags

#[] For plot
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
import matplotlib.colors as colors


#[] For image




def delete_files_with_ext(directory, ext='.AAE'):
    """
    Deletes all files with a certain ext under a specified directory and its subdirectories, then count and report.
    Args:
    directory (str): The path to the directory where certain files will be searched and deleted.
    ext (str): The extension of the file. Case insensitive.
    """
    print('\n[delete_files_with_ext]:', ext)
    #[1] Initialize counters
    total_files_processed = 0
    total_files_found = 0
    total_folders_scanned = 0
    list_dir = []
    list_file_cnt = []
    list_match_cnt = []
    #[2] Walk through the directory and its subdirectories
    for dirpath, _dirnames, filenames in os.walk(directory):
        total_folders_scanned += 1
        sub_files_cnt = 0
        sub_files_match = 0
        list_dir.append(dirpath)
        for file in filenames:
            #[3] Check if the file ends with the specified ext (case insensitive)
            sub_files_cnt += 1
            if file.lower().endswith('.' + ext.lower()):
                file_path = os.path.join(dirpath, file)
                try:
                    os.remove(file_path) #This will remove the file.
                    print('--Remove file:', file_path)
                    total_files_processed += 1
                except Exception as e:
                    print(f"--Error deleting {file_path}: {e}")
                total_files_found += 1
                sub_files_match += 1
        list_file_cnt.append(sub_files_cnt)
        list_match_cnt.append(sub_files_match)
    #[4] Create dataframe.
    df_report = pd.DataFrame({'dir_folder': list_dir,
                               'file_cnt': list_file_cnt,
                               'match_cnt': list_match_cnt})
    return df_report




def datetime_string():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


def move_file_with_ext(dir_search, extension):
    print('\n[move_file_with_ext]:', extension)
    #[]  Initialize counters and lists
    total_files_processed = 0
    total_files_found = 0
    total_folders_scanned = 0
    list_dir = []
    list_file_cnt = []
    list_match_cnt = []
    #[] Create a directory as file destination
    dir_dest = os.path. join(dir_search, datetime_string())
    if not os.path.exists(dir_dest):
        os.makedirs(dir_dest)
    else:
        print(f"--Directory '{dir_dest}' already exists.")
    #[] Walk through the directory and its subdirectories
    for dir_search, _dir_found, file_found in os.walk(dir_search):
        total_folders_scanned += 1
        sub_files_cnt = 0
        sub_files_match = 0
        list_dir.append(dir_search)
        if dir_search == dir_dest: #Skip the destination directory that we just created.
            continue 
        for file in file_found:
            sub_files_cnt += 1
            #[] Check if the file ends with the specified extension (case insensitive)
            if file.lower().endswith('.' + extension.lower()):
                path_file_found = os.path.join(dir_search, file)
                path_file_dest = os.path.join(dir_dest, file)
                try:
                    os.replace(path_file_found, path_file_dest)
                    total_files_processed += 1
                except Exception as e:
                    print(f"--Error deleting {path_file_found}: {e}")
                total_files_found += 1
                sub_files_match += 1
        list_file_cnt.append(sub_files_cnt)
        list_match_cnt.append(sub_files_match)
    #[] Create dataframe.
    list_dir.remove(dir_dest)
    df_report = pd.DataFrame({'dir_folder': list_dir,
                               'file_cnt': list_file_cnt,
                               'match_cnt': list_match_cnt})
    #[] Delete the directory if its empty.
    if len(os.listdir(dir_dest)) == 0:
        os.rmdir(dir_dest)
        print(f"Just delete the temporary destination directory in '{dir_dest}' because we didn't find any file with the extension of {extension}.")
    return df_report, dir_dest



def distory_directory(dir):
    try:
        shutil.rmtree(dir)
        print(f"--Directory '{dir}' and all its contents have been deleted.")
    except FileNotFoundError:
        print(f"--Directory '{dir}' does not exist.")
    except Exception as e:
        print(f"--An error occurred: {e}")
        
        
"""
Obsolete, already updated into: search_oversize_files_in_dir_and_subdir in MD1_Utilities.py.
"""
def search_oversize_files(directory, Mb_limit):
    print('\n[search_oversize_files]:', Mb_limit, 'Mb')
    #[1] Initialize counters
    total_files_found = 0
    total_folders_scanned = 0
    list_dir = []
    list_file_cnt = []
    list_match_cnt = []
    
    #[2] Walk through the directory and its subdirectories
    for dirpath, _dirnames, filenames in os.walk(directory):
        total_folders_scanned += 1
        sub_files_cnt = 0
        sub_files_match = 0
        list_dir.append(dirpath)
        for file in filenames:
            
            # Check if the file ends with the specified extension (case insensitive)
            sub_files_cnt += 1
            file_path = os.path.join(dirpath, file)
            file_size_MB = os.path.getsize(file_path)/1048576
            if file_size_MB > float(Mb_limit):
                total_files_found += 1
                sub_files_match += 1
        list_file_cnt.append(sub_files_cnt)
        list_match_cnt.append(sub_files_match)
        
    #[3] Create dataframe.
    df_report = pd.DataFrame({'dir_folder': list_dir,
                               'file_cnt': list_file_cnt,
                               'match_cnt': list_match_cnt})
    return df_report




def files_in_dir(directory):
    list_basenames = []
    list_size_kb = []
    list_front_bsn = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            basename = os.path.basename(item)
            list_basenames.append(basename)
            size_kb = os.path.getsize(item_path)/1024
            list_size_kb.append(size_kb)
            front_bsn = basename.split('.')[0].split(' ')[0]
            list_front_bsn.append(front_bsn)
    counts = pd.Series(list_front_bsn).value_counts()

    # Filter out names that occur only once
    counts = counts[counts >= 2]
    # Create a DataFrame from the filtered counts
    df_duplicates = pd.DataFrame({'Name': counts.index, 'Count': counts.values})
    
    return list_basenames, list_front_bsn, df_duplicates




def files_in_dir_1(directory):
    list_basenames = []
    list_size_kb = []
    list_front_bsn = []
    front_bsn_to_sizes = {}  # New dictionary to hold file sizes for each front_bsn

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            basename = os.path.basename(item)
            size_kb = int(os.path.getsize(item_path) / 1024)
            front_bsn = basename.split('.')[0].split(' ')[0]

            list_basenames.append(basename)
            list_size_kb.append(size_kb)
            list_front_bsn.append(front_bsn)

            # Add the file size to the corresponding front_bsn entry in the dictionary
            if front_bsn in front_bsn_to_sizes:
                front_bsn_to_sizes[front_bsn].append(size_kb)
            else:
                front_bsn_to_sizes[front_bsn] = [size_kb]

    counts = pd.Series(list_front_bsn).value_counts()

    # Filter out names that occur only once
    counts = counts[counts >= 2]

    # Create a DataFrame from the filtered counts
    df_duplicates = pd.DataFrame({'Name': counts.index, 'Count': counts.values})

    # Add a new column for sizes of duplicates
    df_duplicates['sizes_of_duplicates'] = df_duplicates['Name'].apply(lambda x: ', '.join(map(str, front_bsn_to_sizes[x])))

    #[] Find the full basename of the largest duplicate.
    list_dup_front_bsn = df_duplicates['Name']
    list_dup_max_file = []
    for iter_dup in list_dup_front_bsn:
        list_file_names = [item for item in os.listdir(directory) if iter_dup in item]
        print(list_file_names)
        list_dup_size = []
        for iter_dup_file in list_file_names:
            path_file = os.path.join(directory, iter_dup_file)
            size_kb = int(os.path.getsize(path_file) / 1024)
            list_dup_size.append(size_kb)
        max_value = max(list_dup_size)
        max_index = list_dup_size.index(max_value)
        dup_max_file = list_file_names[max_index]
        list_dup_max_file.append(dup_max_file)
    print(list_dup_max_file)
    df_duplicates['largest dup'] = list_dup_max_file

    return list_basenames, list_front_bsn, df_duplicates







def retrieve_datetime_of_single_media_files(path_media, 
                                            datetime_format = '%Y-%m-%d, %H:%M:%S'):
    #[2] Get file extension
    bsn_ext = os.path.basename(path_media)
    bsn, ext = os.path.splitext(bsn_ext)
    ext = ext.upper()
    
    #[3] Check file type for image
    if ext in ['.JPG', '.JPEG', '.PNG', '.GIF']:
        try:
            media_datetime = datetime.strptime(Image.open(path_media)._getexif()[36867], 
                                                '%Y:%m:%d %H:%M:%S').strftime(datetime_format)
            method = '[1] get_date_taken'
        except (KeyError, UnidentifiedImageError, TypeError, AttributeError):
            media_datetime = datetime.fromtimestamp(os.path.getmtime(path_media)).strftime(datetime_format)
            method = '[2] os.path.getmtime(image)'
    
    #[4] Check file type for video
    elif ext in ['.MP4', '.MOV']:
        media_datetime = datetime.fromtimestamp(os.path.getmtime(path_media)).strftime(datetime_format)
        method = '[3] os.path.getmtime(video)'
    
    #[5] Handle unknown file types
    else:
        media_datetime, method = None, None
        print(f'Unknown file type {bsn_ext}, usually AEE.')
    return ext, media_datetime, method


def retrieve_datetime_from_list_of_media_files(list_path_media, 
                                               print_status=False, 
                                               datetime_format = '%Y-%m-%d, %H:%M:%S'):
    #[1] Initiate lists.
    cnt_total = len(list_path_media)
    list_media_datetime = []
    list_media_ext = []
    list_method = []
    
    for i, iter_path in enumerate(list_path_media):
        #[3] Get datetime from media file
        ext, media_datetime, method = retrieve_datetime_of_single_media_files(iter_path, datetime_format)
        
        #[6] Collect into lists.
        list_media_datetime.append(media_datetime)
        list_media_ext.append(ext)
        list_method.append(method)
        
        #[6] Optionally print status.
        if print_status:
            print(f'-- [{i:04d}/{cnt_total:04d}] \t{media_datetime}, \t{os.path.basename(iter_path)}, \t{method}.')
    
    return list_media_datetime, list_media_ext, list_method






#[1] Code for timer.
start_time = time.time()
end_time = time.time()
print(f'Execution Time (read data): \t{end_time - start_time:.3f} seconds.')




"""
[F22_Renaming.py]
Purpose: store function for ILH project.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import sys, os, openpyxl, tkinter, shutil
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog


#[3] File renaming - Start

def numbering_filenames_with_prefix_and_suffix(list_path, prefix='T_', suffix='0', first_number=0, dir_output=None):
    list_path_renamed = []
    list_bsnext_renamed = []
    
    # [2] Check if first_number is an integer.
    first_number = int(first_number)
    if not isinstance(first_number, int):
        raise ValueError(f'first_number ({first_number}) must be an integer.')
    
    # [3] Rename files.
    for cnt, i_path in enumerate(list_path):
        dir_name = os.path.dirname(i_path)
        bsn_ext = os.path.basename(i_path)
        bsn, ext = os.path.splitext(bsn_ext)
        cnt += first_number
        new_bsnext = f'{prefix}{cnt:04d}{suffix}{ext}'
        new_path = os.path.join(dir_name, new_bsnext)

        #[5] Check for name conflict
        if os.path.exists(new_path):
            raise FileExistsError(f'The file {new_path} already exists.')

        #[8] If dir_output is provided, copy file with new names to dir_output.
        if dir_output:
            if not os.path.exists(dir_output):
                os.makedirs(dir_output)
                
            new_path = os.path.join(dir_output, new_bsnext)
            shutil.copy(i_path, new_path)
            print(f'[{cnt}] Copy \t"{bsn_ext}" to \t"{new_path}".')
            list_path_renamed.append(new_path)
            list_bsnext_renamed.append(new_bsnext)
        
        #[10] Otherwise, rename the file in the original path.
        else:
            os.rename(i_path, new_path)
            print(f'[{cnt}] Rename \t"{bsn_ext}" to \t"{new_bsnext}".')
            list_path_renamed.append(new_path)
            list_bsnext_renamed.append(new_bsnext)
    
    return list_path_renamed, list_bsnext_renamed


def add_prefix_and_suffix_to_filenames(list_path, prefix='T_', suffix='0', dir_output=None):
    list_path_renamed = []
    list_bsnext_renamed = []
     
    # [3] Rename files.
    for cnt, i_path in enumerate(list_path):
        dir_name = os.path.dirname(i_path)
        bsn_ext = os.path.basename(i_path)
        bsn, ext = os.path.splitext(bsn_ext)
        new_bsnext = f'{prefix}{bsn}{suffix}{ext}'
        
        #[4] Determine the new path
        if dir_output:
            new_path = os.path.join(dir_output, new_bsnext)
        else:
            new_path = os.path.join(dir_name, new_bsnext)

        #[5] Check for name conflict
        if os.path.exists(new_path):
            raise FileExistsError(f'The file {new_path} already exists.')

        #[8/10] Copy or rename the file.
        if dir_output:
            shutil.copy(i_path, new_path)
            print(f'[{cnt}] Copy \t"{bsn_ext}" to \t"{new_path}".')
        else:
            os.rename(i_path, new_path)
            print(f'[{cnt}] Rename \t"{bsn_ext}" to \t"{new_bsnext}".')
        
        list_path_renamed.append(new_path)
        list_bsnext_renamed.append(new_bsnext)
    
    return list_path_renamed, list_bsnext_renamed


def replace_certain_string_in_filenames(list_path, str_old='T', str_new='T_', dir_output=None):
    list_path_renamed = []
    list_bsnext_renamed = []
    
    #[1] Ensure output directory exists if specified
    if dir_output and not os.path.exists(dir_output):
        os.makedirs(dir_output, exist_ok=True)
    
    #[3] Rename files.
    for cnt, i_path in enumerate(list_path):
        dir_name = os.path.dirname(i_path)
        bsn_ext = os.path.basename(i_path)
        new_bsnext = bsn_ext.replace(str_old, str_new)
        
        #[4] Determine the new path
        new_path = os.path.join(dir_output if dir_output else dir_name, new_bsnext)

        #[5] Check for name conflict. Case insensitive.
        if os.path.exists(new_path):
            print((f'File already exists: {new_path}'))
            raise FileExistsError(f'The file {new_path} already exists.')

        #[8] Copy or rename the file.
        if dir_output:
            shutil.copy(i_path, new_path)
            print(f'[{cnt}] Copy \t"{bsn_ext}" to \t"{new_path}".')
        else:
            os.rename(i_path, new_path)
            print(f'[{cnt}] Rename \t"{bsn_ext}" to \t"{new_bsnext}".')
        
        list_path_renamed.append(new_path)
        list_bsnext_renamed.append(new_bsnext)
    
    return list_path_renamed, list_bsnext_renamed


def replace_certain_pattern_in_filenames(list_path, str_start, str_end, str_new, dir_output=None):
    list_path_renamed = []
    list_bsnext_renamed = []
    
    # [1] Ensure output directory exists if specified
    if dir_output and not os.path.exists(dir_output):
        os.makedirs(dir_output, exist_ok=True)
    
    # [3] Rename files.
    for cnt, i_path in enumerate(list_path):
        dir_name = os.path.dirname(i_path)
        bsn_ext = os.path.basename(i_path)
        
        # [4] Find and replace pattern in filename
        start_index = bsn_ext.find(str_start) + len(str_start)
        end_index = bsn_ext.find(str_end, start_index)
        
        if start_index != -1 and end_index != -1:
            old_pattern = bsn_ext[start_index:end_index]
            new_bsnext = bsn_ext.replace(old_pattern, str_new)
        else:
            # If the pattern is not found, keep the original filename
            new_bsnext = bsn_ext
        
        # [5] Determine the new path
        new_path = os.path.join(dir_output if dir_output else dir_name, new_bsnext)

        # [6] Check for name conflict
        if os.path.exists(new_path):
            raise FileExistsError(f'The file {new_path} already exists.')

        # [8/10] Copy or rename the file.
        if dir_output:
            shutil.copy(i_path, new_path)
            print(f'[{cnt}] Copy "{bsn_ext}" to "{new_path}".')
        else:
            os.rename(i_path, new_path)
            print(f'[{cnt}] Rename "{bsn_ext}" to "{new_bsnext}".')
        
        list_path_renamed.append(new_path)
        list_bsnext_renamed.append(new_bsnext)
    
    return list_path_renamed, list_bsnext_renamed


def renumbering_certain_pattern_in_filenames(list_path, str_start='T', str_end='_', first_number=0, dir_output=None):
    list_path_renamed = []
    list_bsnext_renamed = []
    
    # [2] Check if first_number is an integer.
    first_number = int(first_number)
    if not isinstance(first_number, int):
        raise ValueError(f'first_number ({first_number}) must be an integer.')
    
    # [3] Rename files.
    for cnt, i_path in enumerate(list_path):
        dir_name = os.path.dirname(i_path)
        bsn_ext = os.path.basename(i_path)
        
        #[4] Find and replace the number pattern in filename
        start_index = bsn_ext.find(str_start) + len(str_start)
        end_index = bsn_ext.find(str_end, start_index)
        
        #[5] Check if the pattern is found.
        if start_index != -1 and end_index != -1:
            new_number = f'{first_number + cnt:04d}'
            new_bsnext = bsn_ext[:start_index] + new_number + bsn_ext[end_index:]
        else:
            #[6] If the pattern is not found, keep the original filename
            new_bsnext = bsn_ext
        
        # [7] Determine the new path
        if dir_output:
            # Create dir_output if it doesn't exist
            if not os.path.exists(dir_output):
                os.makedirs(dir_output)
            new_path = os.path.join(dir_output, new_bsnext)
        else:
            new_path = os.path.join(dir_name, new_bsnext)

        # [8] Check for name conflict if dir_output is provided
        if os.path.exists(new_path) and dir_output is not None:
            raise FileExistsError(f'The file {new_path} already exists.')

        # [10] Copy or rename the file.
        if dir_output:
            shutil.copy(i_path, new_path)
            print(f'[{cnt}] Copy \t"{bsn_ext}" to \t"{new_path}".')
        else:
            os.rename(i_path, new_path)
            print(f'[{cnt}] Rename \t"{bsn_ext}" to \t"{new_bsnext}".')
        
        list_path_renamed.append(new_path)
        list_bsnext_renamed.append(new_bsnext)
    
    return list_path_renamed, list_bsnext_renamed

#[3] File renaming - End




#[4] File Check - Start       

def find_files_match_single_keyword(dir_folder, str_keyword, print_first_n_founds = 0):
    print(f'\n[find_files_match_single_keyword] dir_folder = {dir_folder}')
    #[1] Check if directory exists
    if not os.path.isdir(dir_folder):
        raise FileNotFoundError(f'The directory {dir_folder} was not found.')
    
    #[2] Get list of files in the directory, no folders.
    list_bsns = [file for file in os.listdir(dir_folder) if os.path.isfile(os.path.join(dir_folder, file))]
    cnt_total = len(list_bsns)
    
    #[3] Filter names by the single keyword
    list_bsns = [file for file in list_bsns if str_keyword in file]
    
    #[4] Generate file paths
    list_paths = [os.path.join(dir_folder, file) for file in list_bsns]
    cnt_match = len(list_bsns)
    
    #[5] Report and print.
    print(f'-- Count (found/total): {cnt_match} / {cnt_total}')
    if print_first_n_founds > 0:
        print(f'-- Listing first {print_first_n_founds} items:')
        limited_list = list_bsns[:print_first_n_founds]
        cnt = len(limited_list)
        for i, i_bsn in enumerate(limited_list):
            print(f'[{i+1:03d}/{cnt:03d}] \t{i_bsn}')
    
    return list_paths, list_bsns, cnt_match



def find_files_match_pattern(dir_folder, str_start, str_end, print_first_n_founds = 0):
    print(f'\n[find_files_match_pattern] dir_folder = {dir_folder}')
    #[1] Check if directory exists
    if not os.path.isdir(dir_folder):
        raise FileNotFoundError(f'The directory {dir_folder} was not found.')
    
    #[2] Get list of files in the directory, no folders.
    list_bsns = [file for file in os.listdir(dir_folder) if os.path.isfile(os.path.join(dir_folder, file))]
    cnt_total = len(list_bsns)
    
    #[3] Filter names by str_start and str_end, regardless of string in between.
    list_bsns = [file for file in list_bsns if file.startswith(str_start) and file.endswith(str_end)]
    
    #[4] Generate file paths
    list_paths = [os.path.join(dir_folder, file) for file in list_bsns]
    cnt_match = len(list_bsns)
    
    #[5] Report and print.
    print(f'-- Count (found/total): {cnt_match} / {cnt_total}')
    if print_first_n_founds > 0:
        print(f'-- Listing first {print_first_n_founds} items:')
        limited_list = list_bsns[:print_first_n_founds]
        cnt = len(limited_list)
        for i, i_bsn in enumerate(limited_list):
            print(f'[{i+1:03d}/{cnt:03d}] \t{i_bsn}')
    
    return list_paths, list_bsns, cnt_match





            


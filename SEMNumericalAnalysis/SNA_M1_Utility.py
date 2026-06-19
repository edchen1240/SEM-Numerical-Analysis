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
import os, sys, cv2, openpyxl, shutil
import numpy as np
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt



#[1] File - Start


def make_dir_if_not_exist(dir_to_make=None):
    #[1] If dir_to_make is not provided, make a dir at current directory with timestamp as folder name.
    if dir_to_make is None:
        dir_current = os.path.dirname(os.path.abspath(__file__))
        timestamp = datetime.now().strftime("%Y-%m%d-%H%M%S")
        dir_to_make = os.path.join(dir_current, f'{timestamp}_dir_name')
        
    #[2] Make dir.
    try:
        os.mkdir(dir_to_make)
        print("--Directory wasn't exists. Just made one.")
    except FileExistsError:
        print("--Directory already exists. Skipping directory creation.")


def filter_file_in_dir_with_keywords(dir_folder, list_kwd_yes_or_1=[], list_kwd_no_or_2=[], print_bsn = False):
    print(f'\n[filter_file_in_dir_with_keywords] dir_folder = {dir_folder}')
    #[1] Check if directory exists
    if not os.path.isdir(dir_folder):
        raise FileNotFoundError(f'The directory {dir_folder} was not found.')
    
    #[2] Get list of files in the directory, no folders.
    list_bsns = [file for file in os.listdir(dir_folder) if os.path.isfile(os.path.join(dir_folder, file))]
    cnt_before = len(list_bsns)
    
    #[3] Filter names by keywords to select
    if list_kwd_yes_or_1 != []:
        list_bsns = [file for file in list_bsns if any(keyword in file for keyword in list_kwd_yes_or_1)]
    
    #[4] Filter names by keywords to discard
    if list_kwd_no_or_2 != []:
        list_bsns = [file for file in list_bsns if not any(keyword in file for keyword in list_kwd_no_or_2)]
        
    #[5] Generate file paths and orint
    list_paths = [os.path.join(dir_folder, file) for file in list_bsns]
    cnt_after = len(list_bsns)
    if print_bsn:
        print(f'\n--  Count (before, after) = {cnt_before}, {cnt_after}. list_bsns: \n{list_bsns}', end='\n\n')
    return list_paths, list_bsns



def batch_file_relocate(dir_folder, list_kwd_yes_or_1=[], list_kwd_no_or_2=[], dump_folder_name='01_dump', print_bsn=False):
    print('\n[batch_file_relocate]')
    
    #[1] Filter files
    list_paths, list_bsns = filter_file_in_dir_with_keywords(dir_folder, list_kwd_yes_or_1, list_kwd_no_or_2, print_bsn)
    cnt = len(list_paths)
    if cnt == 0:
        print(f'There is nothing we need to move. File count = {cnt}.')
        return [], []
    
    #[2] Create a dump folder if it does not exist
    dir_dump = os.path.join(dir_folder, dump_folder_name)
    if not os.path.exists(dir_dump):
        os.mkdir(dir_dump)
        print("--Directory didn't exist. Just created one.")
    else:
        print("--Directory already exists. Skipping directory creation.")
    
    #[4] Iterate through file list to move files
    for iter_file in list_paths:
        file_name = os.path.basename(iter_file)
        destination_path = os.path.join(dir_dump, file_name)
        
        #[5] Move the file and handle potential naming conflicts
        try: 
            shutil.move(iter_file, destination_path)
            
        except PermissionError:
            print(f'File {file_name} shown permission denied. Please close the file and press Enter to continue.')
            input()  # Wait for user to close the file
            shutil.move(iter_file, destination_path)
            
        except shutil.Error:
            bsn_ext = os.path.splitext(file_name)
            suffix = 1
            new_file_name = f'{bsn_ext[0]}_dup{suffix}{bsn_ext[1]}'
            new_destination_path = os.path.join(dir_dump, new_file_name)
            
            while os.path.exists(new_destination_path):
                suffix += 1
                new_file_name = f'{bsn_ext[0]}_dup{suffix}{bsn_ext[1]}'
                new_destination_path = os.path.join(dir_dump, new_file_name)
            
            shutil.move(iter_file, new_destination_path)
    
    #[6] Final report
    if print_bsn:
        print(f'--  Finish moving {cnt} files. list_bsns: \n{list_bsns}\n\n')
    
    return list_paths, list_bsns






def get_working_dir_from_sysargv():
    dir_working, dir_bsn = None, None
    #[1] Retrieve the working directory from command-line arguments
    #print(f'sys.argv = {sys.argv}')
    
    if len(sys.argv) < 2:
        raise ValueError(f'\n-- No working directory provided from sys.argv:\n{sys.argv}\n-- Use the existing dir_img_folder in code.')
    elif 'ipykernel_launcher.py' in sys.argv[0]:
        raise ValueError('\n-- Detected ipynb environment. Please provide dir_working manually in the code.')
    else:
        raw = sys.argv[1]
        #[3] sanitize: trim whitespace and remove surrounding quotes (handles cases like ...SARD-03_launchers")
        if isinstance(raw, str):
            raw = raw.strip()
            if raw[0] in ['"', "'"]:
                raw = raw[1:]
            if raw[-1] in ['"', "'"]:
                raw = raw[:-1]
        dir_working = os.path.normpath(raw)
        timestamp = datetime.now().strftime("%Y-%m%d-%H%M%S")
        print(f'-- [{timestamp}] Working directory received: \n{dir_working}')
        dir_bsn = os.path.basename(dir_working)
        
    return dir_working, dir_bsn







def fully_remove_previous_test_files(dir_img_folder, prep_for_stage = 'coverage'):
    """
    list_keywords_to_keep will override list_keywords_to_dump.
    """
    
    #[1] Remove files that will be generated by coarse_matching stage and fine_matching stage. Must keep the original images.
    if prep_for_stage == 'coverage':
        list_keywords_to_dump = ['mblr', 'enhc', 'binary', 'histg']
        list_keywords_to_keep = ['.bat', 'note']


    else:
        raise ValueError(f'\n⚠️[Error] Invalid prep_for_stage: {prep_for_stage}. Please check the code and provide a valid stage name.')
    
    
    
    #[4] Filter files.    
    list_paths_to_remove, list_bsn_to_remove \
        = filter_file_in_dir_with_keywords(dir_img_folder, list_keywords_to_dump, list_keywords_to_keep, print_bsn=False)

    #[5] If no files neede to be removed.
    if len(list_paths_to_remove) == 0:
        #print('\n(Nothing need to be removed.)')
        return None

    #[8] Create dir_dump and move files.
    dir_dump = os.path.join(dir_img_folder, '00_dump')
    os.makedirs(dir_dump, exist_ok=True)
    list_path_files_relocate(list_paths_to_remove, dir_dump)
    
    return list_paths_to_remove
    


def list_path_files_relocate(list_path, dir_dest):
    #[1] Make directory
    make_dir_if_not_exist(dir_dest)
    #[2] Iterate through the file list to move files
    for i_path in list_path:
        relocate_single_file(i_path, dir_dest)




def relocate_single_file(i_old_path, dir_new):
    file_name = os.path.basename(i_old_path)
    destination_path = os.path.join(dir_new, file_name)

    #[2] Move the file and handle potential naming conflicts
    try: 
        shutil.move(i_old_path, destination_path)
        
    #[3] Handle the cases if file already exists.
    except shutil.Error:
        bsn_ext = os.path.splitext(file_name)
        suffix = 1
        new_file_name = f'{bsn_ext[0]}_dup{suffix}{bsn_ext[1]}'
        new_destination_path = os.path.join(dir_new, new_file_name)

        while os.path.exists(new_destination_path):
            suffix += 1
            new_file_name = f'{bsn_ext[0]}_dup{suffix}{bsn_ext[1]}'
            new_destination_path = os.path.join(dir_new, new_file_name)

        shutil.move(i_old_path, new_destination_path)




#[1] File - End





#[5] Excel - Start


def save_df_as_excel_overwrite(df, path_xlsx, sheet_name):
    print('\n[save_df_as_excel_overwrite]')
    #[1] Make dir if not exist.
    dir_excel = os.path.dirname(path_xlsx)
    if not os.path.exists(dir_excel):
        os.makedirs(dir_excel)

    #[2] Use openpyxl to preserve existing sheets
    if os.path.exists(path_xlsx):
        with pd.ExcelWriter(path_xlsx, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=True)
    else:
        with pd.ExcelWriter(path_xlsx, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=True)
            
    print(f'--Dataframe saved to {path_xlsx} in sheet {sheet_name}', end='\n\n')


def adjust_multiple_column_widths(path_xlsx, sheet_name, list_column_letters, list_column_widths):
    print('\n[adjust_multiple_column_widths]')
    #[1] Check if list_column_letters and list_column_widths have the same length
    if len(list_column_letters) != len(list_column_widths):
        raise TypeError('The length of list_column_letters and list_column_widths are different, please check.')
    workbook = openpyxl.load_workbook(path_xlsx)
    
    #[2] Check if sheet_name exist
    if sheet_name not in workbook.sheetnames:
        print(f"--Sheet '{sheet_name}' does not exist in the workbook.")
        return
    worksheet = workbook[sheet_name]
    
    #[3] Adjust column width
    for col_letter, col_width in zip(list_column_letters, list_column_widths):
        worksheet.column_dimensions[col_letter].width = col_width
        print(f"--Column '{col_letter}' in sheet '{sheet_name}' has been adjusted to width {col_width}.")
    workbook.save(path_xlsx)
    print("--All specified columns have been adjusted.", end='\n\n')

def adjust_multiple_column_to_pct(path_xlsx, sheet_name, list_column_letters):
    print('\n[adjust_multiple_column_to_pct]')
    
    #[1] Load the workbook and worksheet, check if sheet exists
    workbook = openpyxl.load_workbook(path_xlsx)
    if sheet_name not in workbook.sheetnames:
        print(f"--Sheet '{sheet_name}' does not exist in the workbook.")
        return
    worksheet = workbook[sheet_name]
    
    #[2] Loop through each specified column and set the cell format to percentage
    for col_letter in list_column_letters:
        for cell in worksheet[col_letter]:
            if isinstance(cell.value, (int, float)):  # Only apply to numeric cells
                cell.number_format = '0.000%'  # Adjust as needed for decimal places
                print(f"--Cell '{cell.coordinate}' set to percentage format.")

    #[3] Save the workbook after adjustments
    workbook.save(path_xlsx)
    print("--All specified columns have been adjusted to percentage format.", end='\n\n')






def read_excel_into_df(path_xlsx, sheet_name=None):
    print('\n[read_excel_into_df]')
    if sheet_name is None:
        sheet_name = 0  # Assuming 0 is the index of the first sheet
    df = pd.read_excel(path_xlsx, sheet_name=sheet_name)
    print('--[dataframe headers]', df.head())
    return df

def find_scale_excel_file_in_folder(dir_find):
    #[1] Filter file.
    list_kwd_yes_or_1 = ['scale', '.xlsx']
    list_kwd_no_or_2 = []
    list_paths, list_bsns = filter_file_in_dir_with_keywords(dir_find, list_kwd_yes_or_1, list_kwd_no_or_2, print_bsn=False)

    #[2] Found more than one.
    if len(list_bsns) >= 2:
        print(f'-- More than one scale excel file was found ({len(list_bsns)}). Use the latest one.')
        
        #[3] Rank the list_paths by modification time
        list_paths.sort(key=os.path.getmtime, reverse=True)  # Sort by modification time, latest first
        path_scale_xlsx = list_paths[0]  # Select the latest file
        print(f'Using the latest scale excel file: {path_scale_xlsx}')

    else:
        path_scale_xlsx = list_paths[0]
        print(f'-- Using the found scale excel file: {path_scale_xlsx}')

    return path_scale_xlsx
        


def add_text_after_the_last_row_in_an_excel_sheet(path_xlsx, sheet_name, text_to_add, row_gap=1, col='A'):
    """
    On the specific Excel sheet, find the last row plus row_gap, and add text at column col.
    """
    print(f'\n[add_text_after_the_last_row_in_an_excel_sheet]')
    
    #[1] Load workbook, Use the first sheet if sheet_name is None.
    workbook = openpyxl.load_workbook(path_xlsx)
    if sheet_name is None:
        sheet_name = 0

    #[3] Access the sheet
    sheet = workbook[sheet_name] if isinstance(sheet_name, str) else workbook.worksheets[sheet_name]
    
    #[4] Find the last row plus row_gap
    target_row = sheet.max_row + row_gap + 1

    #[6] Split the text by newlines (\n)
    list_rows = text_to_add.split('\n')

    #[7] Iterate over each line of the text
    for row_index, row_text in enumerate(list_rows):
        # Determine the actual row to write to
        current_row = target_row + row_index
        
        # Split the row_text by tabs (\t) to determine cell contents
        list_cells = row_text.split('\t')
        
        # Iterate over each cell and write the text to the appropriate column
        for col_index, cell_text in enumerate(list_cells):
            # Calculate the column (starting from the given col)
            current_col = openpyxl.utils.cell.column_index_from_string(col) + col_index
            col_letter = openpyxl.utils.get_column_letter(current_col)
            
            # Write the text to the current cell
            sheet[f'{col_letter}{current_row}'] = cell_text

    #[8] Save the workbook
    workbook.save(path_xlsx)
    print(f"Text added to sheet '{sheet_name}', starting at column '{col}' and row {target_row}.")
    
    
#[5] Excel - End

    
    
    
    
    
    
    
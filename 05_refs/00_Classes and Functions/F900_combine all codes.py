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
import os, sys, cv2, datetime, serial, time, glob, shutil, json
import numpy as np
import pandas as pd
from datetime import datetime
from tabulate import tabulate
import F04_EXLDF as F04_EXLDF

"""
1.  A function that combine all the python files in current directory into a single python file.
    Add file name as comment in between each lines.

2.  A function that walk through every python files in the directory, copy the line starting with "def" until ":", and paste them into a dataframe.
    function, filename, path_file

"""




def combine_all_code_files_in_dir_and_subdir_into_single_py(dir_search, dir_ignore, dir_save, list_path_extend=[]):
    print('\n[combine_all_code_files_in_dir_and_subdir_into_single_py]')
    
    #[1] Set directory as current folder if not assigned.
    bsn_dir_search = os.path.basename(dir_search)
        
    #[2] Collect Python and Jupyter Notebook files from directory and subdirectories.
    ext_py = '.py'
    ext_ipynb = '.ipynb'
    list_file_paths = []
    for dirpath, dirnames, filenames in os.walk(dir_search):
        if dir_ignore and os.path.commonpath([dirpath, dir_ignore]) == dir_ignore:
            continue
        for file in filenames:
            if (file.endswith(ext_py) or file.endswith(ext_ipynb)) and not file.startswith("combined code"):
                file_path = os.path.join(dirpath, file)
                if not any(keyword in file for keyword in ['combined code', 'combined function', '.pyc']):
                    list_file_paths.append(file_path)
    list_file_paths.extend(list_path_extend)

    
    #[3] Prepare file names.
    cnt_ext_file = len(list_file_paths)
    print(f'-- There are {cnt_ext_file} files with extensions {ext_py} and {ext_ipynb}.')
    str_datetime = datetime.now().strftime("%Y-%m%d-%H%M")
    bsn_combined_py_save = f'F901_combined code_{cnt_ext_file} files under {bsn_dir_search}_{str_datetime}.py'
    path_py_save = os.path.join(dir_save, bsn_combined_py_save)
    
    #[4] Initialize combined_py_file content with the opening lines.
    combined_py_file_content = f'# Combined file generated on [{str_datetime}]\n\n'
    
    #[5] Start attaching each code file.
    for iter_code_path in list_file_paths:
        with open(iter_code_path, 'r') as code_path_context:
            iter_basename = os.path.basename(iter_code_path)
            
            #[6] If the file is a Jupyter Notebook, convert its cells to Python code.
            if iter_code_path.endswith(ext_ipynb):
                notebook_content = json.load(code_path_context)
                notebook_code = ""
                for cell in notebook_content['cells']:
                    if cell['cell_type'] == 'code':
                        notebook_code += ''.join(cell['source']) + '\n'
                single_code_file_content = (f'##### ##### ##### ##### ##### ##### ##### ##### ##### ##### \n'
                                            f'# Start of [{iter_basename}]\n'
                                            f'# File path: {iter_code_path}\n\n'
                                            f'{notebook_code}\n'
                                            f'# End of [{iter_basename}]\n\n\n\n\n')
            
            #[7] If the file is a Python script, read its content directly.
            else:
                single_code_file_content = (f'##### ##### ##### ##### ##### ##### ##### ##### ##### ##### \n'
                                            f'# Start of [{iter_basename}]\n'
                                            f'# File path: {iter_code_path}\n\n'
                                            f'{code_path_context.read()}\n'
                                            f'# End of [{iter_basename}]\n\n\n\n\n')
            combined_py_file_content += single_code_file_content
    
    #[8] Save the combined code file.
    with open(path_py_save, 'w') as output_file:
        output_file.write(combined_py_file_content)

    print(f'-- Combined code file created: {path_py_save}')
    return path_py_save




def move_specific_older_files(dir_search, list_ext, list_keywords_select, max_file_count, bsn_dump='01_dump'):
    print('\n[move_specific_older_files]')
    
    #[1] Filter the list according to extension and keywords.
    list_file_paths = [os.path.join(dir_search, file) for file in os.listdir(dir_search) if any(file.endswith(ext) for ext in list_ext)]
    list_file_paths = [file for file in list_file_paths if any(keyword in file for keyword in list_keywords_select)]
    
    #[2] Sort files by modification time and count them.
    list_file_paths = sorted(list_file_paths, key=os.path.getmtime)
    cnt_found_files = len(list_file_paths)
    excess_file_count = cnt_found_files - max_file_count
    print('-- [list_file_paths]:\n' + '\n'.join(list_file_paths))
    print(f'-- File count (cnt_found_files, max_file_count, excess_file_count): {cnt_found_files}, {max_file_count}, {excess_file_count}')
    
    #[3] Process excess files by moving them to the dump folder.
    if excess_file_count > 0:
        dir_dump = os.path.join(dir_search, bsn_dump)
        if not os.path.exists(dir_dump):
            os.makedirs(dir_dump)
        for i in range(excess_file_count):
            try:
                shutil.move(list_file_paths[i], dir_dump)
                print(f'--File moved: {os.path.basename(list_file_paths[i])}')
            except Exception as e:
                print(f"Error moving {list_file_paths[i]}: {e}")
    else:
        print("No files need to be moved according to max_file_count.")
    





dir_all_python = r'D:\01_Floor\a_Ed\09_EECS\10_Python'
dir_ignore = r'D:\01_Floor\a_Ed\09_EECS\10_Python\90_Online Tools'

#[1] Clean old files.
list_ext = ['.py']
list_keywords_select = ['combined code']

#[2] Get current directory where the code locates.
dir_loc = os.path.dirname(os.path.abspath(__file__))
move_specific_older_files(dir_loc, list_ext, list_keywords_select, 1, bsn_dump='00_CF dump')

#[5] Combine all python files into one single python file for code search.
path_py_save = combine_all_code_files_in_dir_and_subdir_into_single_py(dir_all_python, dir_ignore, dir_loc)

#[20] Complete
print('\nCompleted. Close in 5 seconds.')
time.sleep(5)
sys.exit()











#[7] We don't need to combine functions into an excel. It's less useful.
sys.exit()



def collect_all_functions_as_df(dir_search=None):
    print('\n[collect_all_functions_as_df]')
    # [1] Set directory as current folder if not assigned.
    if dir_search is None:
        dir_search = os.path.dirname(os.path.abspath(__file__))
        print(f'-- Searching in the directory: {dir_search}')
    
    # [2] Collect python files, walk through the dir_search directory and its subdirectories.
    ext = '.py'
    list_file_paths = []
    for dirpath, dirnames, filenames in os.walk(dir_search):
        #print(f'--Currently searching in the folder: {dirpath}')
        for file in filenames:
            if file.endswith(ext) and not file.startswith("combined code"):
                file_path = os.path.join(dirpath, file)
                list_file_paths.append(file_path)
    list_keywords_discard = ['combined code', 'combined function', '.pyc']
    list_file_paths = [file for file in list_file_paths if not any(keyword in file for keyword in list_keywords_discard)]
    #print('--[list_file_paths]:\n' + '\n'.join(list_file_paths)) #  Print a list of strings with each element on a new line, without using a loop

    # Initialize lists to store extracted data.
    list_functions = []
    list_python_basenames = []
    list_python_paths = []
    
    # [3] Read into lines and extract function definitions.
    for path_python in list_file_paths:
        with open(path_python, 'r') as file:
            lines = file.readlines()
        
        for line in lines:
            if line.strip().startswith('def ') and ':' in line:
                list_functions.append(line.strip())
                list_python_basenames.append(os.path.basename(path_python))
                list_python_paths.append(path_python)
    
    # [4] Combine into DataFrame.
    df_py_function = pd.DataFrame({
        'FunctionDefinition': list_functions,
        'FileName': list_python_basenames,
        'FilePath': list_python_paths})
    #print(tabulate(df_py_function, headers='keys', tablefmt='orgtbl'))
    return df_py_function


def search_file_with_certain_ext_in_dir_and_subdir(dir_search, one_ext, list_keywords_select, list_keywords_discard=None):
    print('\n[search_file_with_certain_ext_in_dir_and_subdir]')
    
    #[1] Initialize an empty list to store file paths.
    list_file_paths = []

    #[2] Walk through the directory and its subdirectories.
    for dirpath, dirnames, filenames in os.walk(dir_search):
        print(f'-- Currently searching in the folder: {dirpath}')
        
        #[3] Select files with the specified extension (case insensitive) and keywords.
        for file in filenames:
            if file.lower().endswith(one_ext.lower()) and any(keyword in file for keyword in list_keywords_select):
                file_path = os.path.join(dirpath, file)
                list_file_paths.append(file_path)
    
    #[4] Discard files with unwanted keywords, if specified.
    if list_keywords_discard is not None:
        list_file_paths = [file for file in list_file_paths if not any(keyword in os.path.basename(file) for keyword in list_keywords_discard)]
    
    #[5] Return the list of file paths that match the criteria.
    return list_file_paths




#[6] Clean old files.
list_ext = ['.xlsx']
list_keywords_select = ['combined function']
dir_search = os.path.dirname(os.path.abspath(__file__))
move_specific_older_files(dir_search = dir_search
                            , list_ext = list_ext
                            , list_keywords_select = list_keywords_select
                            , max_file_count = 0
                            , bool_delete = False
                            , dump_folder = 'CF_dump')


#[8] Assign paths and collect all functions into dataframe.
df_py_function = collect_all_functions_as_df(dir_all_python)


#[9] Save dataframe as excel and adjest column width.
dir_excel = os.path.dirname(os.path.abspath(__file__))
cnt_func = len(df_py_function)
str_datetime = datetime.now().strftime("%Y-%m%d-%H%M")
basename_excel = f'F902_combined function_{cnt_func} funcs_{str_datetime}.xlsx'
sheet_name_or_index = 'Combined Functions'
path_excel = F04_EXLDF.save_df_as_excel_add(df_py_function, dir_excel, basename_excel, sheet_name_or_index)
list_column_letters = ['A', 'B', 'C', 'D']
list_column_widths = [5, 100, 50, 20]
F04_EXLDF.adjust_multiple_column_widths(path_excel, sheet_name_or_index, list_column_letters, list_column_widths)


#[9] Complete.
print('\nCompleted. Close in 5 seconds.')
time.sleep(5)




















    

    

    

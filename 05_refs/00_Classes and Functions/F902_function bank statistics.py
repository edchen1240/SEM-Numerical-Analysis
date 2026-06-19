"""
[F92_function bank statistics.py]
Purpose: Count the size of function (or class) files in the function bank.
Collect information such as cnt_line, cnt_word, size_kB.
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





class Python_File_Statistics:
    """
    Count the size of function (or class) files in the function bank.
    1. User assigns a dir_search to search for Python scripts (.py).
        File paths containing list_kwd_ignore will be ignored.
    2. The function will count the cnt_line, cnt_word, size_kB of these files,
        and combine the result into df_py_stat.
    3. The function tabulate_stats will tabulate the result.
    """
    def __init__(self, dir_search, list_kwd_ignore=[]):
        self.dir_search = dir_search
        self.list_kwd_ignore = list_kwd_ignore
        self.df_py_stat = None
        print(f'[Python_File_Statistics] {dir_search}')
    
    
    def get_list_paths_of_scripts(self):
        """
        Get a list of Python script paths in the directory, ignoring files with keywords in list_kwd_ignore.
        """
        print("\n[get_list_paths_of_scripts]")
        # [1] Use glob to collect Python files
        list_file_paths = glob.glob(os.path.join(self.dir_search, "**/*.py"), recursive=True)
        list_file_paths = [file for file in list_file_paths if not any(kwd in file for kwd in self.list_kwd_ignore)]
        
        # [2] Count total files and raise an error if the count is invalid
        cnt_total = len(list_file_paths)
        print(f"-- Total Python files found: {cnt_total}")
        if cnt_total >= 1000 or cnt_total <= 0:
            raise ValueError(f"Please check the value of cnt_total. {cnt_total}")

        return list_file_paths


    def compute_script_stats(self):
        """
        Compute statistics for each Python script: line count, word count, and file size in kB.
        """
        print("\n[compute_script_stats]")
        list_file_paths = self.get_list_paths_of_scripts()
        
        #[1] Initialize lists to store statistics
        list_file_names = []
        list_file_paths_full = []
        list_cnt_lines = []
        list_cnt_words = []
        list_size_kB = []

        #[2] Iterate through files and compute statistics
        for file_path in list_file_paths:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.readlines()
                cnt_lines = len(content)
                cnt_words = sum(len(line.split()) for line in content)
                size_kB = round(os.path.getsize(file_path) / 1024, 2) 
            
            list_file_names.append(os.path.basename(file_path))
            list_file_paths_full.append(file_path)
            list_cnt_lines.append(cnt_lines)
            list_cnt_words.append(cnt_words)
            list_size_kB.append(size_kB)

        #[3] Combine statistics into a DataFrame
        self.df_py_stat = pd.DataFrame({
            'FileName': list_file_names,
            'Line Count': list_cnt_lines,
            'Word Count': list_cnt_words,
            'Size (kB)': list_size_kB
        })

        #[4] Append Mean and STD in the last row
        mean_row = self.df_py_stat.mean(numeric_only=True).round(2).to_dict()
        std_row = self.df_py_stat.std(numeric_only=True).round(2).to_dict()
        mean_row.update({'FileName': 'Mean'})
        std_row.update({'FileName': 'STD'})
        self.df_py_stat = pd.concat([self.df_py_stat, pd.DataFrame([mean_row, std_row])], ignore_index=True)

        print('-- Statistics computed successfully.')
        return self.df_py_stat

    def tabulate_stats(self):
        """
        Tabulate the statistics in a readable format.
        """
        if self.df_py_stat is None:
            raise ValueError('No statistics available. Please run compute_script_stats first.')
        print(f'\n[tabulate_stats]\n{tabulate(self.df_py_stat, headers="keys", tablefmt="orgtbl")}\n\n')
        
    def save_stat_as_txt(self, bsn='Function snd Class Bank Stat'):
        #[1] Remove filte extesion.
        if '.' in bsn:
            print(f'No need to add the file extention in bsn. {bsn}')
            bsn = os.path.splitext(bsn)[0]
        
        #[2] Process content
        timestamp = datetime.now().strftime("%Y-%m%d-%H%M")
        content = f'[Stat of Function snd Class Bank]\n{timestamp}\n\n{tabulate(self.df_py_stat, headers="keys", tablefmt="orgtbl")}\n\n\n'
        
        #[3] Save
        timestamp = datetime.now().strftime("%Y-%m")
        path_save = os.path.join(self.dir_search, f'{timestamp}_{bsn}.txt')
        with open(path_save, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Statistics saved successfully to {path_save}')




#[1] Define directory to search.
dir_search = r'D:\01_Floor\a_Ed\09_EECS\10_Python\00_Classes and Functions'
list_kwd_ignore = ['F91_']

# [2] Create an instance of the class
PFS = Python_File_Statistics(dir_search, list_kwd_ignore)

# [3] Compute statistics for Python scripts in the directory
df_stats = PFS.compute_script_stats()

# [4] Tabulate the statistics in a readable format
PFS.tabulate_stats()
PFS.save_stat_as_txt('Function snd Class Bank Stat')


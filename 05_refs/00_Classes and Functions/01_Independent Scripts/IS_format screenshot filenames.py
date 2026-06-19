"""
[IS_format screenshot filenames.py]
Purpose: Format the timestamped format of screenshot filenames.
Author: Meng-Chi Ed Chen
Date: 2026-0129
Status: Complete.
Note:
1. This script will be initiated by a batch file like this:
cd /d "D:\01_Floor\a_Ed\09_EECS\10_Python\00_Classes and Functions\01_Independent Scripts
python "IS_format screenshot filenames.py" "%dir_current%" "%bsn_suffix%"
if bsn_suffix is empty, no suffix will be added.

"""

import os, sys, tabulate
from datetime import datetime


class FormatScreenshotFilenames:
    def __init__(self,
                 dir_input,
                 bsn_suffix):

        #[1] Register instance variables.
        self.dir_input = dir_input
        self.bsn_suffix = bsn_suffix
        self.list_files = []
        self.list_timestamps = []
        self.cnt_total = 0

    def get_screenshot_files(self):
        """
        Get a list of screenshot files in the input directory.
        Their filenames should have a format like: Screenshot 2025-01-02 213221.png
        """

        for file in os.listdir(self.dir_input):
            if file.startswith('Screenshot ') and file.endswith('.png'):
                self.list_files.append(os.path.join(self.dir_input, file))
                #[1] Extract timestamp part
                timestamp_str = file[len('Screenshot '):-len('.png')]
                #[2] Store timestamp
                self.list_timestamps.append(timestamp_str)
        
        #[3] Report.
        self.cnt_total = len(self.list_files)
        print(f'Found {self.cnt_total} screenshot files in {self.dir_input}.')
        if self.cnt_total == 0:
            sys.exit('No screenshot files found. Exiting.')
        return self.list_files, self.list_timestamps

    def rename_files(self, timestamp_fmt):
        """
        Rename screenshot files with desired timestamp_fmt.
        Example: timestamp_fmt = '%Y-%m%d-%H%M'
        """
        for i, (file, timestamp) in enumerate(zip(self.list_files, self.list_timestamps)):
            #[1] Parse timestamp
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H%M%S')
            #[2] Format new filename
            new_filename = f'{dt.strftime(timestamp_fmt)}{self.bsn_suffix}.png'
            path_new = os.path.join(self.dir_input, new_filename)
            #[3] Rename file
            os.rename(file, path_new)
            print(f'[{i:03}/{self.cnt_total:03}]{os.path.basename(file)} --> {new_filename}')


#[1] Get the directory path from the command-line arguments
expected_argc = 3  # script name + dir_input + bsn_suffix
if len(sys.argv) != expected_argc:
    # Tabulate sys.argv with index, no heading
    argv_table = tabulate.tabulate(list(enumerate(sys.argv)), tablefmt='simple', showindex=False, headers=[])
    text_error =    f'\nlen(sys.argv) = {len(sys.argv)}.\nArguments received:\n'\
                    f'{argv_table}\n'\
                    f'Expected {expected_argc} arguments: script name, dir_input, bsn_suffix.\n'
    raise ValueError(text_error)


#[2] Settings.
timestamp_fmt = '%Y-%m%d-%H%M'

#[3] Process.
dir_input = sys.argv[1]
bsn_suffix = sys.argv[2]
formatter = FormatScreenshotFilenames(dir_input, bsn_suffix)
formatter.get_screenshot_files()
formatter.rename_files(timestamp_fmt)





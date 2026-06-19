"""
[F06_Resource.py]
Purpose: Resource management, such as timer, variable sizes, and memories.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import sys, os, openpyxl, tkinter, datetime, shutil, time, psutil
from tabulate import tabulate
from datetime import datetime
import pandas as pd
import numpy as np



#[1] Timer - start


class Timer():
    """
    # Example of use:
    Timer = Timer()
    Timer.start_timer()                 # Must start timer. Didn't put error check to save time.
    time.sleep(1)                       # Some process
    Timer.report_time_lapse('Lap1')
    time.sleep(2)                       # Some process
    Timer.report_time_lapse('Lap2')
    time.sleep(3)                       # Some process
    Timer.report_time_lapse('Lap3')
    time.sleep(4)                       # Some process
    Timer.end_timer('Final', True)
    """
    
    def __init__(self):
        self.t0_start = time.time()
        self.list_mark = []  
        self.list_duration_lap = []  
        self.list_duration_start = []  
        print(f'[Timer] Initiated, t0_start = {self.t0_start}')
        
    def start_timer(self):
        self.t_start = time.time()
        
    def report_time_lapse(self, mark, print_status=True, reset=True):
        #[1] Calculate durations
        duration_lap = time.time() - self.t_start
        duration_start = time.time() - self.t0_start

        #[2] Append to lists
        self.list_mark.append(mark)
        self.list_duration_lap.append(duration_lap)
        self.list_duration_start.append(duration_start)

        #[3] Print the report if requested
        if print_status:
            print(f'[Timer] {mark}: Lap Time = {duration_lap:.2f}s; \tFrom Start = {duration_start:.2f}s')

        #[4] Reset the timer if requested
        if reset:
            self.start_timer()
        
    def end_timer(self, last_mark='Last', report=True):
        #[1] Record last loop.
        self.report_time_lapse(last_mark, False, True)
        
        #[2] Combine timing data into a DataFrame
        self.df_timing = pd.DataFrame({
            'Mark': self.list_mark,
            'Lap Time (s)': [round(duration, 4) for duration in self.list_duration_lap], 
            'From Start (s)': [round(duration, 4) for duration in self.list_duration_start]})

        #[3] Print the DataFrame if requested
        if report:
            print(f'\n[Time Record]\n{tabulate(self.df_timing, headers="keys", tablefmt="orgtbl")}\n')

        return self.df_timing
                 
#[1] Timer - end




#[2] Variables - start

def print_variable_sizes(scope_vars, print_all=False):
    """
    Prints the size of all variables in the given scope in a tabular format.
    Args: scope_vars (dict): A dictionary of variables (e.g., locals() or globals()).
    Usage: M1BFI.print_variable_sizes(locals())
    """
    #[1] Create a list to store variable details
    var_data = []
    for var_name, var_value in scope_vars.items():
        try:
            size_in_bytes = sys.getsizeof(var_value)
            size_in_kb = size_in_bytes / 1024
            var_type = type(var_value).__name__ 
            var_data.append({"Variable Name": var_name, 
                             "Variable Type": var_type, 
                             "Size (Bytes)": size_in_bytes, 
                             "Size (KB)": f"{size_in_kb:.2f}"})
        except Exception as e:
            var_data.append({"Variable Name": var_name, 
                             "Variable Type": "Error", 
                             "Size (Bytes)": "Error", 
                             "Size (KB)": str(e)})

    #[2] Convert to a Pandas DataFrame
    df_var_size = pd.DataFrame(var_data)
    
    #[4] Filter variables based on size if print_all is False
    cnt_var = len(df_var_size)
    if print_all:
        text_show_scope = f'(printing all, {cnt_var} in total)'
        df_var_size = df_var_size 
    else:
        text_show_scope = f'(showing size above 1 kB, {cnt_var} in total)'
        df_var_size = df_var_size[df_var_size['Size (KB)'].astype(float) > 1]  

    #[5] Print the DataFrame as a table
    timestamp = datetime.now().strftime("%Y-%m%d-%H%M%S")
    print(f'\n\n[print_variable_sizes] #{timestamp}\n{text_show_scope}:\n')
    print(tabulate(df_var_size, headers='keys', tablefmt='orgtbl'))
    return df_var_size

            
#[2] Variables - end


def print_current_cpu_and_memory_usage(print_info=True):
    """
    Prints the current CPU and memory usage in a tabular format.
    """
    #[1] Get CPU and memory usage
    cpu_percent = psutil.cpu_percent(interval=1)  # CPU usage percentage
    memory_info = psutil.virtual_memory()  # Memory usage details
    memory_used = int(memory_info.used / (1024 ** 2))  # Convert bytes to MB
    memory_total = int(memory_info.total / (1024 ** 2))  # Convert bytes to MB
    memory_percent = memory_info.percent  # Memory usage percentage

    #[3] Collect into string.
    if print_info:
        timestamp = datetime.now().strftime("%Y-%m%d-%H%M%S")
        text_usage =    f'\n\n[print_current_cpu_and_memory_usage] #{timestamp}\n'\
                        f'CPU Usage: \t{cpu_percent}%\n'\
                        f'Memory Usage:\t{memory_percent}%\n'\
                        f'-- used/total: \t{memory_used}/{memory_total}'
        print(text_usage)
        
    return cpu_percent, memory_percent, memory_used, memory_total
    


print_current_cpu_and_memory_usage()

#[3] Memory - start











            
#[3] Memory - end






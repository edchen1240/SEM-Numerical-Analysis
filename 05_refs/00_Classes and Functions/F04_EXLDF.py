"""
[F04_EXLDF.py]
Purpose: Excel and dataframes. Reading and Saving. As well as arraies.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import sys, os, openpyxl, tkinter, datetime, shutil
from tabulate import tabulate

import pandas as pd
import numpy as np



#[1] Excel - start

"""def save_df_as_excel_overwrite(df, dir_excel, bsn_excel, sheet_name):
    print('\n[save_df_as_excel_overwrite]')
    if not os.path.exists(dir_excel):
        os.makedirs(dir_excel)
    path_xlsx = os.path.join(dir_excel, bsn_excel)
    # Use ExcelWriter in a context manager (with statement)
    with pd.ExcelWriter(path_xlsx, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=True)
    print(f'--Dataframe saved to {path_xlsx} in sheet {sheet_name}', end='\n\n')"""

#print(tabulate(averages_df, headers="keys", tablefmt="orgtbl"))




def read_excel_sheet_into_2d_array_panda(path_xlsx, sheetname): 
    print(f'\n[read_excel_sheet_into_2d_array_panda] \t Reading {os.path.basename(path_xlsx)} - {sheetname}...')
    
    #[1] Read only the specified sheet using pandas
    print(f'-- The following step might take ~20 seconds.')
    df = pd.read_excel(path_xlsx, sheet_name=sheetname, engine='openpyxl', header=None)  # Read without assuming headers
    # If this line fails, the file is damaged.
    
    #[2] Convert DataFrame to a NumPy array
    array_data = df.to_numpy()
    
    return array_data




def read_excel_sheet_into_df(path_xlsx, sheet_name=None, print_header=False):
    #[1] Read the Excel file into a DataFrame
    if sheet_name is None:
        sheet_name = 0  # Assuming 0 is the index of the first sheet
    df = pd.read_excel(path_xlsx, sheet_name=sheet_name)
    
    #[2] Tabulate the head of the DataFrame
    text_header = f"\n[read_excel_into_df] DataFrame Head:\n--\n"\
                  f"{tabulate(df.head(), headers='keys', tablefmt='orgtbl')}\n--\n"
    if print_header:
        print(text_header)
    del text_header
    return df



def read_excel_sheet_into_df_and_dict(path_xlsx, 
                                      sheet_name=None, 
                                      separator="----------",
                                      print_header=False):
    """
    An excel sheet is saved with a m×n table, an empty row, a separator row, and a d×2 dictionary key-value table.
    1. Locate the separator row, split the sheet into a m×n table and a d×2 dict table.
    2. Return df and dict.
    """
    
    #[1] Read the Excel file into a DataFrame
    if sheet_name is None:
        sheet_name = 0  # Assuming 0 is the index of the first sheet
    df = pd.read_excel(path_xlsx, sheet_name=sheet_name, header=0)

    #[1b] If the sheet was written with index=True, pandas reads the row index back as a leading
    #     'Unnamed: 0' column. Drop it so the table/separator/dict live in column 0 again
    #     (this keeps the reader compatible with both index=True and index=False writes).
    if len(df.columns) > 0 and str(df.columns[0]).startswith('Unnamed:'):
        df = df.drop(columns=df.columns[0]).reset_index(drop=True)

    #[2] Locate the separator row (first cell of the row equals the separator string)
    sep_row_idx = None
    for idx in df.index:
        if str(df.iloc[idx, 0]) == separator:
            sep_row_idx = idx
            break
    if sep_row_idx is None:
        raise ValueError(f"[read_excel_sheet_into_df_and_dict] Separator '{separator}' not found in the first column of sheet '{sheet_name}'.")

    #[3] Split into the m×n table (above separator) and the d×2 dict table (below separator)
    df_table = df.iloc[:sep_row_idx].copy()
    df_dict  = df.iloc[sep_row_idx + 1:].copy()

    #[4] Drop trailing empty rows from df_table
    df_table = df_table.dropna(how='all')

    #[5] Build the result dict from the first two columns of df_dict (no header row)
    result_dict = {}
    for _, row in df_dict.iterrows():
        key   = row.iloc[0]
        value = row.iloc[1]
        if pd.notna(key):
            result_dict[key] = value

    #[6] Optionally print the head of the table DataFrame
    text_header = f"\n[read_excel_sheet_into_df_and_dict] DataFrame Head:\n--\n"\
                  f"{tabulate(df_table.head(), headers='keys', tablefmt='orgtbl')}\n--\n"
    if print_header:
        print(text_header)
    del text_header

    return df_table, result_dict








def read_excel_sheet_into_df_no_header(path_xlsx, sheet_name, liist_headers, prevew_rows=5):
    #[1] Read the Excel file into a DataFrame without headers
    df = pd.read_excel(path_xlsx, sheet_name=sheet_name, header=None)
    
    #[2] Assign custom headers
    df.columns = liist_headers
    
    #[3] Tabulate the head of the DataFrame
    if prevew_rows not in [None, 0]:
        print(f"\n[read_excel_sheet_into_df_no_header] DataFrame Head:\n--\n"
            f"{tabulate(df.head(), headers='keys', tablefmt='orgtbl')}\n--\n")
    return df




def save_df_as_excel_overwrite(df, path_xlsx, sheet_name, index=False):
    print('\n[save_df_as_excel_overwrite]')
    
    #[1] Make dir if not exist.
    dir_excel = os.path.dirname(path_xlsx)
    if not os.path.exists(dir_excel):
        os.makedirs(dir_excel)

    #[2] Try saving, wait if file is open
    while True:
        try:
            if os.path.exists(path_xlsx):
                with pd.ExcelWriter(path_xlsx, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=index)
            else:
                with pd.ExcelWriter(path_xlsx, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=index)
            break  # success: break loop

        except PermissionError:
            text_warning = f'\n⚠️[Warning] Cannot write to "{path_xlsx}"!\n'\
                            f'Did you close the excel fiel? Please close the file and hit Enter to try again.'
            print(text_warning)
            input('-- Press Enter after closing the Excel file...')

    print(f'-- Dataframe saved to {path_xlsx} in sheet {sheet_name}', end='\n\n')



def save_df_and_dict_as_excel_overwrite(df, 
                                        dict,
                                        path_xlsx, 
                                        sheet_name, 
                                        separator="----------",
                                        index=False):
    """
    A DataFrame and a dictionary are saved in the same sheet, separated by an empty row + separator row.
    Layout: [df header + data rows] -> [empty row] -> [separator row] -> [key-value rows (col A, col B)]
    Mirrors read_excel_sheet_into_df_and_dict().
    Implementation: dict rows are appended to df as regular rows (NaN-padded), then the combined
    DataFrame is written in a single pandas pass to avoid openpyxl load-resave corruption.
    """
    print('\n[save_df_and_dict_as_excel_overwrite]')

    dir_excel = os.path.dirname(path_xlsx)
    if dir_excel:
        os.makedirs(dir_excel, exist_ok=True)

    #[1] Build combined DataFrame: df + empty row + separator row + dict key-value rows.
    n_cols = len(df.columns)
    cols   = df.columns.tolist()

    empty_row = pd.DataFrame([[np.nan] * n_cols], columns=cols)
    sep_row   = pd.DataFrame([[separator] + [np.nan] * (n_cols - 1)], columns=cols)

    dict_rows = []
    for key, value in dict.items():
        row = [key, value] + [np.nan] * max(0, n_cols - 2)
        dict_rows.append(row)
    df_dict = pd.DataFrame(dict_rows, columns=cols) if dict_rows else pd.DataFrame(columns=cols)

    df_combined = pd.concat([df, empty_row, sep_row, df_dict], ignore_index=True)

    #[2] Write the combined DataFrame in a single pandas pass, retrying on PermissionError.
    while True:
        try:
            if os.path.exists(path_xlsx):
                with pd.ExcelWriter(path_xlsx, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df_combined.to_excel(writer, sheet_name=sheet_name, index=index)
            else:
                with pd.ExcelWriter(path_xlsx, engine='openpyxl') as writer:
                    df_combined.to_excel(writer, sheet_name=sheet_name, index=index)
            break  # success

        except PermissionError:
            text_warning = f'\n⚠️[Warning] Cannot write to "{path_xlsx}"!\n'\
                            f'Did you close the excel file? Please close the file and hit Enter to try again.'
            print(text_warning)
            input('-- Press Enter after closing the Excel file...')

    print(f'-- DataFrame and dict saved to {path_xlsx} in sheet {sheet_name}', end='\n\n')









def save_list_dfs_as_excel_overwrite(list_dfs, list_sheetnames, path_xlsx):
    print('\n[save_list_dfs_as_excel_overwrite]')

    #[1] Make sure the list_dfs and list_sheetnames match.
    if len(list_dfs) != len(list_sheetnames):
        raise ValueError('The provided number of dataframes and sheet names should be the same.')

    #[2] Save all DataFrames into a single Excel workbook (overwrite).
    try:
        with pd.ExcelWriter(path_xlsx) as writer:
            for i_df, i_sheetname in zip(list_dfs, list_sheetnames):
                i_df.to_excel(writer, sheet_name=i_sheetname, index=True)
        print(f'--All DataFrames saved to {path_xlsx}', end='\n\n')
    except Exception as e:
        print(f'--Failed to save Excel file: {e}')
        raise

    
    

def read_list_dfs_from_excel(path_xlsx, list_sheetnames):
    print('\n[read_list_dfs_from_excel]')
    list_dfs = []
    for i_sheetname in list_sheetnames:
        df = read_excel_sheet_into_df(path_xlsx, sheet_name=i_sheetname, print_header=False)
        list_dfs.append(df)
    print(f'--All DataFrames read from {path_xlsx}', end='\n\n')
    return list_dfs



    








def save_df_as_excel_add(df, dir_excel, basename_excel, sheet_name_or_index, print_status=False):
    print('\n[save_df_as_excel_add]')
    sheet_name = f'Sheet{sheet_name_or_index}' if isinstance(sheet_name_or_index, int) else str(sheet_name_or_index)
    os.makedirs(dir_excel, exist_ok=True)
    path_excel = os.path.join(dir_excel, basename_excel)

    #[1] Auto-increment sheet name if it already exists in the workbook
    if os.path.isfile(path_excel):
        wb = openpyxl.load_workbook(path_excel, read_only=True)
        existing = wb.sheetnames
        wb.close()
        base, suffix = sheet_name, 1
        while sheet_name in existing:
            sheet_name = f'{base}{suffix}'
            suffix += 1

    #[2] Save, retrying on PermissionError
    mode = 'a' if os.path.isfile(path_excel) else 'w'
    writer_kwargs = dict(engine='openpyxl', mode=mode)
    if mode == 'a':
        writer_kwargs['if_sheet_exists'] = 'new'
    try:
        with pd.ExcelWriter(path_excel, **writer_kwargs) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=True)
    except PermissionError as e:
        print(f'Error: {e}\nThe file "{path_excel}" is open. Close it and press Enter...')
        input()
        return save_df_as_excel_add(df, dir_excel, basename_excel, sheet_name_or_index, print_status)

    if print_status:
        print(f'--Dataframe saved to {path_excel}\n-- in sheet {sheet_name}', end='\n\n')
    return sheet_name








def save_df_as_excel_add_with_full_path(df, path_xlsx, sheet_name_or_index):
    print('\n[save_df_as_excel_add_with_full_path]')
    #[1] Convert sheet index to string name if an integer is provided
    if isinstance(sheet_name_or_index, int):
        sheet_name = f'Sheet{sheet_name_or_index}'
    else:
        sheet_name = str(sheet_name_or_index)  # Ensure sheet_name is always a string
    #[2] Check if the file exists
    if os.path.isfile(path_xlsx):
        book = openpyxl.load_workbook(path_xlsx)
        
        #[3] If the sheet exists, remove the existing sheet
        if sheet_name in book.sheetnames:
            del book[sheet_name]
        
        with pd.ExcelWriter(path_xlsx, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=True)
    else:  
        #[4] If file doesn't exist, create a new one
        with pd.ExcelWriter(path_xlsx, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=True)
    print(f'--Dataframe saved to {path_xlsx} in sheet {sheet_name}', end='\n\n')
    return path_xlsx


def save_df_as_excel_add_with_bsn(df, dir_excel, bsn_excel, sheet_name_or_index):
    print('\n[save_df_as_excel_add]')
    #[2] Ensure the directory exists
    if not os.path.exists(dir_excel):
        os.makedirs(dir_excel)
    path_xlsx = os.path.join(dir_excel, bsn_excel)
    
    #[5] Convert sheet index to string name if an integer is provided
    save_df_as_excel_add_with_full_path(df, path_xlsx, sheet_name_or_index)
    return path_xlsx



def read_excel_sheet_into_2d_array(path_xlsx, sheetname):
    print(f'\n[read_excel_sheet_into_2d_array] \t working on {os.path.basename(path_xlsx)} ...')
    #[1] Open the Excel sheet.
    workbook = openpyxl.load_workbook(path_xlsx)
    sheet_input = workbook[sheetname]
    
    # [2] Read data from the input sheet
    data = []
    for row in sheet_input.iter_rows(values_only=True):
        data.append(row)
    
    # [3] Extract the x-axis (wavenumber) from the first column
    array_data = np.array(data)

    return array_data, workbook




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





def adjust_all_column_width_and_row_height(path_xlsx, column_width, row_height, sheet_name=None):
    """
    Adjust all columns' width and rows' height in an Excel workbook.

    Parameters:
    path_xlsx (str): Path to the Excel file.
    column_width (int or float): New width to set for each column.
    row_height (int or float): New height to set for each row.
    sheet_name (str, optional): Specific sheet name to adjust. If None, adjusts all sheets.

    """
    print('\n[adjust_all_column_width_and_row_height]')
    #[1] Load workbook
    workbook = openpyxl.load_workbook(path_xlsx)
    column_width = column_width / 3.29 * 4

    #[2] Determine which sheets to adjust
    sheets_to_adjust = workbook.sheetnames if not sheet_name else [sheet_name]

    #[3] Check if specified sheet exists when sheet_name is provided
    if sheet_name and sheet_name not in workbook.sheetnames:
        print(f"--Sheet '{sheet_name}' does not exist in the workbook.")
        return

    #[4] Adjust column width and row height
    for sheet in sheets_to_adjust:
        worksheet = workbook[sheet]
        #[5] Adjust column widths
        max_column = worksheet.max_column  # Fetch the maximum populated column
        for i in range(1, max_column + 1):
            col_letter = openpyxl.utils.get_column_letter(i)
            worksheet.column_dimensions[col_letter].width = column_width
        
        #[6] Adjust row heights
        max_row = worksheet.max_row  # Fetch the maximum populated row
        for i in range(1, max_row + 1):
            worksheet.row_dimensions[i].height = row_height

        print(f"--Adjusted width to {column_width} and height to {row_height} for sheet '{sheet}'.")

    #[7] Save workbook
    workbook.save(path_xlsx)
    print("--All specified sheets have been adjusted.", end='\n\n')






def read_excel_with_multiple_sheets_into_list_of_dfs(path_xlsx):
    print('\n[read_excel_with_multiple_sheets_into_list_of_dfs]')
    #[1] Read all sheets into a dictionary of dataframes
    dfs = pd.read_excel(path_xlsx, sheet_name=None)
    
    #[2] Separate the dictionary into a list of dataframes and a list of sheet names
    list_of_dfs = list(dfs.values())
    list_of_sheetnames = list(dfs.keys())
    
    #[2] Optionally print the headers of the first few rows of each dataframe
    for sheet_name, df in dfs.items():
        print(f'--[dataframe headers for {sheet_name}]', df.columns.tolist())
    print()
    return list_of_dfs, list_of_sheetnames


def save_dict_as_excel_overwrite(dict_dfs, path_xlsx):
    print('\n[save_dict_as_excel_overwrite]')
    #[1] Make dir if not exist.
    dir_excel = os.path.dirname(path_xlsx)
    if not os.path.exists(dir_excel):
        os.makedirs(dir_excel)

    #[2] Use ExcelWriter to save each dataframe in the dictionary to its corresponding sheet
    with pd.ExcelWriter(path_xlsx, engine='xlsxwriter') as writer:
        for sheet_name, df in dict_dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=True)
    
    print(f'--All DataFrames saved to {path_xlsx}', end='\n\n')
    
    
def read_excel_with_two_columns_into_dict(path_xlsx, sheet_name):
    print('\n[read_excel_with_two_columns_into_dict]')
    #[1] Read the specified sheet into a DataFrame
    df = pd.read_excel(path_xlsx, sheet_name=sheet_name)
    
    #[2] Check if the DataFrame has at least two columns
    if df.shape[1] < 2:
        raise ValueError(f"The sheet '{sheet_name}' must have at least two columns.")
    
    #[3] Create a dictionary from the first two columns
    result_dict = pd.Series(df.iloc[:, 1].values, index=df.iloc[:, 0]).to_dict()
    
    print(f'--Dictionary created from {path_xlsx} - {sheet_name}', end='\n\n')
    return result_dict



def color_the_header_row_in_excel(path_xlsx, sheet_name, 
                                  header_row_index=0, 
                                  start_col_index=0, end_col_index=None,
                                  fill_color="FFDDAA"):
    print('\n[color_the_header_row_in_excel]')

    #[1] Load workbook
    workbook = openpyxl.load_workbook(path_xlsx)

    #[2] Access the sheet
    if sheet_name not in workbook.sheetnames:
        print(f"--Sheet '{sheet_name}' does not exist in the workbook.")
        return
    worksheet = workbook[sheet_name]

    #[3] Determine column range (0-based indices → 1-based openpyxl)
    if end_col_index is None:
        end_col_index = worksheet.max_column - 1  # inclusive, 0-based

    #[4] Apply fill color to the header row
    fill = openpyxl.styles.PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
    row_number = header_row_index + 1  # openpyxl uses 1-based rows
    for col_idx in range(start_col_index, end_col_index + 1):
        col_letter = openpyxl.utils.get_column_letter(col_idx + 1)
        worksheet[f'{col_letter}{row_number}'].fill = fill

    #[5] Save workbook
    workbook.save(path_xlsx)
    print(f"--Row {header_row_index} colored '{fill_color}' (cols {start_col_index}–{end_col_index}) in sheet '{sheet_name}'.", end='\n\n')



#[1] Excel - end





#[2] CSV - start



def save_df_as_csv_overwrite(df, path_csv, index=False, sep=','):
    print('\n[save_df_as_csv_overwrite]')
    #[1] Make dir if not exist.
    dir_csv = os.path.dirname(path_csv)
    if not os.path.exists(dir_csv):
        os.makedirs(dir_csv)
    #[2] Add "sep=;" to the file if the delimiter is not the default ','
    add_sep_line = sep != ','
    with open(path_csv, 'w', encoding='utf-8') as f:
        if add_sep_line:
            f.write(f'sep={sep}\n')
        #[3] Save the DataFrame as a CSV file
        df.to_csv(f, index=index, sep=sep)
    print(f'--Dataframe saved to {path_csv}', end='\n\n')

def read_csv_into_df(path_csv, sep=','):
    print('\n[read_csv_into_df]')
    #[1] Check if the file exists
    if not os.path.exists(path_csv):
        raise FileNotFoundError(f"The file {path_csv} does not exist.")
    
    # [2] Handle optional "sep=" line
    with open(path_csv, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        if first_line.startswith("sep="):
            sep = first_line.split('=')[1]  # Extract delimiter from the first line
            print(f"--Detected delimiter from file: '{sep}'")
            skip_rows = 1  # Skip the first line when reading the CSV
        else:
            skip_rows = 0  # Do not skip lines if "sep=" is not present

    #[3] Read the CSV file into a DataFrame
    df = pd.read_csv(path_csv, sep=sep, skiprows=skip_rows)
    print(f'--Dataframe read from {path_csv}', end='\n\n')
    return df







#[2] CSV - end















#[Array] Start


def save_3D_image_arrays_as_excel(array_image, dir_xlsx, filename_xlsx):
    """
    Save an array image into multiple sheets in Excel. This function handles both grayscale (2D) and multi-channel (3D) images.
    Sheets are named as c0, c1, c2, etc., for multi-channel images. For a grayscale image, a single sheet named 'c0' is created.

    Parameters:
    array_image (numpy.ndarray): The numpy array to be saved, either 2D (grayscale image) or 3D (multi-channel image).
    dir_xlsx (str): The directory where the Excel file will be saved.
    filename_xlsx (str): The filename for the Excel file; ensures it has an .xlsx extension.

    Returns:
    str: The full path to the saved Excel file.
    """
    #[1] Ensure the filename ends with .xlsx
    if not filename_xlsx.endswith('.xlsx'):
        filename_xlsx += '.xlsx'

    #[2] Ensure the directory exists
    if not os.path.exists(dir_xlsx):
        os.makedirs(dir_xlsx)

    #[3] Create full path for the Excel file
    path_xlsx = os.path.join(dir_xlsx, filename_xlsx)

    #[4] Using ExcelWriter to handle writing multiple sheets
    with pd.ExcelWriter(path_xlsx, engine='xlsxwriter') as writer:
        #[5] Check if the image is grayscale (2D) or multi-channel (3D)
        if array_image.ndim == 2:
            df = pd.DataFrame(array_image)
            df.to_excel(writer, sheet_name='c0', index=False)
        elif array_image.ndim == 3:
            #[6] Loop through each index in the third dimension for multi-channel images
            for i in range(array_image.shape[2]):
                df = pd.DataFrame(array_image[:, :, i])
                df.to_excel(writer, sheet_name=f'c{i}', index=False)

    return path_xlsx




def save_array_as_csv(array, dir_csv, filename_csv):
    print('\n[save_array_as_csv]')
    array = np.asarray(array)
    #[1] Check dimensions
    if array.ndim >= 4:
        raise ValueError(f'\nArray has too many dimensions: {array.shape}')
    if array.ndim == 3:
        # Accept only if one dimension is 1
        if 1 not in array.shape:
            raise ValueError(f'\n3D array must have a singleton dimension, got shape {array.shape}')
        array = np.squeeze(array)
        if array.ndim != 2:
            raise ValueError(f'\nAfter squeezing, array is not 2D: {array.shape}')
    elif array.ndim == 2:
        pass 
    else:
        raise ValueError(f"Array must be 2D or 3D with a singleton dimension, got shape {array.shape}")

    #[2] Make dir if not exist.
    if not os.path.exists(dir_csv):
        os.makedirs(dir_csv)
    path_csv = os.path.join(dir_csv, filename_csv)
    np.savetxt(path_csv, array, delimiter=",")
    return path_csv

def read_csv_as_array(path_csv):
    print('\n[read_csv_as_array]')
    if not os.path.exists(path_csv):
        raise FileNotFoundError("CSV file doesn't exist!")
    array = np.genfromtxt(path_csv, delimiter=',')
    return array

#[Array] End







#[Cell in Excel] Start



def add_text_after_the_last_row_in_an_excel_sheet(path_xlsx, sheet_name, text_to_add, row_gap=1, col='A'):
    """
    On the specific Excel sheet, find the last row plus row_gap, and add text at column col.
    """
    print('\n[add_text_after_the_last_row_in_an_excel_sheet]')
    
    #[1] Load workbook, Use the first sheet if sheet_name is None.
    workbook = openpyxl.load_workbook(path_xlsx)
    if sheet_name is None:
        sheet_name = 0

    #[3] Access the sheet
    sheet = workbook[sheet_name] if isinstance(sheet_name, str) else workbook.worksheets[sheet_name]
    
    #[4] Find the last row plus row_gap
    target_row = sheet.max_row + row_gap

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



#[Cell in Excel] End


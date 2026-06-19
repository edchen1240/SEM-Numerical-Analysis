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

#[] For plot
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
import matplotlib.colors as colors
from tabulate import tabulate


#[] For Font
import freetype
sys.path.append(r'D:\01_Floor\a_Ed\09_EECS\10_Python\00_Classes and Functions')
import F02_File as F02_File # type: ignore







def print_info_for_single_TTF(path_font, exp_size):
    print('\n[print_face_of_a_TTF]')
    #[1] Import the face of the TTF file.
    face = freetype.Face(path_font) # [Note] Refer to regular face, not bold or
    #[Note] Faces representing different styles (such as italic, bold, regular) and weights (light, regular, bold, extra-bold, etc.).
    print(f'--Font name: \t{face.family_name.decode()}')  # Decoding from bytes to string
    print(f'--Style name: \t{face.style_name.decode()}')  # Decoding from bytes to string
    print(f'--Glyphs [cnt]: \t{face.num_glyphs}')

    #[2] Set a example size to have size
    face.set_char_size(exp_size * exp_size)  # Example size, might not be necessary for this analysis
    size_metrics = face.size  #[Note] In a 16-point font, 1 em equals 16 points
    print(f'--Ascender, Descender, Height: {face.ascender}, {face.descender}, {face.height}')
    print(f'--Max advance (width, height): {face.max_advance_width}, {face.max_advance_height}')
    print(f'--Underline (position, thickness): {face.underline_position}, {face.underline_thickness}')
    print(f'--Example size: {exp_size}')
    print(f'--Font size in pixels per EM (H, V): {size_metrics.x_ppem}, {size_metrics.y_ppem}')
    #[3] Set character ranges: Basic ASCII and CJK Unified Ideographs range
    character_ranges = [(32, 127),  # Basic ASCII
                        (0x4E00, 0x9FFF)]  # CJK Unified Ideographs Block
    #[4] Count defined and undefined characters
    defined, total = 0, 0
    for start, end in character_ranges:
        for char_code in range(start, end + 1):
            total += 1
            if face.get_char_index(char_code) != 0:
                defined += 1
    undefined = total - defined
    defined_percentage = (defined / total) * 100 if total > 0 else 0
    print(f'--Defined [char]: {defined}')
    print(f'--Undefined [cjar]: {undefined}')
    print(f'--Defined [pct]: {defined_percentage:.2f}%')






def print_info_for_TTFs_in_dir(dir_TTF):
    print('\n[print_info_for_TTFs_in_dir]')
    #[1] Check directory and filter list with only TTF files.
    if not os.path.isdir(dir_TTF):
        raise FileNotFoundError(f"The directory '{dir_TTF}' was not found.")
    list_path_TTF = [os.path.join(dir_TTF, file) for file in os.listdir(dir_TTF) if file.lower().endswith('.ttf')]
    #[2] Extracting infromation from every ttf files.
    data = []
    character_ranges = [(32, 127)  # Basic ASCII
                        ,(0x4E00, 0x9FFF)  # CJK Unified Ideographs Block
                        ,(0x10000, 0x10FFFF) ]  # Supplementary Multilingual Plane
    print(f'--character_ranges: {character_ranges}')
    for path_font in list_path_TTF:
        bsn = os.path.basename(path_font)
        folder_name = os.path.basename(dir_TTF)
        size = os.path.getsize(path_font)/1024
        face = freetype.Face(path_font)  # [Note] Refer to regular face, not bold or italic
        font_name = face.family_name.decode()  # Decoding from bytes to string
        style_name = face.style_name.decode()  # Decoding from bytes to string
        num_glyphs = face.num_glyphs
        max_advance = face.max_advance_width, face.max_advance_height
        underline_P_T = face.underline_position, face.underline_thickness
        # [3] Set character ranges: Basic ASCII and CJK Unified Ideographs range
        character_ranges = [(32, 127), (0x4E00, 0x9FFF)]  # Basic ASCII, CJK Unified Ideographs Block
        # [4] Count defined and undefined characters
        defined, total = 0, 0
        for start, end in character_ranges:
            for char_code in range(start, end + 1):
                total += 1
                if face.get_char_index(char_code) != 0:
                    defined += 1
        undefined = total - defined
        defined_percentage = round((defined / total) * 100, 2) if total > 0 else 0
        data.append({
            'File Nmae': bsn,
            'Size (kB)': size,
            'Font Name': font_name,
            'Style Name': style_name,
            'Glyphs [cnt]': num_glyphs,
            'Max Adv (W, H)': max_advance,
            'Underline (P,T)': underline_P_T,
            'Defined [Char]': defined,
            'Undefined [Char]': undefined,
            'Defined Pct [%]': defined_percentage})
        print(f'--[{bsn}] total = {total}')
    df_TTF = pd.DataFrame(data)
    # [5] Save a copy of df_TTF
    now = datetime.now()
    str_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")
    text = (f'[TTF File Statistics] {str_datetime}\n' 
            + 'Target Directory: ' + dir_TTF + '.\n\n'
            + tabulate(df_TTF, headers='keys', tablefmt='orgtbl'))
    txt_report_basename = f'[TTF File Statistics] {folder_name}.txt'
    path_save_txt_report = os.path.join(dir_TTF, txt_report_basename)
    F02_File.create_txt_and_save_text(path_save_txt_report, text)   
    return df_TTF

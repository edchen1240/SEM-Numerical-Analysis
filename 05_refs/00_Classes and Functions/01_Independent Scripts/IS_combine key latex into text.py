"""
[IS_combine key latex into text.py]
Purpose: Combine separated latex files into text files for LLM to read.
Author: Meng-Chi Ed Chen
Date: 2026-0128

Status: Complete.
"""
import os
from datetime import datetime


class CombineKeyLatexIntoText:
    def __init__(self, 
                    list_files,
                    output_dir,
                    output_bsn):
        
        #[1] Register instance variables.
        self.list_files = list_files
        self.output_dir = output_dir
        #[2] Ensure output base name has no extension to avoid double extensions
        base_name = os.path.splitext(output_bsn)[0]
        self.output_bsn = base_name
        ts = datetime.now().strftime('%H%M%S')
        self.path_output = os.path.join(self.output_dir, f'{self.output_bsn}_{ts}.txt')

    def validate_inputs(self):
        """
        1. Check if all list_files are txt or tex files.
        2. Check if output_dir exists, if not create it.
        """
        #[1] Check if all list_files are txt or tex files.
        for file in self.list_files:
            if not (file.endswith('.tex') or file.endswith('.txt')):
                raise ValueError(f'File {file} is not a .tex or .txt file.')
            
        #[2] Check if output_dir exists, if not create it.
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f'Created output directory: {self.output_dir}')
        
    def combine_files(self):
        """
        Combine all files in list_files into a single text file.
        """
        #[1] Make sure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        with open(self.path_output, 'w', encoding='utf-8') as outfile:
            for fname in self.list_files:
                #[2] Skip missing files with a warning instead of crashing
                if not os.path.exists(fname):
                    print(f'Warning: source file not found, skipping: {fname}')
                    continue
                try:
                    with open(fname, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                except Exception as e:
                    print(f'Error reading {fname}: {e}; skipping.')
                    continue
                outfile.write(content + '\n\n')  # Add double newlines between files
        print(f'Combined files into: {self.path_output}')
        
        
list_files = [
    r'D:\01_Floor\a_Ed\01_Organize\03_Clan 家族\2026-0127_蔡卓穎碩論\05_overleaf\05_cover.tex',
    r'D:\01_Floor\a_Ed\01_Organize\03_Clan 家族\2026-0127_蔡卓穎碩論\05_overleaf\06_abstract.tex',
    r'D:\01_Floor\a_Ed\01_Organize\03_Clan 家族\2026-0127_蔡卓穎碩論\05_overleaf\11_ch01_intro.tex',
    r'D:\01_Floor\a_Ed\01_Organize\03_Clan 家族\2026-0127_蔡卓穎碩論\05_overleaf\12_ch02_literature.tex',
    r'D:\01_Floor\a_Ed\01_Organize\03_Clan 家族\2026-0127_蔡卓穎碩論\05_overleaf\13_ch03_methodology.tex',
    r'D:\01_Floor\a_Ed\01_Organize\03_Clan 家族\2026-0127_蔡卓穎碩論\05_overleaf\14_ch04_result_and_diss.tex',
    r'D:\01_Floor\a_Ed\01_Organize\03_Clan 家族\2026-0127_蔡卓穎碩論\05_overleaf\15_ch05_conclusion.tex'
]


output_dir = r'D:\01_Floor\a_Ed\01_Organize\03_Clan 家族\2026-0127_蔡卓穎碩論\05_overleaf'
output_bsn = '2026-0127_蔡卓穎碩論_full.txt'

combiner = CombineKeyLatexIntoText(list_files, output_dir, output_bsn)
combiner.validate_inputs()  
combiner.combine_files()






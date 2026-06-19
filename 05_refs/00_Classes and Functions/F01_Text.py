"""
[F01_Text.py]
Purpose: Functions of text file management.
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


#[1] Emoji Reference - Start




"""
Status & Results
✅ Success / Check Mark: :white_check_mark:, ✔️, ☑️, 🆗, ✓
☑️ Success after correction.
❌ Error / Wrong: :x:, ✖️, 🛑, 🚫
⚠️ Warning: :warning:, ☣️, ⚡, 🔸
ℹ️ Info: :information_source:, 🔹, 💬
Processes & Actions
🔍 Checking / Auditing: :mag:, :search:, :microscope:, :eye:
🔄 Processing / In-Progress: :arrows_counterclockwise:, ⏳, ⌛, ⚙️
🚀 Running / Deploying: :rocket:, ▶️, 🏃
🧪 Testing: :test_tube:, 🧪, ⚗️
Data & Organization
📋 List: :clipboard:, 📜, 📑, 🗒️
🔢 Count / Metrics: :1234:, 📊, 📈, 📉, 🔢
📦 Input / Output: :package:, 📥, 📤
🪵 Logging: :wood:, 🪵, 📝
Examples of Combined Usage
Build Status:
🔍 Analyzing source code...
⏳ Compiling...
✅ Build passed (2.4s)
⚠️ 3 non-critical dependencies found
🔢 Tests run: 45 | Errors: 0
"""

#[1] Emoji Reference - End






#[2] Text  start


def create_txt_and_save_text(path_txt, text, open_file=True):
    print('\n[create_txt_and_save_text]')
    #[1] Ensure the directory where the file will be saved exists.
    os.makedirs(os.path.dirname(path_txt), exist_ok=True)    
       
    #[2] Open the file in write mode ('w'), which will create the file if it doesn't exist.
    with open(path_txt, 'w') as file:
        file.write(text)
        
    #[3] After saving, optionally open the txt file.
    if open_file:
        #[4] Check the platform and open the file accordingly
        if os.name == 'nt':             # For Windows
            os.startfile(path_txt)
        elif os.name == 'posix':        # For MacOS
            subprocess.run(['open', path_txt])
        else:                           # For Linux (xdg-open should work for most environments)
            subprocess.run(['xdg-open', path_txt])


def read_text_from_txt(path_txt, char_preview=None):
    try:
        # [1] Open the file in read mode ('r') and read its content.
        with open(path_txt, 'r') as file:
            content = file.read()
            # [2] Print a preview of the content based on char_preview.
            if char_preview is not None:
                print('[read_txt] content quick view:\n', content[:char_preview])
        
        return content
    except FileNotFoundError:
        # [4] Handle the case where the file is not found.
        print(f'[read_txt] File not found:\n {path_txt}')
        sys.exit()
    except Exception as e:
        # [6] Handle any other exceptions that may occur while reading the file.
        print(f'[read_txt] An error occurred while reading the file:\n {str(e)}')
        sys.exit()


def append_text_to_txt(path_txt, text_to_append, char_preview=None):
    # [1] Check if the path_txt exists.
    if not os.path.exists(path_txt):
        print(f'[append_txt] File not found:\n {path_txt}')
        sys.exit()
    
    # [2] Get current datetime and create the opening_of_append string.
    timestamp = datetime.now().strftime("%Y-%m%d-%H%M%S")
    opening_of_append = '\n\n--\n[' + timestamp + ']\n\n'
    
    try:
        # [5] Open the file in append mode ('a') and write the opening_of_append and text_to_append.
        with open(path_txt, 'a') as file:
            file.write(opening_of_append)
            file.write(text_to_append)
            # [6] Print a preview of the text_to_append based on char_preview.
            if char_preview is not None:
                print('[append_txt] content quick view:\n', text_to_append[:char_preview], '\n')
            file.close()
    except Exception as e:
        # [7] Handle any exceptions that may occur while appending to the file.
        print(f'[append_txt] An error occurred while reading the file:\n {str(e)}')
        sys.exit()
        
        
def add_newline_for_every_character(path_txt):
    # [1] Read text from txt file.
    content = read_text_from_txt(path_txt, char_preview=None)
    
    # [2] Remove spaces, newlines, and tabs in the content.
    content = content.replace(' ', '').replace('\n', '').replace('\t', '')
    
    # [3] Add new line between each character.
    new_content = '\n'.join(content)
    
    # [4] Append back to original file and save.
    append_text_to_txt(path_txt, new_content, char_preview=100)
    print(f'Complete processing file: {path_txt}')
    
#[2] Text  end








#[Dictionary] start


def save_dict_as_txt(dict_obj, path_txt):
    with open(path_txt, 'w') as file:
        for key, value in dict_obj.items():
            file.write(f"{key}:{value}\n")
    return path_txt


def read_dict_as_txt(path_txt):
    dict_obj = {}
    with open(path_txt, 'r') as file:
        for line in file:
            key, value = line.strip().split(':', 1)
            dict_obj[key] = value
    return dict_obj

def save_dict_as_json(dict_obj, path_json):
    import json
    with open(path_json, 'w') as file:
        json.dump(dict_obj, file)
    return path_json

def read_json_as_dict(path_json):
    import json
    with open(path_json, 'r') as file:
        dict_obj = json.load(file)
    return dict_obj


def format_dict_beautifully(dict_obj):
    formatted_str = ""
    for key, value in dict_obj.items():
        formatted_str += f"{key}: {value}\n"
    return formatted_str



#[Dictionary] end









#[Interaction] Start




def do_you_want_to_continue(message):
    print('\n[do_you_want_to_continue]')
    string_ques = input(message)
    string_ques = string_ques.lower()
    if ('yes' in string_ques) or ('ye' in string_ques) or ('y' in string_ques) or ('ok' in string_ques) \
        or ('sure' in string_ques) or ('go' in string_ques):
        print('User agreed to proceed.', string_ques)
    elif ('no' in string_ques) or ('n' in string_ques):
        print('User chose to stop.', string_ques)
        sys.exit()
    else:
        print('[Invalid Input] I will just keep moving on.\n', string_ques)



def putTextSmooth(image, text, org, fontFace, fontScale, color, thickness, smooth_iterations=3):
    for i in range(smooth_iterations):
        # Draw the text with decreasing thickness
        cv2.putText(image, text, org, fontFace, fontScale, color, thickness - i, cv2.LINE_AA)



#[Interaction] end
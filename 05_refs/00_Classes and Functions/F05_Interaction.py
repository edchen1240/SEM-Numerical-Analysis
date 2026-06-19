"""
[F05_Interaction.py]
Purpose: Functions ask for user input.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import sys, os, openpyxl, tkinter, datetime, shutil
import pandas as pd
import numpy as np



#[1] Interaction - start


def ask_for_input(question_message, readback=True, allow_empty=True):
    """
    Ed Chen's function, 2025-06-06.
    """
    print('\n[ask_for_input] ', end='')
    while True:
        str_find = input(question_message).strip()
        #[3] Check if str_find is not empty or if empty input is allowed
        if str_find or allow_empty:  
            if readback:
                print(f'-- User said: {str_find}')
            return str_find
        else:
            print('-- Please enter a non-empty value!')

def question_and_if_yes_action(yes_no_question, action_if_yes=None):
    """
    2025-0912-0958: Keep this function updated in F05_Interaction.py.
    """
    #[1] Asks a yes/no question, and if the answer is yes, executes the given action (function).
    answer = ask_for_input(yes_no_question)
    if any(keyword in answer.lower() for keyword in ['yes', 'ye', 'y', 'ok', 'okey', 'sure', 'go', 'aff', 'affirmative']):
        print('-- User agreed to proceed.', answer)
        return action_if_yes() if action_if_yes is not None else True
    else:
        sys.exit('-- User chose to exit.')

   
#[1] Interaction - end







#[2]  - start


#[2]  - end


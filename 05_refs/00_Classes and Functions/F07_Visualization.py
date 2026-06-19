"""
[F07_Visualization.py]
Purpose: Useful visualization functions.
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








#[1] Simple Visualization- Start

def add_text_in_plot_with_new_line_and_tab(ax, pos_x, pos_y, text, 
                                           linespace=0.05, ft_size=12, color='gray',
                                           tab_replacement='    '):
    #[1] Replace tabs with spaces
    formatted_text = text.replace("\t", tab_replacement)
    
    #[2] Add text line by line
    lines = formatted_text.split("\n")
    i_pos_y = pos_y
    for i, line in enumerate(lines):
        #[3] Adjust position for each line.
        if line and (line[0] == '[' or line[-1] == ':'): 
            i_pos_y -= linespace * 1.2
        else:
            i_pos_y -= linespace 
        
        #[4] Add text.
        ax.text(
            pos_x, i_pos_y,
            line,
            transform=ax.transAxes,
            fontsize=ft_size, 
            color = color,
            verticalalignment='top',
            horizontalalignment='left')    



def array_2D_visualization(array_or_tensor, text_title, path_save=None, dpi=300):
    """
    Visualize a 2D numpy array or PyTorch tensor with a blue-white-red colormap.
    Shows statistics and optionally saves the figure.
    """
    # [1] Convert to numpy array if input is a tensor.
    if isinstance(array_or_tensor, torch.Tensor):
        arr_input = array_or_tensor.detach().cpu().numpy()
    elif isinstance(array_or_tensor, np.ndarray):
        arr_input = array_or_tensor
    else:
        raise TypeError('Input must be a numpy array or a PyTorch tensor.')

    # [2] Check array shape.
    if arr_input.ndim != 2:
        raise ValueError('Input must be 2D (matrix).')
    h, w = arr_input.shape
    if h == 0 or w == 0:
        raise ValueError('Input array must not be empty.')
    if h > 200 or w > 200:
        print(f'-- Array ({text_title}) exceeds 200x200 ({h}x{w}), too large for visualization. Skipping...')
        return

    # [3] Font sizes for better visibility
    flex_bounds = False
    fig_h, fig_w = int(max(h, 5) * 0.5), int(max(w, 5) * 0.5)
    fig_size = (fig_w, fig_h)
    if fig_w < 5:
        fs_title, ft_text, linespace = 8, 4, 0.03
    else:
        fs_title, ft_text, linespace = 16, 8, 0.04

    #[4] Hanld text vertical position for differnt height.
    pos_y = _determine_pos_y_from_h(h)

    # [6] Create a figure and visualize 2D array.
    plt.figure(figsize=fig_size, dpi=dpi)
    if flex_bounds:
        max_abs_val = np.max(np.abs(arr_input))
    else:
        max_abs_val = 10
    plt.imshow(arr_input, cmap='seismic', vmin=-max_abs_val, vmax=max_abs_val)

    # [7] Optionally add gridlines for very small matrices.
    if h <= 5 and w <= 5:
        plt.grid(which='major', color='black', linestyle='-', linewidth=2)
        plt.xticks(np.arange(w))
        plt.yticks(np.arange(h))
    else:
        plt.xticks([])
        plt.yticks([])

    # [8] Show statistics.
    stat_max = np.max(arr_input)
    stat_min = np.min(arr_input)
    stat_mean = np.mean(arr_input)
    stat_med = np.median(arr_input)
    stat_std = np.std(arr_input)
    text_stat = f'Max={stat_max:.3f}, Min={stat_min:.3f}, Mean={stat_mean:.3f}, Median={stat_med:.3f}, STD={stat_std:.3f}'
    
    #[10] Place the text in the top-left corner of the plot.
    ax = plt.gca()
    add_text_in_plot_with_new_line_and_tab(ax, -0.01, pos_y, text_stat, linespace, ft_text, 'gray')
    plt.axis('off')

    # [12] Set title and layout
    plt.title(text_title, fontsize=fs_title)
    #plt.subtitle(text_stat, fontsize=ft_text, y=1, color='gray')
    plt.tight_layout(rect=[0, 0, 1, 0.7])

    # [15] Save or show the figure.
    if path_save is not None:
        plt.savefig(path_save, bbox_inches='tight')
        plt.close()
        print(f'-- Plot saved to {path_save}')
    else:
        plt.show()



def plot_single_confusion_matrices(arr_pred, arr_gt, list_labels, 
                          title='Device/Wire Flag Confusion Matrix', path_save=None):
    """
    arr_gt is the ground truth, arr_pred is the predicted labels.
    list_labels is a list of labels for the confusion matrix.
    2025-0813-2106: Rename Node to Wire.
    """
    def _compute_precision_recall_f1(cm):
        #[1] Extract values from confusion matrix
        tn, fp = cm[0, 0], cm[0, 1]
        fn, tp = cm[1, 0], cm[1, 1]
        #[2] Calculate precision
        cm_precis = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
        #[3] Calculate recall
        cm_recall = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
        #[4] Calculate F1 score
        cm_f1 = 2 * cm_precis * cm_recall / (cm_precis + cm_recall) if (cm_precis + cm_recall) > 0 else 0
        return cm_precis, cm_recall, cm_f1


    #[1] Validate inputs.
    if arr_pred.shape != arr_gt.shape:
        raise ValueError('arr_pred and arr_gt must have the same shape.')
    if len(list_labels) != arr_pred.shape[1]:
        raise ValueError('list_labels must match the number of classes in arr_pred.')
    if len(list_labels) >= 10:
        raise ValueError('list_labels must have less than 10 classes for visualization purposes.')

    #[2] Settings
    cmap = plt.cm.Blues  # Corrected colormap name
    fs_title, fs_subtitle, fs_axis = 24, 14, 12
    figsize_val = 4
    data_count = arr_gt.shape[0] 
    vmax_val = (data_count//100 + 1) * 100
    #print(f'vmax_val: {vmax_val}')

    #[3] Create DataFrame for precision, recall, and F1 scores
    metrics_data = {label: [] for label in list_labels}

    #[4] Store images of each confusion matrix
    images = []
  
    #[5] Iterate through labels and generate confusion matrices
    for i, i_label in enumerate(list_labels):

        #[1] Create confusion matrix for each label
        cm = confusion_matrix(arr_gt[:, i], arr_pred[:, i], labels=[0, 1])
        cm_precis, cm_recall, cm_f1 = _compute_precision_recall_f1(cm)
        metrics_data[i_label] = [cm_precis, cm_recall, cm_f1]

        #[2] Plot confusion matrix
        fig, ax = plt.subplots(figsize=(figsize_val, figsize_val))
        sns.heatmap(cm, annot=True, fmt='d', cmap=cmap,
                    xticklabels=[f'0', f'1'], yticklabels=[f'0', f'1'], ax=ax,
                    vmin=0, vmax=vmax_val)
        ax.set_aspect('equal', adjustable='box')
        text_i_title = f'Label: {i_label}.   (p,r,F1):\n{cm_precis:.2f}%, {cm_recall:.2f}%, {cm_f1:.2f}%'
        ax.set_title(text_i_title, fontsize=fs_subtitle, y=-0.2, ha='center')
        ax.set_xlabel('Predicted', fontsize=fs_axis)
        ax.xaxis.set_label_position('top')
        ax.xaxis.tick_top()
        ax.set_ylabel('True', fontsize=fs_axis)
        plt.tight_layout()

        #[5] Save figure to a BytesIO buffer
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        img = Image.open(buf)
        images.append(img)


    # [6] Create DataFrame from metrics data
    df_prF1 = pd.DataFrame(metrics_data, index=['Precision', 'Recall', 'F1 Score']).round(4)    

    # [6] Horizontally stack the images
    widths, heights = zip(*(im.size for im in images))
    total_width = sum(widths)
    max_height = max(heights)
    combined_img = Image.new('RGB', (total_width, max_height), (255, 255, 255))

    x_offset = 0
    for im in images:
        combined_img.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    #[8] Add a main title at the top
    title_height = figsize_val * 10  # Adjust as needed for font size
    final_img = Image.new('RGB', (total_width, max_height + title_height), (255, 255, 255))
    draw = ImageDraw.Draw(final_img)

    #[10] Optional: Use a truetype font if available
    try:
        font = ImageFont.truetype("arial.ttf", fs_title)
    except:
        try:
            path_font_linux = '/u/chened/fs5/sandbox/03_Additional Lib/ed_font/arial.ttf'
            font = ImageFont.truetype(path_font_linux, fs_title)
        except:
            font = ImageFont.load_default()

    #[12] Draw the title
    bbox = draw.textbbox((0, 0), title, font=font)
    w_tb, h_tb, pad = bbox[2] - bbox[0], bbox[3] - bbox[1], 10
    draw.text(((total_width - w_tb) // 2, (title_height - h_tb) // 2), title, fill=(0, 0, 0), font=font)
    final_img.paste(combined_img, (0, title_height))

    # [15] Save or show the final image
    if path_save is not None:
        final_img.save(path_save)
        print(f'-- Plot saved to {path_save}')
    else:
        final_img.show()

    return df_prF1

#[1] Simple Visualization - End






















#[3] Memory - start



            
#[3] Memory - end






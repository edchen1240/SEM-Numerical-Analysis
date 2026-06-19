"""
[C04_PixelStatistics.py]
Purpose: store function for XYZ linear motion stage related.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import os
import cv2
import numpy as np
from collections import Counter
import pandas as pd
from tabulate import tabulate
from PIL import Image, ImageDraw, ImageFont
import mpl_toolkits.mplot3d as m3d

import matplotlib.pyplot as plt
import matplotlib.ticker as plticker



import sys
sys.path.append(r'D:\01_Floor\a_Ed\09_EECS\10_Python\00_Classes and Functions')
import F02_File as F02_File

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from sklearn.linear_model import LinearRegression
import numpy as np

#[] Change text size
font_size = 100
font_path = r'C:\Windows\Fonts\arial.ttf'  # Update this path to a specific font file on your system.

if os.path.exists(font_path):
    print('--Font file exists.')
else:
    print('--Font file does not exist.')
try:
    font = ImageFont.truetype(font_path, font_size)
except IOError:
    print(f'--Could not use the font from {font_path}, using the default font.')
    font = ImageFont.load_default()





class PixelStatistics:
    def __init__(self, path_image):
        print('\n[PixelStatistics]')
        self.path_image = path_image
        self.dir_image = os.path.dirname(path_image)
        self.image_basename = os.path.basename(self.path_image)
        print(f'--File Name: {self.image_basename}')
        #[1-1] Read image as array
        self.array_image_BGR = cv2.imread(self.path_image)
        #[1-2] Get image shape.
        h, w, c = self.array_image_BGR.shape
        print(f'--Image Shape (H, W, C): {h, w, c}')
        #[1-3] Check if dire exist.
        dir = os.path.splitext(path_image)[0]
        try:
            os.mkdir(dir)
            print(f'--Directory was not exists. Just made one. {dir}')
        except FileExistsError:
            #print(f'--Directory already exists. Skipping directory creation. {dir}')
            print()

    
    def color_channel_stat(self, ratio=20, limit_criterion = 2):
        
        """
        Write a code to choose between ratio and maxi pixel.
        
        """
        print('\n[color_channel_stat]')
        #[2-1] Reduce
        global array_color_stat
        #[2-2] Compress
        h, w, c = self.array_image_BGR.shape
        new_w = w // ratio
        new_h = h // ratio
        print(f'--Reduced Image Shape (H, W, C): {new_h}, {new_w}, {c}.')
        self.array_image_BGR_reduced = cv2.resize(self.array_image_BGR, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        
        #limit_criterion = 2 # Choose 2 to enclose 95% of data, or 3 to enclose 99.7% of data.
        #[] Blue channel statistics
        blu_channel = self.array_image_BGR_reduced[:,:,0] # Blue
        self.blu_mean_int = round(np.mean(blu_channel))
        self.blu_std_int = round(np.std(blu_channel))
        self.blu_upper = round(self.blu_mean_int + limit_criterion* self.blu_std_int)
        self.blu_lower = round(self.blu_mean_int - limit_criterion* self.blu_std_int)
        #[] Green channel statistics
        gre_channel = self.array_image_BGR_reduced[:,:,1] # Green
        self.gre_mean_int = round(np.mean(gre_channel))
        self.gre_std_int = round(np.std(gre_channel))
        self.gre_upper = round(self.gre_mean_int + limit_criterion* self.gre_std_int)
        self.gre_lower = round(self.gre_mean_int - limit_criterion* self.gre_std_int)
        #[] Red channel statistics
        red_channel = self.array_image_BGR_reduced[:,:,2] # Red
        self.red_mean_int = round(np.mean(red_channel))
        self.red_std_int = round(np.std(red_channel))
        self.red_upper = round(self.red_mean_int + limit_criterion* self.red_std_int)
        self.red_lower = round(self.red_mean_int - limit_criterion* self.red_std_int)

        list_title = ['max', 'min', 'mean', 'std', 'mean-2std', 'mean+2std']
        print(f'--{list_title}')
        self.blu_stat = [np.max(blu_channel), np.min(blu_channel), self.blu_mean_int, self.blu_std_int, self.blu_lower, self.blu_upper]
        self.gre_stat = [np.max(gre_channel), np.min(gre_channel), self.gre_mean_int, self.gre_std_int, self.gre_lower, self.gre_upper]
        self.red_stat = [np.max(red_channel), np.min(red_channel), self.red_mean_int, self.red_std_int, self.red_lower, self.red_upper]
        array_color_stat_RGB = np.array([self.red_stat, self.gre_stat, self.blu_stat])
        print(f'--array_color_stat_RGB (limit_criterion ={limit_criterion})\n{array_color_stat_RGB}')
        return array_color_stat_RGB
      
    def reshape_3Dpixel_into_2Dlist(self):
        print('\n[reshape_3Dpixel_into_2Dlist]')
        array_BGR_reduced_reshaped = self.array_image_BGR_reduced.reshape(-1, 3)
        if array_BGR_reduced_reshaped.shape[0] > 5000:
            raise ValueError("There are more than 5000 pixels. Please further reduce the size in the previous step before continuing.")
        #[] Rank the pixels
        list_third_elements = array_BGR_reduced_reshaped[:, 2]
        third_sorted_indices = np.argsort(list_third_elements)
        array_BGR_reduced_reshaped = array_BGR_reduced_reshaped[third_sorted_indices]
        list_second_elements = array_BGR_reduced_reshaped[:, 1]
        second_sorted_indices = np.argsort(list_second_elements)
        array_BGR_reduced_reshaped = array_BGR_reduced_reshaped[second_sorted_indices]
        list_first_elements = array_BGR_reduced_reshaped[:, 0]
        first_sorted_indices = np.argsort(list_first_elements)
        array_BGR_reduced_reshaped = array_BGR_reduced_reshaped[first_sorted_indices]
        #[] Rearrange from BGR to RGB.
        self.array_RGB_reduced_reshaped = array_BGR_reduced_reshaped[:, ::-1]
        
        #[] Do an SVD on the mean-centered data.
        self.mean_point = np.mean(self.array_RGB_reduced_reshaped, axis=0) #[] Calculate mean point for other functions.
        uu, dd, vv = np.linalg.svd(self.array_RGB_reduced_reshaped - self.mean_point)
        print('[Singular value decomposition] to find line vector. (vv[0], the direction of maximum variance.)') 
        print(f'--[uu] shape: {uu.shape}; [dd] shape: {dd.shape}; [vv] shape: {vv.shape}; ')
        print(f'--[vv] value:\n', vv, '\n')
        #print("The matrix vv contains the principal directions of the data.")
        #print("The first row vv[0] is the direction of maximum variance")
        #print(", and it's the direction vector of the 1D regression line in the 3D space.")
        self.line_vector = vv[0]
        print('--array_RGB_reduced_reshaped (R, G, B):', self.array_RGB_reduced_reshaped.shape)
        print('--self.mean_point:', self.mean_point)
        print('--self.line_vector', self.line_vector, 'vv[0], the direction of maximum variance.')
        print()


    def pixel_count_return_df(self): #0.0545 seconds.
        print('\n[pixel_count_return_df]')
        # Convert the 2D array into a list of tuples (BGR values)
        color_tuples = [tuple(pixel) for pixel in self.array_RGB_reduced_reshaped]
        # Use Counter to count the occurrences of each color
        color_counts = Counter(color_tuples)
        df_color_counts = pd.DataFrame.from_dict(color_counts, orient='index', columns=['Count'])
        df_color_counts.index.name = 'Color'
        df_color_counts[['Red', 'Green', 'Blue']] = pd.DataFrame(df_color_counts.index.tolist(), index=df_color_counts.index)
        df_color_counts['RGB'] = df_color_counts.apply(lambda row: (row['Red'], row['Green'], row['Blue']), axis=1)
        #print(df_color_counts['RGB'])
        df_color_counts['dist_line'] = df_color_counts['RGB'].apply(lambda x: distance_to_line(x, self.mean_point, self.line_vector))
        df_color_counts['dist_mean'] = df_color_counts['RGB'].apply(lambda x: np.linalg.norm(x - self.mean_point))

        #[] Statistics for distance to line.
        list_dist_line = df_color_counts['dist_line']
        list_dist_line_max = round(max(list_dist_line), 2)
        list_dist_line_min = round(min(list_dist_line), 2)
        list_dist_line_mean = round(np.mean(list_dist_line), 2)
        list_dist_line_std = round(np.std(list_dist_line), 2)
        print('--[Distance to line] (max, min, mean, std):', list_dist_line_max, list_dist_line_min, list_dist_line_mean, list_dist_line_std)
        
        #[] Statistics for distance to mean.
        list_dist_mean = df_color_counts['dist_mean']
        list_dist_mean_max = round(max(list_dist_mean), 2)
        list_dist_mean_min = round(min(list_dist_mean), 2)
        list_dist_mean_mean = round(np.mean(list_dist_mean), 2)
        list_dist_mean_std = round(np.std(list_dist_mean), 2)
        print('--[Distance to mean] (max, min, mean, std):', list_dist_mean_max, list_dist_mean_min, list_dist_mean_mean, list_dist_mean_std)

        self.df_color_counts = df_color_counts.sort_values(by=['Count'], ascending=False)
        print('--Dataframe size:', self.df_color_counts.shape)
        print('--Showing first 10 rows of the df_color_counts:')
        df_first_10_rows = self.df_color_counts.head(10)
        print(tabulate(df_first_10_rows, headers='keys', tablefmt='orgtbl'))
        print()
        return self.df_color_counts


    def plot_pixel_3D_heatmap(self, path_save = None):
        print('\n[plot_pixel_3D_heatmap]')
        list_red = self.df_color_counts['Red'].tolist()
        list_green = self.df_color_counts['Green'].tolist()
        list_blue = self.df_color_counts['Blue'].tolist()
        list_count = self.df_color_counts['Count'].tolist()
    
        #[02-02] Set up the 3D plot
        fig = plt.figure(figsize=(16, 4))
        alpha_value = 0.5

        """# Create a grid of (x, y) points
        x_range = np.linspace(0, 255, 100)  # Adjust the range and number of points as needed
        y_range = np.linspace(0, 255, 100)
        x_points, y_points = np.meshgrid(x_range, y_range)

        # Calculate z values for each (x, y) point using the equation z = ax + by + c
        #z_points = self.a * x_points + self.b * y_points + self.c"""

        #[02-03] Plot the 3D scatter plot
        ax1 = fig.add_subplot(141, projection='3d')
        ax1.set_xlabel('list_red')
        ax1.set_ylabel('list_green')
        ax1.set_zlabel('list_blue')
        ax1.set_xlim(0, 255)
        ax1.set_ylim(0, 255)
        ax1.set_zlim(0, 255) 
        #ax1.plot_surface(list_red, list_green, list_blue, cmap='gray', alpha=0.5)
        sc1 = ax1.scatter(list_red, list_green, list_blue, c = list_count, cmap='cool', alpha=alpha_value, s=3)
        plt.colorbar(sc1, ax=ax1, label='list_count')

        #[02-04] Plot the 2D scatter plots
        ax2 = fig.add_subplot(142)
        ax2.set_xlabel('list_red')
        ax2.set_ylabel('list_green')
        ax2.set_xlim(0, 255)
        ax2.set_ylim(0, 255)
        sc2 = ax2.scatter(list_red, list_green, c = list_count, cmap='cool', alpha=alpha_value, s=3)
        plt.colorbar(sc2, ax=ax2, label='list_count')

        ax3 = fig.add_subplot(143)
        ax3.set_xlabel('list_green')
        ax3.set_ylabel('list_blue')
        ax3.set_xlim(0, 255)
        ax3.set_ylim(0, 255)
        sc3 = ax3.scatter(list_green, list_blue, c = list_count, cmap='cool', alpha=alpha_value, s=3)
        plt.colorbar(sc3, ax=ax3, label='list_count')

        ax4 = fig.add_subplot(144)
        ax4.set_xlabel('list_blue')
        ax4.set_ylabel('list_red')
        ax4.set_xlim(0, 255)
        ax4.set_ylim(0, 255)
        sc4 = ax4.scatter(list_blue, list_red, c = list_count, cmap='cool', alpha=alpha_value, s=3)
        plt.colorbar(sc4, ax=ax4, label='list_count')

        #[02-05] Show or save the plot
        fig.suptitle('Pixel 3D Heatmap')
        plt.tight_layout()
        #[02-06] Save plot as png
        if path_save:
            plt.savefig(path_save)
            print(f'--Plot saved at {path_save}')
        else:
            plt.show()
    

    def generate_color_chart_image(self, path_save):
        print('\n[generate_color_chart_image]')
        h, w = 900, 900
        array_color_chart_image = np.zeros((h, w, 3))

        h_0_3, h_1_3, h_2_3, h_3_3 = 0, h//3, 2*h//3, h
        w_0_3, w_1_3, w_2_3, w_3_3 = 0, w//3, 2*w//3, w
        
        #[1] Define color blocks
        color_blocks = [
            (slice(h_0_3, h_1_3), slice(w_0_3, w_1_3), [self.blu_upper, self.gre_upper, self.red_upper]),
            (slice(h_0_3, h_1_3), slice(w_1_3, w_2_3), [self.blu_upper, self.gre_upper, self.red_lower]),
            (slice(h_0_3, h_1_3), slice(w_2_3, w_3_3), [self.blu_upper, self.gre_lower, self.red_lower]),
            (slice(h_1_3, h_2_3), slice(w_0_3, w_1_3), [self.blu_lower, self.gre_upper, self.red_upper]),
            (slice(h_2_3, h_3_3), slice(w_0_3, w_1_3), [self.blu_lower, self.gre_lower, self.red_upper]),
            (slice(h_1_3, h_2_3), slice(w_2_3, w_3_3), [self.blu_upper, self.gre_lower, self.red_upper]),
            (slice(h_2_3, h_3_3), slice(w_1_3, w_2_3), [self.blu_lower, self.gre_upper, self.red_lower]),
            (slice(h_2_3, h_3_3), slice(w_2_3, w_3_3), [self.blu_lower, self.gre_lower, self.red_lower]),
            (slice(h_1_3, h_2_3), slice(w_1_3, w_2_3), [self.blu_mean_int, self.gre_mean_int, self.red_mean_int]),
        ]

        #[2] Assign colors to blocks
        for h_slice, w_slice, color in color_blocks:
            array_color_chart_image[h_slice, w_slice] = color

        #[3] Save image
        cv2.imwrite(path_save, array_color_chart_image)
        
        #[4] Change text size
        font_size = 30
        font_path = r'C:\Windows\Fonts'  # Update this path to a valid font file on your system
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"Could not use the font from {font_path}, using the default font.")
            font = ImageFont.load_default()
        
        
        
        #[5] Make value
        image_PIL = Image.open(path_save)
        I1 = ImageDraw.Draw(image_PIL)
        text_fill = (0, 0, 0)
        I1.text((h_0_3 + 10, w_0_3 + 10), f'RGB({self.red_upper},{self.gre_upper},{self.blu_upper})', fill=text_fill, font=font)
        I1.text((h_0_3 + 10, w_1_3 + 10), f'RGB({self.red_lower},{self.gre_upper},{self.blu_upper})', fill=text_fill, font=font)
        I1.text((h_0_3 + 10, w_2_3 + 10), f'RGB({self.red_lower},{self.gre_lower},{self.blu_upper})', fill=text_fill, font=font)
        I1.text((h_1_3 + 10, w_0_3 + 10), f'RGB({self.red_upper},{self.gre_upper},{self.blu_lower})', fill=text_fill, font=font)
        I1.text((h_2_3 + 10, w_0_3 + 10), f'RGB({self.red_upper},{self.gre_lower},{self.blu_lower})', fill=text_fill, font=font)
        I1.text((h_1_3 + 10, w_2_3 + 10), f'RGB({self.red_upper},{self.gre_lower},{self.blu_upper})', fill=text_fill, font=font)
        I1.text((h_2_3 + 10, w_1_3 + 10), f'RGB({self.red_lower},{self.gre_upper},{self.blu_lower})', fill=text_fill, font=font)
        I1.text((h_2_3 + 10, w_2_3 + 10), f'RGB({self.red_lower},{self.gre_lower},{self.blu_lower})', fill=text_fill, font=font)
        I1.text((h_1_3 + 10, w_1_3 + 10), f'RGB({self.red_mean_int},{self.gre_mean_int},{self.blu_mean_int})', fill=text_fill, font=font)

        
        """#[5] Make value
        image_PIL = Image.open(path_save)
        I1 = ImageDraw.Draw(image_PIL)
        text_fill = (0, 0, 0)
        I1.text((h_0_3 + 10, w_0_3 + 10), 'RGB('+str(self.red_upper)+','+str(self.gre_upper)+','+str(self.blu_upper)+')', fill=text_fill, font=font)
        I1.text((h_0_3 + 10, w_1_3 + 10), 'RGB('+str(self.red_lower)+','+str(self.gre_upper)+','+str(self.blu_upper)+')', fill=text_fill, font=font)
        I1.text((h_0_3 + 10, w_2_3 + 10), 'RGB('+str(self.red_lower)+','+str(self.gre_lower)+','+str(self.blu_upper)+')', fill=text_fill, font=font)
        I1.text((h_1_3 + 10, w_0_3 + 10), 'RGB('+str(self.red_upper)+','+str(self.gre_upper)+','+str(self.blu_lower)+')', fill=text_fill, font=font)
        I1.text((h_2_3 + 10, w_0_3 + 10), 'RGB('+str(self.red_upper)+','+str(self.gre_lower)+','+str(self.blu_lower)+')', fill=text_fill, font=font)
        I1.text((h_1_3 + 10, w_2_3 + 10), 'RGB('+str(self.red_upper)+','+str(self.gre_lower)+','+str(self.blu_upper)+')', fill=text_fill, font=font)
        I1.text((h_2_3 + 10, w_1_3 + 10), 'RGB('+str(self.red_lower)+','+str(self.gre_upper)+','+str(self.blu_lower)+')', fill=text_fill, font=font)
        I1.text((h_2_3 + 10, w_2_3 + 10), 'RGB('+str(self.red_lower)+','+str(self.gre_lower)+','+str(self.blu_lower)+')', fill=text_fill, font=font)
        I1.text((h_1_3 + 10, w_1_3 + 10), 'RGB('+str(self.red_mean_int)+','+str(self.gre_mean_int)+','+str(self.blu_mean_int)+')', fill=text_fill, font=font)"""

        #[6] Save color chart
        image_PIL.save(path_save)

        return array_color_chart_image



    def generate_mask_with_color_statistics(self, array_color_stat_RGB, path_image, replace_old_dis, with_new_dis):
        print('\n[generate_mask_with_color_statistics]')
        dir = os.path.dirname(path_image)
        array_image = cv2.imread(path_image)
        if array_color_stat_RGB.shape != (3, 6):
            raise ValueError("The shape of array_color_stat doesn't seems to be correct.")   
        
        red_lower, red_upper = array_color_stat_RGB[0][4], array_color_stat_RGB[0][5]
        gre_lower, gre_upper = array_color_stat_RGB[1][4], array_color_stat_RGB[1][5]
        blu_lower, blu_upper = array_color_stat_RGB[2][4], array_color_stat_RGB[2][5]
        #print(red_lower, red_upper, gre_lower, gre_upper, blu_lower, blu_upper)
        
        red_mask = (array_image[:,:,2] > red_lower) & (array_image[:,:,2] < red_upper)
        gre_mask = (array_image[:,:,1] > gre_lower) & (array_image[:,:,1] < gre_upper)
        blu_mask = (array_image[:,:,0] > blu_lower) & (array_image[:,:,0] < blu_upper)

        combined_mask = blu_mask & gre_mask & red_mask

        array_mask_image = np.where(combined_mask[..., None], [250, 250, 250], [10, 10, 10])
        
        #[] Calculate ratio
        cnt_within = np.sum(combined_mask)
        cnt_outof = combined_mask.size - cnt_within
        with_in_ratio_pct = round(100 * cnt_within / (cnt_within + cnt_outof), 2)
        

        # Save image
        image_basename = os.path.basename(path_image)
        print(image_basename, '[color_statistics] with_in_ratio_pct:', with_in_ratio_pct, '%')
        image_basename = image_basename.replace(replace_old_dis, with_new_dis)
        path_save_image = os.path.join(dir, image_basename)
        cv2.imwrite(path_save_image, array_mask_image)
        return array_mask_image
    
    def generate_mask_with_regression_line(self, mean_point, line_vector, path_image, replace_old_dis, with_new_dis):
        print('\n[generate_mask_with_regression_line]')
        dir = os.path.dirname(path_image)
        array_image_BGR = cv2.imread(path_image)
        array_image_RGB = cv2.cvtColor(array_image_BGR, cv2.COLOR_BGR2RGB)
        h, w, c = array_image_RGB.shape
        array_mask_image = np.full((h, w, 3), 10)
        cnt_within = 0
        for iter_h in range(0, h):
            for iter_w in  range(0, w):
                test_point = array_image_RGB[iter_h][iter_w]
                dist_to_line = distance_to_line(test_point, mean_point, line_vector)
                dist_to_mean = round(np.linalg.norm(test_point - mean_point), 4)
                #print('Point:', test_point, 'Location:', iter_h, iter_w, 'dist_to_line:',dist_to_line, 'dist_to_mean:', dist_to_mean)
                #[Importabt Parameter] dist_to_line Best 5, can be adjusted to 4 or 6.
                if  dist_to_line < 6 and dist_to_mean < 40: #[Importabt Parameter] dist_to_mean Best 40.
                    array_mask_image[iter_h][iter_w] = (250, 250, 250)
                    cnt_within +=1
        
        #[] Calculate ratio
        cnt_outof = h*w - cnt_within
        with_in_ratio_pct = round(100 * cnt_within / (cnt_within + cnt_outof), 2)
        
        #[] Save image
        image_basename = str(os.path.basename(path_image))
        print(image_basename, '[regression_line] with_in_ratio_pct:', with_in_ratio_pct, '%')
        image_basename = image_basename.replace(replace_old_dis, with_new_dis)
        path_save_image = os.path.join(dir, image_basename)
        cv2.imwrite(path_save_image, array_mask_image)
        return array_mask_image
                    
        
        

    def find_regression_line_in_3D_and_plot(self, path_save=None):
        print('\n[find_regression_line_in_3D_and_plot]')

        """
        Sample data of self.array_RGB_reduced_reshaped (positive integers from 0-255):
        [[188 140  93]
        [187 139  94]
        [186 138  94]
        [185 139  95]
        [185 139  95]
        [188 141  95]
        [186 139  95]]
        """
        # Centralize the data
        #print('self.array_RGB_reduced_reshaped:\n', self.array_RGB_reduced_reshaped[:10])
        self.mean_point = np.mean(self.array_RGB_reduced_reshaped, axis=0)
        #centralized_data = self.array_RGB_reduced_reshaped - mean_point
        
        X_data = self.array_RGB_reduced_reshaped[:, 0]
        Y_data = self.array_RGB_reduced_reshaped[:, 1]
        Z_data = self.array_RGB_reduced_reshaped[:, 2]
        
        
        #[] Plot
        fig = plt.figure(figsize=(8, 7))
        alpha_value = 0.5
    
        
        #[] Figure-1
        ax1 = fig.add_subplot(221, projection='3d')
        RGB_max_std_xn = 3*round(max(self.red_stat[4], self.gre_stat[4], self.blu_stat[4]), 0)
        #X_limit = self.red_mean_int - RGB_max_std_xn, self.red_mean_int + RGB_max_std_xn
        #Y_limit = self.gre_mean_int - RGB_max_std_xn, self.gre_mean_int + RGB_max_std_xn
        #Z_limit = self.blu_mean_int - RGB_max_std_xn, self.blu_mean_int + RGB_max_std_xn
        ax1.set_xlim(0, 255)
        ax1.set_ylim(0, 255)
        ax1.set_zlim(0, 255)
        ax1.set_xlabel('Red channel')
        ax1.set_ylabel('Green channel')
        ax1.set_zlabel('Blue channel')
        ax1.scatter(X_data, Y_data, Z_data, color='turquoise', alpha = alpha_value, s=2)
        
        
        #[] Figure-2
        ax2 = fig.add_subplot(222, projection='3d')
        ax2.set_xlim(160, 250)
        ax2.set_ylim(110, 200)
        ax2.set_zlim(90, 160)
        ax2.set_xlabel('Red channel')
        ax2.set_ylabel('Green channel')
        ax2.set_zlabel('Blue channel')
        ax2.scatter(X_data, Y_data, Z_data, color='turquoise', alpha = alpha_value/2, s=2)
        
        #[] Generate points along the line defined by line_vector
        linepts = self.line_vector * np.mgrid[0:256:255][:, np.newaxis]

        #[] Shift by the mean to get the line in the right place
        linepts = np.outer(np.linspace(-500, 500, 1000), self.line_vector)
        linepts += self.mean_point


        #[] Figure-3
        ax3 = fig.add_subplot(223, projection='3d')
        ax3.set_xlim(0, 255)
        ax3.set_ylim(0, 255)
        ax3.set_zlim(0, 255)
        ax3.set_xlabel('Red channel')
        ax3.set_ylabel('Green channel')
        ax3.set_zlabel('Blue channel')
        ax3.plot3D(*linepts.T, color='firebrick')
        ax3.scatter3D(*self.array_RGB_reduced_reshaped.T, color='turquoise', alpha = alpha_value, s=2)
        
        #[] Figure-4
        ax4 = fig.add_subplot(224, projection='3d')
        ax4.set_xlim(160, 250)
        ax4.set_ylim(110, 200)
        ax4.set_zlim(90, 160)
        ax4.set_xlabel('Red channel')
        ax4.set_ylabel('Green channel')
        ax4.set_zlabel('Blue channel')
        ax4.plot3D(*linepts.T, color='firebrick')
        ax4.scatter3D(*self.array_RGB_reduced_reshaped.T, color='turquoise', alpha = alpha_value/2, s=2)
        
       
        #[02-06] Save plot as png
        fig.suptitle('regression_line_in_3D')
        if path_save:
            plt.savefig(path_save)
            print(f'--Plot saved at {path_save}')
        else:
            plt.show()
        sys.exit()
        






def distance_to_line(test_point, mean_point, line_vector):
    """
    This function will be execute many times. Do not print.
    *test_point is the input point to test.
    *self.mean_point can be seen as a point on the line.
    *line_vector is directional vector of the line.
    """
    mean_to_point_vector = test_point - mean_point
    cross_product = np.cross(mean_to_point_vector, line_vector)
    distance = round(np.linalg.norm(cross_product) / np.linalg.norm(line_vector), 4)
    return distance
    
#sys.exit()





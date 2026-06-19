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


import sys
sys.path.append(r'D:\01_Floor\a_Ed\09_EECS\10_Python\00_Classes and Functions')
import F02_File as F02_File

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class PixelStatistics:
    def __init__(self, path_image):
        self.path_image = path_image
        self.dir_image = os.path.dirname(path_image)
        self.image_basename = os.path.basename(self.path_image)
        print('PixelStatistics initiation complete.')

    def image_info(self):
        print('[File Name]:', self.image_basename)
        self.array_image = cv2.imread(self.path_image)
        h, w, c = self.array_image.shape
        print('[Image Shape] (H, W, C):', h, w, c, end='\n')
        print()
        
        
    def color_channel_stat(self, ratio=20, limit_criterion = 2):
        #[] Reduce
        global blu_stat
        global gre_stat
        global red_stat
        #[] Compress
        h, w, c = self.array_image.shape
        new_w = w // ratio
        new_h = h // ratio
        print('[Reduced Image Shape] (H, W, C):', new_h, new_w, c)
        self.array_image_reduced = cv2.resize(self.array_image, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        
        #limit_criterion = 2 # Choose 2 to enclose 95% of data, or 3 to enclose 99.7% of data.
        #[] Blue channel statistics
        blu_channel = self.array_image_reduced[:,:,0] # Blue
        blu_mean = np.mean(blu_channel)
        self.blu_mean_int = round(blu_mean)
        blu_std = np.std(blu_channel)
        self.blu_upper = round(blu_mean + limit_criterion* blu_std)
        self.blu_lower = round(blu_mean - limit_criterion* blu_std )
        #[] Green channel statistics
        gre_channel = self.array_image_reduced[:,:,1] # Green
        gre_mean = np.mean(gre_channel)
        self.gre_mean_int = round(gre_mean)
        gre_std = np.std(gre_channel)
        self.gre_upper = round(gre_mean + limit_criterion* gre_std)
        self.gre_lower = round(gre_mean - limit_criterion* gre_std )
        #[] Red channel statistics
        red_channel = self.array_image_reduced[:,:,2] # Red
        red_mean = np.mean(red_channel)
        self.red_mean_int = round(red_mean)
        red_std = np.std(red_channel)
        self.red_upper = round(red_mean + limit_criterion* red_std)
        self.red_lower = round(red_mean - limit_criterion* red_std )

        blu_stat = [np.max(blu_channel), np.min(blu_channel), round(blu_mean, 2), round(blu_std, 2), self.blu_upper, self.blu_lower]
        gre_stat = [np.max(gre_channel), np.min(gre_channel), round(gre_mean, 2), round(gre_std, 2), self.gre_upper, self.gre_lower]
        red_stat = [np.max(red_channel), np.min(red_channel), round(red_mean, 2), round(red_std, 2), self.red_upper, self.red_lower]
        print('[color_channel_stat]: (max, min, mean, std, mean+2std, mean-2std)')
        print('[Red   channel]:', red_stat)
        print('[Green channel]:', gre_stat)
        print('[Blue  channel]:', blu_stat)
        
        print()
      
    def reshape(self):
        reshaped_array = self.array_image_reduced.reshape(-1, 3)
        if reshaped_array.shape[0] > 5000:
            raise ValueError("There are more than 5000 pixels. Please further reduce the size in the previous step before continuing.")
        
        third_elements = reshaped_array[:, 2]
        third_sorted_indices = np.argsort(third_elements)
        reshaped_array = reshaped_array[third_sorted_indices]

        second_elements = reshaped_array[:, 1]
        second_sorted_indices = np.argsort(second_elements)
        reshaped_array = reshaped_array[second_sorted_indices]

        first_elements = reshaped_array[:, 0]
        first_sorted_indices = np.argsort(first_elements)
        self.reshaped_array = reshaped_array[first_sorted_indices]
        
        print('Reshaped:', self.reshaped_array.shape)
        print(self.reshaped_array)
        print()


    def pixelcount(self): #0.0545 seconds.
        # Convert the 2D array into a list of tuples (BGR values)
        color_tuples = [tuple(pixel) for pixel in self.reshaped_array]
        # Use Counter to count the occurrences of each color
        color_counts = Counter(color_tuples)
        df_color_counts = pd.DataFrame.from_dict(color_counts, orient='index', columns=['Count'])
        df_color_counts.index.name = 'Color'
        df_color_counts[['Blue', 'Green', 'Red']] = pd.DataFrame(df_color_counts.index.tolist(), index=df_color_counts.index)
        self.df_color_counts = df_color_counts.sort_values(by=['Count'], ascending=False)
        print('Dataframe size:', self.df_color_counts.shape)
        table_formate = 'orgtbl'
        print('Showing first 10 rows of the df_color_counts:')
        df_first_10_rows = self.df_color_counts.head(10)
        print(tabulate(df_first_10_rows, headers='keys', tablefmt=table_formate))
        return self.df_color_counts


    def plot_pixel_3D_heatmap(self):
        list_red = self.df_color_counts['Red'].tolist()
        list_green = self.df_color_counts['Green'].tolist()
        list_blue = self.df_color_counts['Blue'].tolist()
        list_count = self.df_color_counts['Count'].tolist()
    
        #[02-02] Set up the 3D plot
        fig = plt.figure(figsize=(16, 4))
        alpha_value = 0.1

        #[02-03] Plot the 3D scatter plot
        ax1 = fig.add_subplot(141, projection='3d')
        ax1.set_xlabel('list_red')
        ax1.set_ylabel('list_green')
        ax1.set_zlabel('list_blue')
        ax1.set_xlim(0, 255)
        ax1.set_ylim(0, 255)
        ax1.set_zlim(0, 255) 
        sc1 = ax1.scatter(list_red, list_green, list_blue, c = list_count, cmap='winter', alpha=alpha_value)
        # plt.colorbar(sc1, ax=ax1, label='list_count')

        #[02-04] Plot the 2D scatter plots
        ax2 = fig.add_subplot(142)
        ax2.set_xlabel('list_red')
        ax2.set_ylabel('list_green')
        ax2.set_xlim(0, 255)
        ax2.set_ylim(0, 255)
        sc2 = ax2.scatter(list_red, list_green, c = list_count, cmap='winter', alpha=alpha_value)
        plt.colorbar(sc2, ax=ax2, label='list_count')

        ax3 = fig.add_subplot(143)
        ax3.set_xlabel('list_green')
        ax3.set_ylabel('list_blue')
        ax3.set_xlim(0, 255)
        ax3.set_ylim(0, 255)
        sc3 = ax3.scatter(list_green, list_blue, c = list_count, cmap='winter', alpha=alpha_value)
        plt.colorbar(sc3, ax=ax3, label='list_count')

        ax4 = fig.add_subplot(144)
        ax4.set_xlabel('list_blue')
        ax4.set_ylabel('list_red')
        ax4.set_xlim(0, 255)
        ax4.set_ylim(0, 255)
        sc4 = ax4.scatter(list_blue, list_red, c = list_count, cmap='winter', alpha=alpha_value)
        plt.colorbar(sc4, ax=ax4, label='list_count')

        #[02-05] Show the plot
        plt.tight_layout()
        plt.show()
    
    def apply_criterion_generate_mask1(self, dir, image_basename):
        h, w, c = self.array_image_reduced.shape
        array_mask_image = np.zeros_like(self.array_image_reduced)
        cnt_within, cnt_outof = 0, 0
        for iter_h in range(h):
            for iter_w in  range(w):

                if (self.blu_lower < self.array_image_reduced[iter_h, iter_w][0] < self.blu_upper
                and self.gre_lower < self.array_image_reduced[iter_h, iter_w][1] < self.gre_upper
                ) and self.red_lower < self.array_image_reduced[iter_h, iter_w][2] < self.red_upper:
                    array_mask_image[iter_h, iter_w] = [200, 255, 200]
                    cnt_within += 1
                else:
                    #print('out!')
                    array_mask_image[iter_h, iter_w] = [10, 10, 100]
                    cnt_outof += 1
        with_in_ratio_pct = round(100 * cnt_within / (cnt_within + cnt_outof), 2)
        print('with_in_ratio_pct:', with_in_ratio_pct, '%')

        #[] Save image
        path_save_image = os.path.join(dir, image_basename)
        cv2.imwrite(path_save_image, array_mask_image)
        return array_mask_image
    

    def apply_criterion_generate_mask2(self, dir, image_basename):
        blu_mask = (self.array_image_reduced[:,:,0] > self.blu_lower) & (self.array_image_reduced[:,:,0] < self.blu_upper)
        gre_mask = (self.array_image_reduced[:,:,1] > self.gre_lower) & (self.array_image_reduced[:,:,1] < self.gre_upper)
        red_mask = (self.array_image_reduced[:,:,2] > self.red_lower) & (self.array_image_reduced[:,:,2] < self.red_upper)

        combined_mask = blu_mask & gre_mask & red_mask

        array_mask_image = np.where(combined_mask[..., None], [200, 255, 200], [10, 10, 100])
        
        cnt_within = np.sum(combined_mask)
        cnt_outof = combined_mask.size - cnt_within
        with_in_ratio_pct = round(100 * cnt_within / (cnt_within + cnt_outof), 2)
        print('with_in_ratio_pct:', with_in_ratio_pct, '%')

        # Save image
        path_save_image = os.path.join(dir, image_basename)
        cv2.imwrite(path_save_image, array_mask_image)
        return array_mask_image


    def generate_color_chart_image(self, dir, image_basename):
        h, w = 900, 900
        array_color_chart_image = np.zeros((h, w, 3))
        for iter_h in range(0, h//3):
            for iter_w in  range(0, w//3):
                array_color_chart_image[iter_h, iter_w] = [self.blu_upper, self.gre_upper, self.red_upper]
        for iter_h in range(0, h//3):
            for iter_w in  range(w//3, w*2//3):
                array_color_chart_image[iter_h, iter_w] = [self.blu_upper, self.gre_upper, self.red_lower]
        for iter_h in range(0, h//3):
            for iter_w in  range(w*2//3, w):
                array_color_chart_image[iter_h, iter_w] = [self.blu_upper, self.gre_lower, self.red_lower]
        for iter_h in range(h//3, h*2//3):
            for iter_w in  range(0, w//3):
                array_color_chart_image[iter_h, iter_w] = [self.blu_lower, self.gre_upper, self.red_upper]
        for iter_h in range(h*2//3, h):
            for iter_w in  range(0, w//3):
                array_color_chart_image[iter_h, iter_w] = [self.blu_lower, self.gre_lower, self.red_upper]
        for iter_h in range(h//3, h*2//3):
            for iter_w in  range(w*2//3, w):
                array_color_chart_image[iter_h, iter_w] = [self.blu_upper, self.gre_lower, self.red_upper]
        for iter_h in range(h*2//3, h):
            for iter_w in  range(w//3, w*2//3):
                array_color_chart_image[iter_h, iter_w] = [self.blu_lower, self.gre_upper, self.red_lower] 
        for iter_h in range(h*2//3, h):
            for iter_w in  range(w*2//3, w):
                array_color_chart_image[iter_h, iter_w] = [self.blu_lower, self.gre_lower, self.red_lower]       
        for iter_h in range(h//3, h*2//3):
            for iter_w in  range(w//3, w*2//3):
                array_color_chart_image[iter_h, iter_w] = [self.blu_mean_int, self.gre_mean_int, self.red_mean_int]  
            
            





    def generate_color_chart_image(self, dir, image_basename):
        h, w = 900, 900
        array_color_chart_image = np.zeros((h, w, 3))

        h_0_3, h_1_3, h_2_3, h_3_3 = 0, h//3, 2*h//3, h
        w_0_3, w_1_3, w_2_3, w_3_3 = 0, w//3, 2*w//3, w

        # Define color blocks
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

        # Assign colors to blocks
        for h_slice, w_slice, color in color_blocks:
            array_color_chart_image[h_slice, w_slice] = color

        # Save image
        path_save_image = os.path.join(dir, image_basename)
        cv2.imwrite(path_save_image, array_color_chart_image)
        return array_color_chart_image


#sys.exit()





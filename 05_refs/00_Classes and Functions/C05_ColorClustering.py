"""
[C05_ColorClustering.py]
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

from sklearn.mixture import GaussianMixture
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans

import numpy as np
import matplotlib.colors as mcolors


# This file is C05_ColorClustering.py
# Suppose necessary libraries has been imported.




def size_reduction(array_image, title=None, pixel_limit=None, default_ratio = 20, dir_save=None):
    #[1] Get the shape of the image
    h, w, c = array_image.shape 
    
    #[2] If pixel_limit is specified, calculate the necessary reduction ratio
    if pixel_limit:
        default_ratio = None # Not using default ratio if pixel limit is defined.
        current_pixels = w * h
        if current_pixels > pixel_limit:
            target_ratio = int((current_pixels / pixel_limit) ** 0.5) + 1
            text_limit_condition = f'Using pixel_limit of {pixel_limit} to reduce the original image with {current_pixels} pixels.'
        else:
            target_ratio = 1 
            text_limit_condition = f'Using the original image with size of {current_pixels} pixels.'
            return array_image
    else:
        target_ratio = default_ratio 
        text_limit_condition = f'Using the default conpression ratio of {default_ratio} to reduce the image.'
    
    #[3] Calculate new dimensions
    new_w = w // target_ratio
    new_h = h // target_ratio
    text_printed = f'\n[size_reduction] {title}\n'\
                    f'--{text_limit_condition}\n'\
                    f'--Old image dimensions (H, W, pixel): {h}, {w}, {h*w}\n'\
                    f'--New image dimensions (H, W, pixel): {new_h}, {new_w}\n'
    print(text_printed)
    #[4] Resize image
    arrimg_reduced = cv2.resize(array_image, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
    if dir_save:
        path_save_01_reduced = os.path.join(dir_save, f'01_{title}_reduced.jpg')
        cv2.imwrite(path_save_01_reduced, arrimg_reduced)
    return arrimg_reduced, text_printed



def reshape_3D_array_of_image_into_2D_array_of_values(arrimg_reduced):
    print('\n[reshape_3D_array_of_image_into_2D_array_of_values]')
    shape_hwc = arrimg_reduced.shape
    arr2D_pixel = arrimg_reduced.reshape(-1, 3)
    #mean_point = np.mean(arr2D_pixel, axis=0)
    #[2] Check size.
    if shape_hwc[0] > 100000:
        raise ValueError("There are more than 100k pixels. Please further reduce the size in the previous step before continuing.")
    print(f'--Shape of arrimg_reduced: {shape_hwc}')
    return arr2D_pixel
    


def plot_pixel_heatmap_one_3D_three_2D(arr2D, title, path_save=None):
    print('\n[plot_pixel_heatmap_one_3D_three_2D]')
    if title == 'BGR':
        x_title, y_title, z_title = 'Blue', 'Green', 'Red'
    elif title == 'HSV': 
        x_title, y_title, z_title = 'Hue', 'Saturation', 'Value' 
    list_red = arr2D[:, 0].tolist()
    list_green = arr2D[:, 1].tolist()
    list_blue = arr2D[:, 2].tolist()

    # [02-02] Set up the 3D plot
    fig = plt.figure(figsize=(16, 4))
    alpha_value = 0.5

    # [02-03] Plot the 3D scatter plot
    ax1 = fig.add_subplot(141, projection='3d')
    ax1.set_xlabel(x_title)
    ax1.set_ylabel(y_title)
    ax1.set_zlabel(z_title)
    ax1.set_xlim(0, 255)
    ax1.set_ylim(0, 255)
    ax1.set_zlim(0, 255)
    ax1.scatter(list_red, list_green, list_blue, c='k', alpha=alpha_value, s=3, edgecolors='none')

    # [02-04] Plot the 2D scatter plots
    ax2 = fig.add_subplot(142)
    ax2.set_xlabel(x_title)
    ax2.set_ylabel(y_title)
    ax2.set_xlim(0, 255)
    ax2.set_ylim(0, 255)
    ax2.scatter(list_red, list_green, c='k', alpha=alpha_value, s=3, edgecolors='none')

    ax3 = fig.add_subplot(143)
    ax3.set_xlabel(y_title)
    ax3.set_ylabel(z_title)
    ax3.set_xlim(0, 255)
    ax3.set_ylim(0, 255)
    ax3.scatter(list_green, list_blue, c='k', alpha=alpha_value, s=3, edgecolors='none')

    ax4 = fig.add_subplot(144)
    ax4.set_xlabel(z_title)
    ax4.set_ylabel(x_title)
    ax4.set_xlim(0, 255)
    ax4.set_ylim(0, 255)
    ax4.scatter(list_blue, list_red, c='k', alpha=alpha_value, s=3)

    # [02-05] Show or save the plot
    fig.suptitle('Pixel 3D Heatmap')
    plt.tight_layout()
    # [02-06] Save plot as png
    if path_save:
        plt.savefig(path_save)
        print(f'--Plot saved at {path_save}')
    else:
        plt.show()
    return fig, ax1



def plot_pixel_heatmap_two_3D_BGR_and_HSV(arr2D_BGR, arr2D_HSV, path_save=None):
    print('\n[plot_pixel_heatmap_one_3D_three_2D]')
    # [1] Convert arrays to lists
    list_blue = arr2D_BGR[:, 0].tolist()
    list_green = arr2D_BGR[:, 1].tolist()
    list_red = arr2D_BGR[:, 2].tolist()
    list_hue = arr2D_HSV[:, 0].tolist()
    list_sat = arr2D_HSV[:, 1].tolist()
    list_val = arr2D_HSV[:, 2].tolist()

    # [2] Set up the 3D plot
    fig = plt.figure(figsize=(8, 4))
    alpha_value = 0.4

    # [3] Plot the 3D scatter plot for BGR
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.set_xlabel('Blue')
    ax1.set_ylabel('Green')
    ax1.set_zlabel('Red')
    ax1.set_xlim(0, 255)
    ax1.set_ylim(0, 255)
    ax1.set_zlim(0, 255)
    colors_BGR = [(b/255, g/255, r/255) for b, g, r in zip(list_blue, list_green, list_red)]
    ax1.scatter(list_red, list_green, list_blue, c=colors_BGR, alpha=alpha_value, s=5, edgecolors='none')

    # [4] Plot the 2D scatter plots for HSV
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.set_xlabel('Hue')
    ax2.set_ylabel('Saturation')
    ax2.set_zlabel('Value')
    ax2.set_xlim(0, 180)
    ax2.set_ylim(0, 255)
    ax2.set_zlim(0, 255)
    #colors_HSV = [mcolors.hsv_to_rgb([h/255, s/255, v/255]) for h, s, v in zip(list_hue, list_sat, list_val)]
    colors_HSV = [mcolors.hsv_to_rgb([(h/180), s/255, v/255]) for h, s, v in zip(list_hue, list_sat, list_val)]

    ax2.scatter(list_hue, list_sat, list_val, c=colors_HSV, alpha=alpha_value, s=5, edgecolors='none')

    # [5] Show or save the plot
    fig.suptitle('Pixel 3D Heatmap')
    plt.tight_layout()
    # [6] Save plot as png
    if path_save:
        plt.savefig(path_save)
        print(f'--Plot saved at {path_save}')
    else:
        plt.show()
    return fig, ax1, ax2










class PixelStatistics:
    def __init__(self, path_image):
        print('\n[PixelStatistics]')
        self.path_image = path_image
        self.dir_image = os.path.dirname(path_image)
        self.image_basename = os.path.basename(self.path_image)
        print(f'--File Name: {self.image_basename}')
        
        #[1-1] Read image as array
        self.arrimg_BGR = cv2.imread(self.path_image)
        self.arrimg_HSV = cv2.cvtColor(self.arrimg_BGR, cv2.COLOR_BGR2HSV)

        #[1-2] Get image shape.
        h, w, c_bgr = self.arrimg_BGR.shape
        print(f'--Image Shape (H, W, C): {h, w, c_bgr}')
        print(f'--Number of pixel (H × W): {h*w}')
        #[1-3] Check if dire exist.
        self.dir_imagename = os.path.splitext(path_image)[0]
        try:
            os.mkdir(self.dir_imagename)
            print(f'--Directory was not exists. Just made one. {self.dir_imagename}')
        except FileExistsError:
            #print(f'--Directory already exists. Skipping directory creation. {self.dir_imagename}')
            print()
    



    def channel_statistics(self, arrimg_reduced, title=None,  limit_criterion = 1):
        """
        For BGR color space, the channel c1, c2, and c3 are blue, green, and red, respectively.
        For HSV color space, the channel c1, c2, and c3 are hue, satuation, and value(brightness), respectively.        
        """
        #limit_criterion = 2 # Choose 2 to enclose 95% of data, or 3 to enclose 99.7% of data.
        #[] Blue channel statistics
        c1 = arrimg_reduced[:,:,0] # Channel 1
        self.c1_mean_int = round(np.mean(c1))
        self.c1_std_int = round(np.std(c1))
        self.c1_upper = round(self.c1_mean_int + limit_criterion* self.c1_std_int)
        self.c1_lower = round(self.c1_mean_int - limit_criterion* self.c1_std_int)
        #[] Green channel statistics
        c2 = arrimg_reduced[:,:,1] # Channel 2
        self.c2_mean_int = round(np.mean(c2))
        self.c2_std_int = round(np.std(c2))
        self.c2_upper = round(self.c2_mean_int + limit_criterion* self.c2_std_int)
        self.c2_lower = round(self.c2_mean_int - limit_criterion* self.c2_std_int)
        #[] Red channel statistics
        c3 = arrimg_reduced[:,:,2] # Channel 3
        self.c3_mean_int = round(np.mean(c3))
        self.c3_std_int = round(np.std(c3))
        self.c3_upper = round(self.c3_mean_int + limit_criterion* self.c3_std_int)
        self.c3_lower = round(self.c3_mean_int - limit_criterion* self.c3_std_int)

        list_title = f'[{title}] max, min, mean, std, mean-{limit_criterion}std, mean+{limit_criterion}std'
        self.c1_stat = [np.max(c1), np.min(c1), self.c1_mean_int, self.c1_std_int, self.c1_lower, self.c1_upper]
        self.c2_stat = [np.max(c2), np.min(c2), self.c2_mean_int, self.c2_std_int, self.c2_lower, self.c2_upper]
        self.c3_stat = [np.max(c3), np.min(c3), self.c3_mean_int, self.c3_std_int, self.c3_lower, self.c3_upper]
        array_color_stat = np.array([self.c1_stat, self.c2_stat, self.c3_stat])
        text_printed = f'\n[channel_statistics] {title}\n'\
                        f'--{list_title}\n'\
                        f'--array_color_stat_RGB (limit_criterion ={limit_criterion})\n{array_color_stat}\n'
        print(text_printed)
        return array_color_stat, text_printed

    
    def run_size_reduction_and_channel_statistics_for_BGR_and_HSV(self
                                                                  , text_log
                                                                  , pixel_limit=None
                                                                  , default_ratio = 20
                                                                  , dir_save=None):
        #[1] Size reduction
        self.arrimg_BGR_reduced, text_BGR_1 = size_reduction(self.arrimg_BGR, 'BGR', pixel_limit, default_ratio, dir_save)
        self.arrimg_HSV_reduced, text_HSV_1 = size_reduction(self.arrimg_HSV, 'HSV', pixel_limit, default_ratio, dir_save)

        #[2] Color statistics
        array_BGR_stat, text_BGR_2 = self.channel_statistics(self.arrimg_BGR_reduced, 'BGR', limit_criterion = 1)
        array_HSV_stat, text_HSV_2 = self.channel_statistics(self.arrimg_HSV_reduced, 'HSV', limit_criterion = 1)
        text_log += f'{text_BGR_1}\n{text_HSV_1}\n\n{text_BGR_2}\n{text_HSV_2}'
        return self.arrimg_BGR_reduced, self.arrimg_HSV_reduced, text_log
    

      

        
        
        
        
        
        
        
        
        
        
        
    def cluster_RGB_color_array_GM(self, n_components=2, path_save=None):
        print('\n[cluster_RGB_color_array]')
        #[1] Clustering and print result.
        gmm = GaussianMixture(n_components, random_state=0)
        self.clusters = gmm.fit_predict(self.array_RGB_reduced_reshaped)
        #self.mean_of_clusters = gmm.means_
        #print('--[Cluster assignments]:\n', self.mean_of_clusters)
        #print('--[Means of each component]:\n', gmm.means_)
        #print('--[Covariances of each component]:\n', gmm.covariances_)
        
        #[2] Define colors
        self.mean_of_clusters = gmm.means_.astype(int)
        print('--[Means of each component]:\n', self.mean_of_clusters)
        
        #[3] Regenerate the image with corresponding mean color
        h, w, c = self.shape_hwc
        regenerated_image = np.zeros((h * w, c), dtype=np.uint8)
        for i, cluster in enumerate(self.clusters):
            regenerated_image[i] = self.mean_of_clusters[cluster]
            
        #[4] Reshape back to the 3D array and save as image
        self.arrimg_BGR_reduced_back = regenerated_image.reshape(h, w, c)[:, :, ::-1]  # Convert back to BGR
        if path_save is None:
            self.path_save_02_c = os.path.join(self.dir_imagename, '02-1_clustec3_GM.jpg')
        else:
            self.path_save_02_c = path_save
        cv2.imwrite(self.path_save_02_c, self.arrimg_BGR_reduced_back)
        
        #[5] H-stack image and save
        path_save = os.path.join(self.dir_imagename, '02-2_hconcat_GM.jpg')
        hstack_before_and_after_clustering_old(self.arrimg_BGR_reduced, self.arrimg_BGR_reduced_back, path_save)
        
        return self.mean_of_clusters
            


    
    def cluster_RGB_color_array_DBSCAN(self, eps=5, min_samples=10, path_save=None):
        print('\n[cluster_RGB_color_array_DBSCAN]')
        #[1] Clustering and print result.
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        self.clusters = dbscan.fit_predict(self.array_RGB_reduced_reshaped)
        
        #[2] Define colors
        unique_clusters = np.unique(self.clusters)
        self.mean_of_clusters = np.zeros((len(unique_clusters), 3), dtype=int)
        for i, cluster in enumerate(unique_clusters):
            if cluster != -1:  # Skip the noise points
                cluster_points = self.array_RGB_reduced_reshaped[self.clusters == cluster]
                self.mean_of_clusters[i] = np.mean(cluster_points, axis=0).astype(int)
        print('--[Means of each cluster]:\n', self.mean_of_clusters)
        
        #[3] Regenerate the image with corresponding mean color
        h, w, c = self.shape_hwc
        regenerated_image = np.zeros((h * w, c), dtype=np.uint8)
        for i, cluster in enumerate(self.clusters):
            if cluster != -1:  # Skip the noise points
                regenerated_image[i] = self.mean_of_clusters[np.where(unique_clusters == cluster)[0][0]]
            else:
                regenerated_image[i] = [0, 0, 0]  # Assign black color to noise points
            
        #[4] Reshape back to the 3D array and save as image
        self.arrimg_BGR_reduced_back = regenerated_image.reshape(h, w, c)[:, :, ::-1]  # Convert back to BGR
        if path_save is None:
            self.path_save_02_c = os.path.join(self.dir_imagename, '03-1_clustec3_DBSCAN.jpg')
        else:
            self.path_save_02_c = path_save
        cv2.imwrite(self.path_save_02_c, self.arrimg_BGR_reduced_back)
        
        #[5] H-stack image and save
        path_save = os.path.join(self.dir_imagename, '03-2_hconcat_DBSCAN.jpg')
        hstack_before_and_after_clustering_old(self.arrimg_BGR_reduced, self.arrimg_BGR_reduced_back, path_save)
        
        return self.mean_of_clusters
    

    def cluster_RGB_color_array_Kmean(self, n_clusters=2, path_save=None):
        print('\n[cluster_RGB_color_array_Kmean]')
        #[1] Clustering and print result.
        kmeans = KMeans(n_clusters=n_clusters, random_state=0)
        self.clusters = kmeans.fit_predict(self.array_RGB_reduced_reshaped)
        
        #[2] Define colors
        self.mean_of_clusters = kmeans.cluster_centers_.astype(int)
        print('--[Means of each cluster]:\n', self.mean_of_clusters)
        
        #[3] Regenerate the image with corresponding mean color
        h, w, c = self.shape_hwc
        regenerated_image = np.zeros((h * w, c), dtype=np.uint8)
        for i, cluster in enumerate(self.clusters):
            regenerated_image[i] = self.mean_of_clusters[cluster]
            
        #[4] Reshape back to the 3D array and save as image
        self.arrimg_BGR_reduced_back = regenerated_image.reshape(h, w, c)[:, :, ::-1]  # Convert back to BGR
        if path_save is None:
            self.path_save_02_c = os.path.join(self.dir_imagename, '04-1_clustec3_Kmean.jpg')
        else:
            self.path_save_02_c = path_save
        cv2.imwrite(self.path_save_02_c, self.arrimg_BGR_reduced_back)
        
        #[5] H-stack image and save
        path_save = os.path.join(self.dir_imagename, '04-2_hconcat_Kmean.jpg')
        hstack_before_and_after_clustering_old(self.arrimg_BGR_reduced, self.arrimg_BGR_reduced_back, path_save)
        
        return self.mean_of_clusters


    def pixel_count_return_df(self):
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






    def generate_mask_with_color_statistics(self, array_color_stat_RGB, path_image, replace_old_dis, with_new_dis):
        print('\n[generate_mask_with_color_statistics]')
        dir = os.path.dirname(path_image)
        array_image = cv2.imread(path_image)
        if array_color_stat_RGB.shape != (3, 6):
            raise ValueError("The shape of array_color_stat doesn't seems to be correct.")   
        
        c3_lower, c3_upper = array_color_stat_RGB[0][4], array_color_stat_RGB[0][5]
        c2_lower, c2_upper = array_color_stat_RGB[1][4], array_color_stat_RGB[1][5]
        c1_lower, c1_upper = array_color_stat_RGB[2][4], array_color_stat_RGB[2][5]
        #print(c3_lower, c3_upper, c2_lower, c2_upper, c1_lower, c1_upper)
        
        c3_mask = (array_image[:,:,2] > c3_lower) & (array_image[:,:,2] < c3_upper)
        c2_mask = (array_image[:,:,1] > c2_lower) & (array_image[:,:,1] < c2_upper)
        c1_mask = (array_image[:,:,0] > c1_lower) & (array_image[:,:,0] < c1_upper)

        combined_mask = c1_mask & c2_mask & c3_mask

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
        arrimg_BGR = cv2.imread(path_image)
        arrimg_RGB = cv2.cvtColor(arrimg_BGR, cv2.COLOR_BGR2RGB)
        h, w, c = arrimg_RGB.shape
        array_mask_image = np.full((h, w, 3), 10)
        cnt_within = 0
        for iter_h in range(0, h):
            for iter_w in  range(0, w):
                test_point = arrimg_RGB[iter_h][iter_w]
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
        RGB_max_std_xn = 3*round(max(self.c3_stat[4], self.c2_stat[4], self.c1_stat[4]), 0)
        #X_limit = self.c3_mean_int - RGB_max_std_xn, self.c3_mean_int + RGB_max_std_xn
        #Y_limit = self.c2_mean_int - RGB_max_std_xn, self.c2_mean_int + RGB_max_std_xn
        #Z_limit = self.c1_mean_int - RGB_max_std_xn, self.c1_mean_int + RGB_max_std_xn
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
        

#[] Here are the functions that are used in the class but not written in the class.

def hstack_before_and_after_clustering_old(img1, img2, path_save):
    # Images must be in 3D array with BGR channel sequence.
    #[1] Load the images.
    #[2] Check size.
    if img1.shape[0] != img2.shape[0]:
        ratio = img1.shape[0] / img2.shape[0]
        print(f'Two images are in different size, need to resize. H_img1/H_img2 = {ratio}')
        img2 = cv2.resize(img2, (int(img2.shape[1] * ratio), img1.shape[0]))
    #[3] Horizontally stack the images
    hstacked_img = cv2.hconcat([img1, img2])
    # Save the result
    cv2.imwrite(path_save, hstacked_img)
    return hstacked_img


def distance_to_line(point, line_point, line_vector):
    """
    This function will be execute many times. Do not print.
    *test_point is the input point to test.
    *line_point is a point on the line.
    *line_vector is directional vector of the line.
    """
    point, line_point, line_vector = np.array(point), np.array(line_point), np.array(line_vector)
    mean_to_point_vector = np.array(point - line_point)
    cross_product = np.cross(mean_to_point_vector, line_vector)
    distance = round(np.linalg.norm(cross_product) / np.linalg.norm(line_vector), 4)
    return distance



def stretch_point_from_a_line(point, ratio, line_point, line_vector):
    """
    point = [122.47, 122.47, 0]                 # List
    point = np.array([122.47, 122.47, 0])       # Array
    point = (122.47, 122.47, 0)                 # Tuple
    """
    #[1] Calculate original distance
    point, line_point, line_vector = np.array(point), np.array(line_point), np.array(line_vector)
    distance = distance_to_line(point, line_point, line_vector)
    
    #[2] Find the projection of point onto the line to find the closest point on the line
    point_to_line_vector = point - line_point
    line_unit_vector = line_vector / np.linalg.norm(line_vector)
    projection_length = np.dot(point_to_line_vector, line_unit_vector)
    closest_point_on_line = line_point + projection_length * line_unit_vector
    
    #[3] Calculate the direction vector from the closest point on the line to the original point
    direction_vector = point - closest_point_on_line
    direction_unit_vector = direction_vector / np.linalg.norm(direction_vector)
    
    #[4] Calculate the new stretched distance
    stretched_distance = distance * ratio
    
    #[5] Calculate the new point's position
    stretched_point = closest_point_on_line + stretched_distance * direction_unit_vector
    return stretched_point


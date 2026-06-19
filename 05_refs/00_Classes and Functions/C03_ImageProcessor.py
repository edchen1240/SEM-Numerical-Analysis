"""
[C02_xyzLS.py]
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
import pandas as pd
import torch
import torch.nn as nn
import tensorflow as tf
from PIL import Image
import numpy as np

class ImageProcessor:
    def __init__(self, path_image):
        self.path_image = path_image
        self.dir_image = os.path.dirname(path_image)
        self.image_basename = None
        self.max_std = None

    def image_color_channel_extract(self, compress, channel): 
        # See PCCS-1_(extract RGB channel, avg, std).py if you need to save to excel
        self.image_basename = os.path.basename(self.path_image)
        array_image = cv2.imread(self.path_image)
        h, w, c = array_image.shape
        print('[image_color_channel_extract] shape (H, W, C):', h, w, c)
        
        # Resize the image
        compressed_width = w // compress
        compressed_height = h // compress
        array_image_reduced = cv2.resize(array_image, (compressed_width, compressed_height), interpolation=cv2.INTER_NEAREST)
        
        if channel == 'B':
            return_channel = array_image_reduced[:,:,0] # Blue
        elif channel == 'G':
            return_channel = array_image_reduced[:,:,1] # Green
        elif channel == 'R':
            return_channel = array_image_reduced[:,:,2] # Red
        else:
            raise 'Color channel not defined.'
        return return_channel


            
    
    def single_channel_average(self, single_color_channel, k, s):
        kernel = torch.ones((1, 1, k, k)) / (k * k)
        print('Kernel:', kernel.shape, type(kernel))
        single_color_channel = torch.tensor(single_color_channel).unsqueeze(0).unsqueeze(1).float()
        print('color_channel:', single_color_channel.shape)
        conv = nn.Conv2d(in_channels=1, out_channels=1, kernel_size=k, stride=s, bias=False)
        conv.weight = nn.Parameter(kernel)
        averaged_channel = conv(single_color_channel)
        #[] Convert the tensor (averaged_channel) to numpy array, and squeeze to remove any singleton dimensions.
        numpy_img = averaged_channel.detach().numpy().squeeze()
        print('averaged_channel:', numpy_img.shape, end='\n\n')
        #[] Normalize the values between 0 and 255, and convert to uint8
        numpy_img = (numpy_img - np.min(numpy_img)) / (np.max(numpy_img) - np.min(numpy_img)) * 255
        numpy_img = numpy_img.astype(np.uint8)
        return numpy_img

    def single_channel_std(self, single_color_channel, k, s):
        single_color_channel = torch.tensor(single_color_channel).unsqueeze(0).unsqueeze(3).float()
        print('color_channel:', single_color_channel.shape, type(single_color_channel))
        
        patches  = tf.image.extract_patches(images=single_color_channel,
                                            sizes=[1, k, k, 1], # kernal: The size of the extracted patches.
                                            strides=[1, s, s, 1], # strides:  How far the centers of two consecutive patches are in the images.
                                            rates=[1, 1, 1, 1],
                                            padding='VALID')  
        
        numpy_img = tf.math.reduce_std(patches, axis=-1)
        numpy_img = numpy_img.numpy().squeeze()
        print('std_channel:', numpy_img.shape, type(numpy_img))
    
        self.max_std = np.max(numpy_img)
        print('max_std: ', self.max_std, end='\n\n')
        #[] Normalization (when standard deviation is small, the image is too dark to see.)
        normalization_constant = 127.5 #The maximum possible STD for n numbers range from 0-255 is 127.5.
        numpy_img = (numpy_img * 255/normalization_constant).astype(np.uint8)
        return numpy_img
    
    
    """
    cv2.imread(image_path): NumPy array in BGR format
    image.open(image_path): Pillow library in RGB format.
    """


    def save_PIL_image(self, img_by_imageopen, dir_save_image=None, replace_old_dis=None, with_new_dis=None):
        img_by_imageopen = Image.fromarray(img_by_imageopen)
        basename = self.image_basename.replace(replace_old_dis, with_new_dis)
        if dir_save_image is None:
            dir_save_image = self.dir_image
        path_save_image = os.path.join(dir_save_image, basename)
        img_by_imageopen.save(path_save_image)
        return path_save_image



    def save_cv2_image(self, img_by_cv2imread, dir_save_image=None, replace_old_dis=None, with_new_dis=None):
        basename = self.image_basename.replace(replace_old_dis, with_new_dis)
        if dir_save_image is None:
            dir_save_image = self.dir_image
        path_save_image = os.path.join(dir_save_image, basename)
        cv2.imwrite(path_save_image, img_by_cv2imread)
        return path_save_image
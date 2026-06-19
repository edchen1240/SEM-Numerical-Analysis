"""
[BLK-0_sandbox.py]
Purpose: 
Author: Meng-Chi Ed Chen
Date: 
Reference:
    1.
    2.

Status: Working.
"""
import os, sys, cv2, torch
import numpy as np
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt


import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np

class ImageWatershedAdjuster:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Watershed Adjuster")
        self.root.geometry("1000x1000")

        # Set dark mode background and text colors
        self.root.configure(bg="#2e2e2e")  # Dark gray background

        # Load Image Button with dark mode
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image, bg="#4e4e4e", fg="white")
        self.load_button.pack(pady=10)

        self.image_label = tk.Label(root, bg="#2e2e2e")
        self.image_label.pack()

        #[3] Create frames for two columns of scale bars
        main_frame = tk.Frame(root, bg="#2e2e2e")
        main_frame.pack()

        left_frame = tk.Frame(main_frame, bg="#2e2e2e")
        left_frame.grid(row=0, column=0, padx=20, pady=10)

        right_frame = tk.Frame(main_frame, bg="#2e2e2e")
        right_frame.grid(row=0, column=1, padx=20, pady=10)

        #[7] Create scale bars on left and right frames
        self.frgd_thrs_ratio_scale = self.create_scale(left_frame, "frgd_thrs_ratio", 0.0, 1.0, 0.01, 0.6)
        self.frgd_GB_k_scale = self.create_scale(left_frame, "frgd_GB_k", 1, 97, 2, 27)
        self.bkgd_GB_k_scale = self.create_scale(right_frame, "bkgd_GB_k", 1, 97, 2, 27)
        self.dilate_iteration_scale = self.create_scale(right_frame, "dilate_iteration", 1, 50, 1, 3)
        self.morph_kernel_size_scale = self.create_scale(right_frame, "morph_kernel_size", 1, 97, 1, 3)

        #[10] Radio buttons for dist_transform_mask_size
        self.dist_transform_mask_size = tk.IntVar(value=3)
        tk.Label(left_frame, text="dist_transform_mask_size:", bg="#2e2e2e", fg="white").pack()
        for value in [0, 3, 5]:
            tk.Radiobutton(left_frame, text=str(value), variable=self.dist_transform_mask_size, value=value, bg="#2e2e2e", fg="white").pack()

        #[15] Invert checkbox
        self.invert_var = tk.BooleanVar(value=True)
        tk.Checkbutton(right_frame, text="Invert", variable=self.invert_var, bg="#2e2e2e", fg="white").pack()

        # Apply Watershed Button with dark mode
        self.apply_button = tk.Button(root, text="Apply Watershed", command=self.apply_watershed, bg="#4e4e4e", fg="white")
        self.apply_button.pack(pady=10)

        self.original_image = None
        self.binarized_image = None
        self.tk_image = None

    def create_scale(self, parent, label, from_, to_, resolution, default):
        scale = tk.Scale(parent, from_=from_, to=to_, resolution=resolution, orient=tk.HORIZONTAL, label=label)
        scale.set(default)
        scale.pack(padx=10, pady=5)
        return scale

    def load_image(self):
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if image_path:
            self.original_image = cv2.imread(image_path)
            self.binarize_image()
            self.show_image(self.binarized_image)

    def binarize_image(self):
        if self.original_image is not None:
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            _, self.binarized_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if self.invert_var.get():
                self.binarized_image = cv2.bitwise_not(self.binarized_image)

    @staticmethod
    def quick_binary_smoothing(arrimg_inpt, ksize=5):
        arrimg_inpt_blur = cv2.GaussianBlur(arrimg_inpt, (ksize, ksize), 0)
        
        if arrimg_inpt_blur.dtype != 'uint8':
            arrimg_inpt_blur = cv2.normalize(arrimg_inpt_blur, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
        
        otsu_threshold, arrimg_oupt = cv2.threshold(arrimg_inpt_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        print(f'\n[quick_binary_smoothing] otsu_threshold: {otsu_threshold}')
        return arrimg_oupt

    def apply_watershed(self):
        if self.binarized_image is not None:
            #[1] Get parameter values from UI controls
            frgd_thrs_ratio = self.frgd_thrs_ratio_scale.get()
            frgd_GB_k = self.frgd_GB_k_scale.get()
            bkgd_GB_k = self.bkgd_GB_k_scale.get()
            morph_kernel_size = self.morph_kernel_size_scale.get()
            dilate_iteration = self.dilate_iteration_scale.get()
            dist_transform_mask_size = self.dist_transform_mask_size.get()

            #[2] Perform morphological operations
            kernel = np.ones((morph_kernel_size, morph_kernel_size), np.uint8)
            arrimg_open = cv2.morphologyEx(self.binarized_image, cv2.MORPH_OPEN, kernel, iterations=2)
            arrimg_open = np.uint8(arrimg_open)
            arrimg_bkgd = cv2.dilate(arrimg_open, kernel, iterations=dilate_iteration)

            #[3] Compute distance transform and find foreground
            dist_transform = cv2.distanceTransform(arrimg_open, cv2.DIST_L2, dist_transform_mask_size)
            _, arrimg_frgd = cv2.threshold(dist_transform, frgd_thrs_ratio * dist_transform.max(), 255, 0)
            arrimg_frgd = self.quick_binary_smoothing(arrimg_frgd, frgd_GB_k)
            arrimg_bkgd = self.quick_binary_smoothing(arrimg_bkgd, bkgd_GB_k)
            arrimg_frgd = np.uint8(arrimg_frgd)
            arrimg_bkgd = np.uint8(arrimg_bkgd)

            #[4] Find unknown region
            unknown = cv2.subtract(arrimg_bkgd, arrimg_frgd)

            #[5] Create overlap image for visualization
            arrimg_inpt_gray = np.where(self.binarized_image == 255, 160, self.binarized_image)
            arrimg_open_gray = np.where(arrimg_open == 255, 80, arrimg_open)
            arrimg_bkgd_gray = np.where(arrimg_bkgd == 255, 80, arrimg_bkgd)
            arrimg_frgd_gray = np.where(arrimg_frgd == 255, 80, arrimg_frgd)
            arrimg_ovlp = arrimg_inpt_gray - arrimg_open_gray + arrimg_bkgd_gray + arrimg_frgd_gray

            #[6] Apply watershed algorithm
            _, markers = cv2.connectedComponents(arrimg_frgd)
            markers = markers + 1
            markers[unknown == 255] = 0
            markers = cv2.watershed(cv2.cvtColor(arrimg_ovlp, cv2.COLOR_GRAY2BGR), markers)

            #[7] Mark watershed boundaries in red
            arrimg_ovlp = cv2.cvtColor(arrimg_ovlp, cv2.COLOR_GRAY2BGR)
            arrimg_ovlp[markers == -1] = [0, 0, 255]

            #[8] Display the result
            self.show_image(arrimg_ovlp)
        

    def show_image(self, img, max_length=720):
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        pil_img = Image.fromarray(img)
        
        w, h = pil_img.size
        if max(h, w) == h:
            scale_factor = max_length / h
        else:
            scale_factor = max_length / w

        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        
        img_resized = pil_img.resize((new_w, new_h), Image.LANCZOS)
        
        self.tk_image = ImageTk.PhotoImage(img_resized)
        self.image_label.config(image=self.tk_image)
        self.image_label.image = self.tk_image 

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageWatershedAdjuster(root)
    root.mainloop()



















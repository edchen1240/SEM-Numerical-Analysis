"""
[F10_CA.py]
Purpose: Color Analysis
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import os, sys, cv2, datetime, serial, time
import numpy as np


#[] For plot
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
import matplotlib.colors as colors







def plot_four_3D(list_vectors, list_color, color_scale_name, title, path_save_plot):
    # Normalization and calculation
    norm = colors.Normalize(min(list_color), max(list_color))
    cmap = cm.winter
    colors_array = cmap(norm(list_color))
    max_abs_element = max([max(map(abs, vec)) for vec in list_vectors])

    # Create a 2x2 subplot grid
    fig, axs = plt.subplots(2, 2, subplot_kw={'projection': '3d'}, figsize=(12, 8))

    # Axis limit factors
    limit_factors = [1, 0.8, 0.5, 0.1]

    for i, ax in enumerate(axs.flat):
        # Set axis limits
        limit = max_abs_element * limit_factors[i]
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)

        # Plot vectors
        for vec, color in zip(list_vectors, colors_array):
            ax.quiver(0, 0, 0, vec[0], vec[1], vec[2], color=color, arrow_length_ratio=0.2, linewidth=3)

        # Set labels
        ax.set_xlabel('Blue')
        ax.set_ylabel('Green')
        ax.set_zlabel('Red')

        # Set individual titles
        ax.set_title(f'Axes Limit: {limit_factors[i]} * max_abs_element', color='gray', fontsize=10, pad=-15)

    # Adjust the main title
    fig.suptitle(title, fontsize=16, y=0.95)

    # Create a mappable object for the colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Add colorbar in the lower right corner
    cbar_ax = fig.add_axes([0.92, 0.15, 0.01, 0.7])  # x, y, width, height
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='vertical')
    cbar.set_label(color_scale_name)

    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, bottom=0.1, hspace=0.2)  # Adjust top spacing to accommodate main title

    # Show plot
    plt.show()
    
    # Save plot
    fig.savefig(path_save_plot, dpi=300)  # Save the figure
    print(f"Plot saved as '{path_save_plot}'")
    return




import matplotlib.pyplot as plt
from matplotlib import colors, cm

def plot_one_3D_three_2D(list_vectors, list_color, color_scale_name, title, path_save_plot):
    # Normalization and calculation
    norm = colors.Normalize(min(list_color), max(list_color))
    cmap = cm.winter
    colors_array = cmap(norm(list_color))
    max_abs_element = max([max(map(abs, vec)) for vec in list_vectors])

    # Create a 2x2 subplot grid
    fig = plt.figure(figsize=(12, 8))
    
    # Axis limit factor
    limit_factor = 1
    limit = max_abs_element * limit_factor

    #[1] 3D plot with BGR as XYZ
    ax_3d = fig.add_subplot(2, 2, 1, projection='3d')
    ax_3d.set_xlim(-limit, limit)
    ax_3d.set_ylim(-limit, limit)
    ax_3d.set_zlim(-limit, limit)
    for vec, color in zip(list_vectors, colors_array):
        ax_3d.quiver(0, 0, 0, vec[0], vec[1], vec[2], color=color, arrow_length_ratio=0.2, linewidth=3)
    ax_3d.set_xlabel('Blue')
    ax_3d.set_ylabel('Green')
    ax_3d.set_zlabel('Red')
    ax_3d.set_title('3D plot: BGR as XYZ')

    #[2] 2D plot with BG as XY
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.set_xlim(-limit, limit)
    ax2.set_ylim(-limit, limit)
    ax2.set_aspect('equal', adjustable='box')
    for vec, color in zip(list_vectors, colors_array):
        ax2.quiver(0, 0, vec[1], vec[0], color=color, angles='xy', scale_units='xy', scale=1)
    ax2.set_xlabel('Green')
    ax2.set_ylabel('Blue')
    ax2.set_title('2D plot: GB as XY (view from bottom)')

    #[3] 2D plot with BR as XY
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.set_xlim(-limit, limit)
    ax3.set_ylim(-limit, limit)
    ax3.set_aspect('equal', adjustable='box')
    for vec, color in zip(list_vectors, colors_array):
        ax3.quiver(0, 0, vec[0], vec[2], color=color, angles='xy', scale_units='xy', scale=1)
    ax3.set_xlabel('Blue')
    ax3.set_ylabel('Red')
    ax3.set_title('2D plot: BR as XY (view from left)')
    
    
    #[34] 2D plot with GR as XY
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.set_xlim(-limit, limit)
    ax4.set_ylim(-limit, limit)
    ax4.set_aspect('equal', adjustable='box')
    for vec, color in zip(list_vectors, colors_array):
        ax4.quiver(0, 0, vec[1], vec[2], color=color, angles='xy', scale_units='xy', scale=1)
    ax4.set_xlabel('Green')
    ax4.set_ylabel('Red')
    ax4.set_title('2D plot: GR as XY (view from right)')
    
    

    # Adjust the main title and layout
    fig.suptitle(title, fontsize=16, y=0.95)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, bottom=0.1, hspace=0.3, wspace=-0.1)

    # Create a mappable object for the colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes([0.92, 0.15, 0.01, 0.7])  # x, y, width, height
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='vertical')
    cbar.set_label(color_scale_name)

    # Show plot
    plt.show()

    # Save plot
    fig.savefig(path_save_plot, dpi=300)  # Save the figure
    print(f"Plot saved as '{path_save_plot}'")
    return



def plot_one_3DandPlane_two_2D(list_X, list_Y, list_Z, params_aXbYc, labels_XYZ, title, path_save_plot):
    print('\n[plot_one_3DandPlane_two_2D]')
    a, b, c = params_aXbYc
    label_X, label_Y, label_Z = labels_XYZ

    # Create a 1x3 subplot grid
    fig = plt.figure(figsize=(15, 6))
    
    #[0-2] Calculate plot limits.
    cvl_limit = 0, (round(max(list_Z)/10)+1)*10
    

    #[1-1] 3D plot XYZ
    ax1_3d = fig.add_subplot(1, 3, 1, projection='3d')
    ax1_3d.scatter(list_X, list_Y, list_Z, c='r', marker='o')
    #[1-2] Create a grid to plot the predicted plane
    grid_X, grid_Y = np.meshgrid(np.linspace(min(list_X), max(list_X), 50), np.linspace(min(list_Y), max(list_Y), 50))
    #[1-3] Calculate corresponding Z values on the grid using the predicted coefficients and intercept
    grid_Z = a * grid_X + b * grid_Y + c
    
    # [1-4] Plot the predicted plane with varying alpha
    # Split the surface plot based on the condition
    for i in range(len(grid_X)-1):
        for j in range(len(grid_Y)-1):
            x = grid_X[i:i+2, j:j+2]
            y = grid_Y[i:i+2, j:j+2]
            z = grid_Z[i:i+2, j:j+2]
            alpha = 0.6 if np.any(z > 0) else 0.1  # Adjust alpha based on condition
            ax1_3d.plot_surface(x, y, z, color='b', alpha=alpha)
    
    
    #[1-5] Set labels
    ax1_3d.set_xlabel(label_X)
    ax1_3d.set_ylabel(label_Y)
    ax1_3d.set_zlabel(label_Z)
    ax1_3d.tick_params(axis='both', which='major', labelsize=9)
    #[1-6] Set limits
    ax1_3d.set_zlim(cvl_limit)
    
    

    #[2-1] 2D plot XZ
    ax2_2d = fig.add_subplot(1, 3, 2)
    ax2_2d.scatter(list_X, list_Z, c='r', marker='o')
    X_unique = np.linspace(min(list_X), max(list_X), 50)
    Z_line = a * X_unique + b * np.mean(list_Y) + c  # 2D line on Z_axis
    ax2_2d.plot(X_unique, Z_line, color='b', alpha=0.5)
    ax2_2d.set_xlabel(label_X)
    ax2_2d.set_ylabel(label_Z)
    
    #[2-2] 2D plot set limit
    #ax2_2d.set_xlim(0, )
    ax2_2d.set_ylim(cvl_limit)
    

    #[3-1] 2D plot YZ
    ax3_2d = fig.add_subplot(1, 3, 3)
    ax3_2d.scatter(list_Y, list_Z, c='r', marker='o')
    Y_unique = np.linspace(min(list_Y), max(list_Y), 50)
    Z_line = a * np.mean(list_X) + b * Y_unique + c  # 2D line on Z_axis
    ax3_2d.plot(Y_unique, Z_line, color='b', alpha=0.5)
    ax3_2d.set_xlabel(label_Y)
    ax3_2d.set_ylabel(label_Z)
    
    #[3-2] 2D plot set limit
    ax3_2d.set_ylim(cvl_limit)


    # Adjust layout and show/save plot
    fig.suptitle(title, fontsize=16, y=0.95)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, bottom=0.2, hspace=0.3, wspace=0.3)
    
    # Add text labels relative to the figure
    #[] Formate equation text
    a = round(a,2)
    b = round(b,2)
    c = round(c,2)
    text_eq = f'(d) Correlation equation\n\
                                        {label_Z} =  {a:+} × {label_X}   {b:+} × {label_Y}   {c:+}'
    text_eq = text_eq.replace('-','−')
    fontname = 'Arial'
    ver_align = 'top'
    fig.text(0.01, 0.87, '(a)', fontsize=14, fontname=fontname, verticalalignment=ver_align)
    fig.text(0.32, 0.87, '(b)', fontsize=14, fontname=fontname, verticalalignment=ver_align)
    fig.text(0.675, 0.87, '(c)', fontsize=14, fontname=fontname, verticalalignment=ver_align)
    fig.text(0.01, 0.1, text_eq, fontsize=14, fontname=fontname, verticalalignment=ver_align)

    plt.show()
    path_save_plot = generate_new_filename(path_save_plot)
    fig.savefig(path_save_plot, dpi=300)
    print(f"Plot saved as '{path_save_plot}'")
    
    

def generate_new_filename(original_path):
    if os.path.exists(original_path):
        base, extension = os.path.splitext(original_path)
        i = 1
        original_path = f"{base}_{i}{extension}"
        while os.path.exists(original_path):
            i += 1
            original_path = f"{base}_{i}{extension}"
    return original_path
    



# No longer need to update this function.

"""def plot_one_3DandPlane_two_2D_XY_change(list_X, list_Y, list_Z, params_aXbYc, labels_XYZ, title, path_save_plot):
    a, b, c = params_aXbYc
    label_X, label_Y, label_Z = labels_XYZ

    # Create a 1x3 subplot grid
    fig = plt.figure(figsize=(15, 5))

    # [1-1] 3D plot XYZ
    ax1_3d = fig.add_subplot(1, 3, 1, projection='3d')
    ax1_3d.scatter(list_X, list_Y, list_Z, c='r', marker='o')
    # [1-2] Create a grid to plot the predicted plane
    grid_X, grid_Y = np.meshgrid(np.linspace(min(list_X), max(list_X), 50), np.linspace(min(list_Y), max(list_Y), 50))
    # [1-3] Calculate corresponding Z values on the grid using the predicted coefficients and intercept
    grid_Z = a * grid_X + b * grid_Y + c
    # [1-4] Plot the predicted plane
    ax1_3d.plot_surface(grid_X, grid_Y, grid_Z, color='b', alpha=0.5)
    # [1-5] Set labels
    ax1_3d.set_xlabel(label_X)
    ax1_3d.set_ylabel(label_Y)
    ax1_3d.set_zlabel(label_Z)
    ax1_3d.tick_params(axis='both', which='major', labelsize=9)

    # [2] 2D plot XZ
    ax2_2d = fig.add_subplot(1, 3, 2)
    ax2_2d.scatter(list_Z, list_X, c='r', marker='o') #[XZ_change]
    X_unique = np.linspace(min(list_X), max(list_X), 50)
    Z_line = a * X_unique + b * np.mean(list_Y) + c  # 2D line on Z_axis
    ax2_2d.plot(Z_line, X_unique, color='b', alpha=0.5) #[XZ_change]
    ax2_2d.set_xlabel(label_Z) #[XZ_change]
    ax2_2d.set_ylabel(label_X) #[XZ_change]

    # [3] 2D plot YZ
    ax3_2d = fig.add_subplot(1, 3, 3)
    ax3_2d.scatter(list_Z, list_Y, c='r', marker='o') #[YZ_change]
    Y_unique = np.linspace(min(list_Y), max(list_Y), 50)
    Z_line = a * np.mean(list_X) + b * Y_unique + c  # 2D line on Z_axis
    ax3_2d.plot(Z_line, Y_unique, color='b', alpha=0.5) #[YZ_change]
    ax3_2d.set_xlabel(label_Z) #[YZ_change]
    ax3_2d.set_ylabel(label_Y) #[YZ_change]

    # Adjust layout and show/save plot
    fig.suptitle(title, fontsize=16, y=0.95)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, bottom=0.1, hspace=0.3, wspace=0.3)
    
    # Add text labels relative to the figure
    fontname = 'Arial'
    ver_align = 'top'
    fig.text(0.01, 0.87, '(a)', fontsize=14, fontname=fontname, verticalalignment=ver_align)
    fig.text(0.32, 0.87, '(b)', fontsize=14, fontname=fontname, verticalalignment=ver_align)
    fig.text(0.675, 0.87, '(c)', fontsize=14, fontname=fontname, verticalalignment=ver_align)

    plt.show()
    fig.savefig(path_save_plot, dpi=300)
    print(f"Plot saved as '{path_save_plot}'")
"""
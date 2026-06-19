"""
[F19_GIF]
Purpose: Generate random datasets
Author: Meng-Chi Ed Chen
Date: 2024-04-03
Reference:
    1.
    2.

Status: Complete.
"""
import os, sys, cv2
import numpy as np
from PIL import Image
import imageio.v2 as imageio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# [Generate Dataset] Start



# [Generate Dataset] End




# [Visualize Dataset] Start


# [Visualize Dataset] End











# [Visualize Kernel] Start



def list_paths_of_images_into_GIF(list_paths, fps=10, path_save=None,
                                   bounce=True, compress_ratio=1, rotate=0):
    """
    Create an animated GIF from a list of image paths.
    """
    # [1] Sort the image paths
    list_paths = sorted(list_paths)

    # [2] Create a list to hold the image data
    image_data = []

    # [3] Load each image, apply compression and rotation
    for image_path in list_paths:
        img = Image.open(image_path)

        if compress_ratio != 1:
            new_width = int(img.width * compress_ratio)
            new_height = int(img.height * compress_ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)

        if rotate in [0, 90, 180, 270]:
            img = img.rotate(rotate, expand=True)

        img_array = np.array(img)
        image_data.append(img_array)

    # [4] Apply bounce effect if needed
    if bounce:
        reversed_data = image_data[-2:0:-1]  # exclude first and last
        image_data.extend(reversed_data)

    # [5] Save as GIF
    imageio.mimsave(path_save, image_data, format='GIF', fps=fps, loop=0)
    print(f'GIF saved to: {path_save}')


def dir_of_images_into_GIF(directory, fps=10, output_filename='output.gif',
                           bounce=True, compress_ratio=1, rotate=0):
    """
    Wrapper to generate GIF from all images in a directory.
    """
    # [1] Collect image file paths
    list_paths = sorted([
        os.path.join(directory, fname)
        for fname in os.listdir(directory)
        if fname.lower().endswith(('.png', '.jpg', '.jpeg'))])

    # [2] Call the core GIF creation function
    path_save=os.path.join(directory, output_filename)
    list_paths_of_images_into_GIF(list_paths, fps, path_save, 
                                  bounce, compress_ratio, rotate)

    return os.path.join(directory, path_save)


def convert_plot_to_gif(fig, ax, list_view_init, path_save, duration=100):
    """
    Converts a 3D Matplotlib plot to a GIF by rotating the plot using predefined view angles.
    Parameters:
    - fig: Matplotlib figure object.
    - ax: Matplotlib 3D axis object.
    - list_view_init: List of tuples/lists containing (elevation, azimuth) angles.
    - filename: Name of the output GIF file.
    - duration: Duration of each frame in the GIF in milliseconds.
    from matplotlib.animation import FuncAnimation
    """
    print(f'\n[convert_plot_to_gif]')
    def update_view(angle):
        ax.view_init(elev=angle[0], azim=angle[1])
        return fig,
    #[2] Create an animation
    anim = FuncAnimation(fig, update_view, frames=list_view_init, blit=False, repeat=True)
    #[3] Save animation as GIF
    anim.save(path_save, writer='pillow', fps=1000/duration)




# [Visualize Kernel] End
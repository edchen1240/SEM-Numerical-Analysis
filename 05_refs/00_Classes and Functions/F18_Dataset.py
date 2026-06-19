"""
[F07_Web.py]
Purpose: Generate random datasets
Author: Meng-Chi Ed Chen
Date: 2024-04-03
Reference:
    1.
    2.

Status: Complete.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# [Generate Dataset] Start

def generate_3d_dataset_linearly_spaced(space_length, data_density, cone_slope):
    print('\n[generate_3d_dataset_linearly_spaced]')
    data_count_1D = int(data_density * space_length) + 1
    arr_X = np.linspace(-space_length / 2, +space_length / 2, data_count_1D)
    arr_Y = np.linspace(-space_length / 2, +space_length / 2, data_count_1D)
    arr_X, arr_Y = np.meshgrid(arr_X, arr_Y)
    arr_Z = cone_slope * np.sqrt(arr_X**2 + arr_Y**2)
    arr_XYZ = np.dstack((arr_X, arr_Y, arr_Z))
    arr_XYZ = arr_XYZ.reshape(-1, arr_XYZ.shape[2])
    print(f'--Shape of arr_XYZ: {arr_XYZ.shape}')
    return arr_XYZ


def generate_3d_dataset_random(data_count_3D, cone_slope, space_length):
    print('\n[generate_3d_dataset_random]')
    half_length = space_length / 2
    arr_XY = np.random.rand(data_count_3D, 2) * space_length - half_length
    arr_Z = cone_slope * np.sqrt(arr_XY[:, 0]**2 + arr_XY[:, 1]**2) 
    arr_XYZ = np.hstack((arr_XY, arr_Z[:, np.newaxis])) 
    print(f'--Shape of arr_XYZ: {arr_XYZ.shape}')
    return arr_XYZ




# [Generate Dataset] End




# [Visualize Dataset] Start

def plot_3D_data_space(arr_XYZ, path_save):
    #[1] Customize
    cmap='viridis'
    title = None
    xlabel, ylabel, zlabel='X', 'Y', 'Z'
    show_colorbar = False
    #[2] Create figure and 3D axis
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(arr_XYZ[:, 0], arr_XYZ[:, 1], arr_XYZ[:, 2], c=arr_XYZ[:, 2], cmap=cmap)
    #[3] Set labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    if title:
        ax.set_title(title)
    ax.grid(True)
    if show_colorbar:
        fig.colorbar(sc, ax=ax, shrink=0.5, aspect=5)
    #[4] Save plot as png
    if path_save:
        plt.savefig(path_save)
        print(f'--Plot saved at {path_save}')
    else:
        plt.title('plot_3D_data_space')
        plt.show()
    return fig, ax



"""
# Example use

#[3] Generate a list of inition view angles of elevation and azimuth. 
elve_azim_center = (30, 40) # Center elevation and azimuth
elve_azim_start = (30, 70) # Start elevation and azimuth
cnt_point = 40
list_view_init = F18_Dataset.generate_circular_view_init(elve_azim_center, elve_azim_start, cnt_point, clockwise=True)


#[4] Generate gif using a list of view angles.
path_save = os.path.join(dir_csv, f'{bsn}.gif')
F18_Dataset.convert_plot_to_gif(fig, ax, list_view_init, path_save, 80)

"""


def generate_circular_view_init(elve_azim_center, elve_azim_start, cnt_point, clockwise=True):
    """
    elve_start -> elve_min -> elve_center -> elve_max -> elve_start
    azim_start -> elve_center -> azim_max -> elve_center -> azim_start
    """
    elve_center, azim_center = elve_azim_center
    elve_start, azim_start = elve_azim_start
    #[1] Calculate the angular distances
    delta_elve = elve_start - elve_center
    delta_azim = azim_start - azim_center
    #[2] Determine the direction of rotation
    direction = 1 if clockwise else -1
    #[3] Calculate the step size for a full circle
    angle_step = 360 / cnt_point
    view_init_list = []
    for i in range(cnt_point):
        #[4] Calculate the new angle
        angle = i * angle_step * direction
        rad_angle = np.radians(angle)
        #[5] Calculate the new positions
        elve = elve_center + delta_elve * np.cos(rad_angle) - delta_azim * np.sin(rad_angle)
        azim = azim_center + delta_elve * np.sin(rad_angle) + delta_azim * np.cos(rad_angle)
        view_init_list.append([int(elve), int(azim)])
    view_init_list = view_init_list[:-1]  # Remove the last viewpoint that duplicate with the first viewpoint.
    print(f'--length: {len(view_init_list)}')
    return view_init_list




def convert_plot_to_gif(fig, ax, list_view_init, path_save, duration=100):
    """
    Converts a 3D Matplotlib plot to a GIF by rotating the plot using predefined view angles.
    Parameters:
    - fig: Matplotlib figure object.
    - ax: Matplotlib 3D axis object.
    - list_view_init: List of tuples/lists containing (elevation, azimuth) angles.
    - filename: Name of the output GIF file.
    - duration: Duration of each frame in the GIF in milliseconds.
    """
    print(f'\n[convert_plot_to_gif] (This might take a while depends on the complexity.)')
    def update_view(angle):
        ax.view_init(elev=angle[0], azim=angle[1])
        return fig,
    #[2] Create an animation
    anim = FuncAnimation(fig, update_view, frames=list_view_init, blit=False, repeat=True)
    #[3] Save animation as GIF
    anim.save(path_save, writer='pillow', fps=1000/duration)

    

def convert_plot_to_gif_multiple_axs(fig, list_or_array_of_axs, list_view_init, path_save, duration=100):
    """
    Converts a 3D Matplotlib plot to a GIF by rotating the plot using predefined view angles.
    Parameters:
    - fig: Matplotlib figure object.
    - list_or_array_of_axs: List or array of Matplotlib 3D axis objects.
    - list_view_init: List of tuples/lists containing (elevation, azimuth) angles.
    - path_save: Path and filename for the output GIF file.
    - duration: Duration of each frame in the GIF in milliseconds.
    """
    def update_view(angle):
        for ax in list_or_array_of_axs:
            ax.view_init(elev=angle[0], azim=angle[1])
        return fig

    # Create an animation
    anim = FuncAnimation(fig, update_view, frames=list_view_init, blit=False, repeat=True)

    # Save animation as GIF
    anim.save(path_save, writer='pillow', fps=1000/duration)




# [Visualize Dataset] End











# [Visualize Kernel] Start



def visualize_matrix_with_number_save(matrix, path, dpi=300):
    #[1] Check size.
    nrows, ncols = matrix.shape
    cnt_ele = nrows * ncols 
    if cnt_ele > 100:
        raise ValueError(f'The matrix ({nrows}, {ncols}) is too big to visualize with number.')
    
    #[2] Set plot
    fig_size = (max(nrows, 5) * 0.5, max(ncols, 5) * 0.5)
    plt.figure(figsize=fig_size, dpi=dpi)
    max_abs_val = np.max(np.abs(matrix))  # Find maximum of absolute value.
    plt.imshow(matrix, cmap='seismic', vmin=-max_abs_val, vmax=max_abs_val)
    
    #[3] Optionally add gridlines for very small matrices
    if nrows <= 5 and ncols <= 5:
        plt.grid(which='major', color='black', linestyle='-', linewidth=2)

    #[4] Annotate each cell with its value
    for i in range(nrows):
        for j in range(ncols):
            color = 'white' if abs(matrix[i, j]) in [np.min(matrix), np.max(matrix)] else 'black'
            plt.text(j, i, f'{matrix[i, j]:.2f}', ha='center', va='center', color=color, fontsize=8)
    
    #[5] Matrix statistics
    stat_max, stat_min, stat_mean, stat_med = round(np.max(matrix),3), round(np.min(matrix),3), round(np.mean(matrix),3), round(np.median(matrix),3)
    stats_text = f'Shape: {nrows} × {ncols}\nMax: {stat_max},  Min: {stat_min}\nMean: {stat_mean},  Median: {stat_med}'
    plt.text(0, -ncols//10, stats_text, fontsize=8, color='white', bbox=dict(facecolor='black', alpha=0.5))
    plt.axis('off')
    plt.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
    plt.close()


def visualize_matrix_save(matrix, path, dpi=300):
    nrows, ncols = matrix.shape
    fig_size = (max(nrows, 5) * 0.5, max(ncols, 5) * 0.5)
    plt.figure(figsize=fig_size, dpi=dpi)
    max_abs_val = np.max(np.abs(matrix))  # Find maximum of absolute value.
    plt.imshow(matrix, cmap='seismic', vmin=-max_abs_val, vmax=max_abs_val)
    # Optionally add gridlines for very small matrices
    if nrows <= 5 and ncols <= 5:
        plt.grid(which='major', color='black', linestyle='-', linewidth=2)
    # Matrix statistics
    stat_max, stat_min, stat_mean, stat_med = round(np.max(matrix),3), round(np.min(matrix),3), round(np.mean(matrix),3), round(np.median(matrix),3)
    stats_text = f'Shape: {nrows} × {ncols}\nMax: {stat_max},  Min: {stat_min}\nMean: {stat_mean},  Median: {stat_med}'
    plt.text(0, -ncols//10, stats_text, fontsize=8, color='white', bbox=dict(facecolor='black', alpha=0.5))
    plt.axis('off')
    plt.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    
    









# [Visualize Kernel] End
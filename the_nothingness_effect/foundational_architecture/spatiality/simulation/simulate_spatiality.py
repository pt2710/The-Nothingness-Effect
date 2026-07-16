"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Spatiality Simulation and Visualization Script

This script simulates the spatiality equation over a range of z values,
saves the results, and generates comprehensive visualizations of the results,
including static and dynamic 3D plots.

Key Features:
1. Progress bars for simulation and saving processes.
2. Static 3D scatter plot illustrating spatiality results.
3. Dynamic animated GIF visualizing spatial symmetry through rotation.
4. Saves simulation results to a CSV file and visualizations as image files.
5. All outputs are saved in the same directory as the script.

Usage:
Run this script directly to simulate spatiality and generate visualizations.

Note:
This script assumes the presence of the spatiality.py module in an appropriate
directory structure.
"""
import os
import numpy as np

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script_dir = os.path.dirname(os.path.abspath(__file__))
import csv
import time
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

import traceback
import random 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from the_nothingness_effect.foundational_architecture.spatiality import spatiality_equation

def simulate_spatiality(n_points=1000, z_range=(-100, 100)):
    """
    Simulates the spatiality equation over a range of z values.

    Args:
        n_points (int): Number of points to simulate.
        z_range (tuple): Range of z values.

    Returns:
        tuple: z_values, results_z, results_neg_z, is_opposite
    """
    z_values = [random.randint(z_range[0], z_range[1]) for _ in range(n_points)]
    results_z = np.zeros(n_points)
    results_neg_z = np.zeros(n_points)
    is_opposite = np.zeros(n_points, dtype=bool)

    logging.info("Starting spatiality simulation...")
    for i, z in enumerate(tqdm(z_values, desc="Simulating Spatiality", unit="point")):
        try:
            results_z[i], results_neg_z[i] = spatiality_equation(z)
            is_opposite[i] = np.isclose(results_z[i], -results_neg_z[i], atol=1e-6)
        except Exception as e:
            logging.error(f"Error in spatiality_equation at z={z}: {e}")
            results_z[i], results_neg_z[i] = np.nan, np.nan
            is_opposite[i] = False

    logging.info("Spatiality simulation completed.")
    return z_values, results_z, results_neg_z, is_opposite

def save_results(z_values, results_z, results_neg_z, is_opposite, filename):
    """
    Saves the simulation results to a CSV file.

    Args:
        z_values (np.ndarray): Array of z values.
        results_z (np.ndarray): Results for z.
        results_neg_z (np.ndarray): Results for -z.
        is_opposite (np.ndarray): Boolean array indicating if results are opposites.
        filename (str): Path to the CSV file.
    """
    try:
        logging.info(f"Saving results to CSV file: {filename}")
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Input (z)', 'Result for z', 'Result for -z', 'Is Opposite'])
            writer.writerows(zip(z_values, results_z, results_neg_z, is_opposite))
        logging.info(f"Results successfully saved to {filename}")
    except Exception as e:
        logging.error(f"Failed to save results to {filename}: {e}")
        logging.error(traceback.format_exc())

def visualize_spatiality_static(z_values, results_z, results_neg_z, is_opposite, filename_static):
    """
    Creates and saves a static 3D scatter plot of the spatiality simulation results.

    Args:
        z_values (np.ndarray): Array of z values.
        results_z (np.ndarray): Results for z.
        results_neg_z (np.ndarray): Results for -z.
        is_opposite (np.ndarray): Boolean array indicating if results are opposites.
        filename_static (str): Filename for the static visualization image.
    """
    max_value = max(np.abs(z_values).max(), np.abs(results_z).max(), np.abs(results_neg_z).max(), 1)

    pbar = tqdm(total=1, desc="Creating static visualization", unit="plot")
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='3d')

    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones(np.size(u)), np.cos(v))
    xs *= max_value
    ys *= max_value
    zs *= max_value
    ax.plot_surface(xs, ys, zs, color='blue', alpha=0.3)

    axis_factor = 0.9
    ax.plot([-axis_factor * max_value, axis_factor * max_value], [0, 0],
            [0, 0], color='red', linewidth=2)       # X-axis
    ax.plot([0, 0], [-axis_factor * max_value, axis_factor * max_value],
            [0, 0], color='green', linewidth=2)     # Y-axis
    ax.plot([0, 0], [0, 0], [-axis_factor * max_value, axis_factor * max_value],
            color='yellow', linewidth=2)             # Z-axis

    ax.set_title('Spatiality Simulation Results - 3D Sphere Plot', fontsize=16)
    ax.set_xlabel('X', fontsize=14)
    ax.set_ylabel('Y', fontsize=14)
    ax.set_zlabel('Z', fontsize=14)

    legend_elements = [
        Line2D([0], [0], color='red', lw=2, label='X-axis'),
        Line2D([0], [0], color='green', lw=2, label='Y-axis'),
        Line2D([0], [0], color='yellow', lw=2, label='Z-axis')
    ]
    ax.legend(handles=legend_elements, loc='upper left')

    plt.tight_layout()
    start_time = time.time()
    fig.savefig(filename_static)
    elapsed_time = time.time() - start_time
    pbar.update(1)
    pbar.set_description(f"Static visualization saved as '{filename_static}' in {elapsed_time:.2f} s")
    pbar.close()
    plt.close(fig)
    logging.info(f"Static visualization saved as '{filename_static}' in {elapsed_time:.2f} seconds.")

def visualize_spatiality_dynamic(z_values, results_z, results_neg_z, is_opposite, filename_animation):
    """
    Creates and saves an animated 3D visualization (GIF) of the spatiality simulation results.

    Args:
        z_values (np.ndarray): Array of z values.
        results_z (np.ndarray): Results for z.
        results_neg_z (np.ndarray): Results for -z.
        is_opposite (np.ndarray): Boolean array indicating if results are opposites.
        filename_animation (str): Filename for the animated visualization.
    """
    max_value = max(np.abs(z_values).max(), np.abs(results_z).max(), np.abs(results_neg_z).max(), 1)

    pbar = tqdm(total=720, desc="Creating animated visualization", unit="frame")
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones(np.size(u)), np.cos(v))
    xs *= max_value
    ys *= max_value
    zs *= max_value
    sphere = ax.plot_surface(xs, ys, zs, color='blue', alpha=0.3)

    axis_factor = 0.9
    ax.plot([-axis_factor * max_value, axis_factor * max_value], [0, 0],
            [0, 0], color='red', linewidth=2)       # X-axis
    ax.plot([0, 0], [-axis_factor * max_value, axis_factor * max_value],
            [0, 0], color='green', linewidth=2)     # Y-axis
    ax.plot([0, 0], [0, 0], [-axis_factor * max_value, axis_factor * max_value],
            color='yellow', linewidth=2)             # Z-axis

    ax.set_title('Spatiality Simulation Results - 3D Animated Visualization', fontsize=16)
    ax.set_xlabel('X', fontsize=14)
    ax.set_ylabel('Y', fontsize=14)
    ax.set_zlabel('Z', fontsize=14)

    def update(frame):
        angle = frame % 360
        ax.view_init(elev=angle * 0.5, azim=angle)
        pbar.update(1)
        pbar.set_description(f"Frame {frame+1}/720")
        return sphere,

    ani = animation.FuncAnimation(fig, update, frames=720, interval=50, blit=False)
    start_time = time.time()
    ani.save(filename_animation, writer='pillow', fps=20)
    elapsed_time = time.time() - start_time
    pbar.set_description(f"Animated visualization saved as '{filename_animation}' in {elapsed_time:.2f} s")
    pbar.close()
    logging.info(f"Animated visualization saved as '{filename_animation}' in {elapsed_time:.2f} seconds.")
    plt.close(fig)

def main():
    """
    Main function to run the simulation, save results, and create visualizations.
    """
    logging.info("Starting spatiality simulation...")
    z_values, results_z, results_neg_z, is_opposite = simulate_spatiality()
    csv_file = os.path.join(script_dir, "artifacts", 'spatiality_simulation_results.csv')
    
    save_results(z_values, results_z, results_neg_z, is_opposite, csv_file)
    png_file = os.path.join(script_dir, "artifacts", 'spatiality_simulation_visualization.png')
    logging.info("Starting creation of static PNG plot...")
    
    visualize_spatiality_static(z_values, results_z, results_neg_z, is_opposite, png_file)
    logging.info(f"Spatiality simulation static plot saved as {png_file}")
    
    gif_file = os.path.join(script_dir, "artifacts", 'spatiality_simulation_animation.gif')
    logging.info("Starting creation of animated GIF...")
    
    visualize_spatiality_dynamic(z_values, results_z, results_neg_z, is_opposite, gif_file)
    logging.info(f"Spatiality simulation animation saved as {gif_file}")

    violations = np.sum(~is_opposite)
    if violations > 0:
        print(f"Spatiality violations found: {violations} out of {len(z_values)} points")
        print("The equation does not demonstrate perfect spatiality.")
    else:
        print("All points passed. The equation demonstrates perfect spatiality.")


if __name__ == "__main__":
    main()
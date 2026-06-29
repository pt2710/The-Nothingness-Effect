# the_nothingness_effect/equations/duality/simulation/simulate_duality.py
"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Duality Simulation and Visualization Script
This script simulates the duality equation over a range of y values,
saves the results, and generates comprehensive visualizations of the results,
including static and dynamic 3D plots and 2D subplots of the outcomes.

Key Features:
1. Progress bars for simulation and saving processes.
2. Static 3D arc plot illustrating the dual arcs.
3. Static 2D subplots showing result vs. input and absolute difference.
4. Dynamic animated GIF visualizing dual arcs through rotation.
5. Saves simulation results to a CSV file and visualizations as image files.
6. Explicitly saves frame 640 of the 3D animation as a PNG.
7. All outputs are saved in the same directory as the script.

Usage:
Run this script directly to simulate duality and generate visualizations.

Note:
This script assumes the presence of the duality.py module in an appropriate
directory structure.
"""

import os
import sys

# Set up script and parent directories for imports and output paths
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import numpy as np
import csv
import time
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from duality import duality_equation

def simulate_duality(n_points=1000):
    """
    Simulates the duality equation over a specified number of random integer inputs.

    Parameters
    ----------
    n_points : int, optional
        Number of simulation points (default 1000).

    Returns
    -------
    list
        Each entry: [y, result_y, result_neg_y].
    """
    results = []
    logging.info(f"Starting duality simulation with {n_points} points.")
    for _ in tqdm(range(n_points), desc="Simulating Duality", unit="sim"):
        y = np.random.randint(-100, 100)
        try:
            result_y, result_neg_y = duality_equation(y)
        except Exception as e:
            logging.warning(f"Error at y={y}: {e}")
            result_y, result_neg_y = np.nan, np.nan
        results.append([y, result_y, result_neg_y])
    logging.info("Duality simulation completed.")
    return results

def save_results(results, filename):
    """
    Saves the simulation results to CSV.

    Parameters
    ----------
    results : list
    filename : str
    """
    try:
        logging.info(f"Saving results to CSV: {filename}")
        start = time.time()
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Input (y)', 'Result for y', 'Result for -y'])
            for row in tqdm(results, desc="Writing CSV", unit="row"):
                writer.writerow(row)
        logging.info(f"CSV saved in {time.time() - start:.2f}s")
    except Exception as e:
        logging.error(f"Failed to save CSV: {e}")

def visualize_duality(results, filename_static, filename_animation):
    """
    Generates visualizations of the duality simulation results:
    - Static 3D arcs
    - Static 2D subplots
    - Dynamic rotating arcs (animated GIF)
    - Explicitly saves frame 640 of the animation.

    Parameters
    ----------
    results : list
    filename_static : str
    filename_animation : str
    """
    # Prepare and filter result arrays
    y_vals  = np.array([r[0] for r in results])
    res_y   = np.array([r[1] for r in results])
    res_ny  = np.array([r[2] for r in results])
    valid   = ~np.isnan(res_y) & ~np.isnan(res_ny)
    y_vals, res_y, res_ny = y_vals[valid], res_y[valid], res_ny[valid]
    diff_vals = np.abs(res_y - res_ny)

    # --- Static 3D arcs at initial orientation ---
    try:
        logging.info(f"Creating static 3D arcs: {filename_static}")
        start = time.time()
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')

        theta_arc = np.linspace(0, 2 * np.pi, 200)
        r_val = 50
        arc1 = np.vstack((
            r_val * np.cos(theta_arc),
            r_val * np.sin(theta_arc),
            np.linspace(0, 300, theta_arc.size)
        ))
        arc2 = np.vstack((
            -r_val * np.cos(theta_arc),
            -r_val * np.sin(theta_arc),
            np.linspace(0, 300, theta_arc.size)
        ))

        ax.plot(arc1[0], arc1[1], arc1[2], color='blue', lw=2, label='Arc y')
        ax.plot(arc2[0], arc2[1], arc2[2], color='red',  lw=2, label='Arc -y')

        ax.set_title('Static Duality Arcs at θ=0', fontsize=14)
        ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
        ax.legend(); ax.set_box_aspect([1,1,1])

        plt.tight_layout()
        fig.savefig(filename_static, dpi=300)
        plt.close(fig)
        logging.info(f"Static arcs saved in {time.time() - start:.2f}s")
    except Exception as e:
        logging.error(f"Static arc visualization failed: {e}")

    # --- Static 2D subplots of results and differences ---
    try:
        subplots_file = os.path.join(script_dir, 'duality_simulation_subplots.png')
        logging.info(f"Creating 2D subplots: {subplots_file}")
        start = time.time()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Top: result vs input
        ax1.scatter(y_vals, res_y,  label='Result for y',  color='blue',  alpha=0.6)
        ax1.scatter(y_vals, res_ny, label='Result for -y', color='red',   alpha=0.6)
        ax1.set_title('Duality Simulation Results', fontsize=16)
        ax1.set_xlabel('Input Value (y)', fontsize=14)
        ax1.set_ylabel('Result',            fontsize=14)
        ax1.legend(); ax1.grid(True)

        # Bottom: absolute difference
        ax2.scatter(y_vals, diff_vals, color='green', alpha=0.6)
        ax2.set_title('Absolute Difference between Results', fontsize=16)
        ax2.set_xlabel('Input Value (y)', fontsize=14)
        ax2.set_ylabel('Absolute Difference', fontsize=14)
        ax2.grid(True)

        fig.tight_layout()
        fig.savefig(subplots_file, dpi=300)
        plt.close(fig)
        logging.info(f"2D subplots saved in {time.time() - start:.2f}s")
    except Exception as e:
        logging.error(f"2D subplot visualization failed: {e}")

    # --- Animated rotating dual arcs ---
    try:
        logging.info(f"Creating animated visualization: {filename_animation}")
        start = time.time()
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim(-100, 100); ax.set_ylim(-100, 100); ax.set_zlim(0, 300)
        ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
        ax.set_title('3D Dual Arcs Rotating around Z-axis')

        line1, = ax.plot([], [], [], lw=2, color='blue', label='Arc y')
        line2, = ax.plot([], [], [], lw=2, color='red',  label='Arc -y')
        ax.legend()

        base1, base2 = arc1, arc2
        n_frames = 800  # ensures capture of frame 640

        def init():
            line1.set_data([], []); line1.set_3d_properties([])
            line2.set_data([], []); line2.set_3d_properties([])
            return line1, line2

        def animate(frame):
            theta = 2 * np.pi * frame / n_frames
            Rz = np.array([[ np.cos(theta), -np.sin(theta), 0],
                           [ np.sin(theta),  np.cos(theta), 0],
                           [             0,              0, 1]])
            rot1 = Rz @ base1
            rot2 = Rz @ base2
            line1.set_data(rot1[0], rot1[1]); line1.set_3d_properties(rot1[2])
            line2.set_data(rot2[0], rot2[1]); line2.set_3d_properties(rot2[2])

            # explicitly save frame 640 (1-based index)
            if frame == 639:
                outpng_640 = os.path.join(script_dir, "duality_frame_640.png")
                plt.savefig(outpng_640, dpi=300)
                logging.info(f"Frame 640 saved: {outpng_640}")

            return line1, line2

        ani = animation.FuncAnimation(
            fig, animate, init_func=init,
            frames=n_frames, interval=50, blit=False
        )
        plt.tight_layout()

        # Save animated GIF on background thread with progress bar
        import threading
        save_evt = threading.Event()
        def _save():
            try:
                ani.save(filename_animation, writer='pillow', fps=20)
                logging.info("Animated GIF saved.")
            except Exception as e:
                logging.error(f"Failed to save GIF: {e}")
            finally:
                save_evt.set()

        threading.Thread(target=_save).start()
        with tqdm(total=n_frames * 0.05, desc="Saving GIF", unit="s") as bar:
            while not save_evt.is_set():
                time.sleep(0.5)
                bar.update(0.5)

        logging.info(f"Animation saved in {time.time() - start:.2f}s")
        plt.close(fig)
    except Exception as e:
        logging.error(f"Animated visualization failed: {e}")

def main():
    """
    Executes the full duality simulation workflow.
    """
    logging.info(f"Script directory: {script_dir}")
    n = 1000
    results = simulate_duality(n)

    csv_path = os.path.join(script_dir, 'duality_simulation_results.csv')
    png_path = os.path.join(script_dir, 'duality_simulation_visualization.png')
    gif_path = os.path.join(script_dir, 'duality_simulation_animation.gif')

    save_results(results, csv_path)
    visualize_duality(results, png_path, gif_path)

    # Verify perfect duality
    violations = [r for r in results if not np.isclose(r[2], -r[1], atol=1e-6)]
    if violations:
        logging.warning(f"Duality violations: {len(violations)}/{n}")
    else:
        logging.info("All simulations demonstrate perfect duality.")

if __name__ == "__main__":
    main()

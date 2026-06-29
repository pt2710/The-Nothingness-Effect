"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Symmetry Simulation and Visualization Script
This script imports the symmetry.py module, runs a symmetry simulation over time,
and generates visualizations of the results, including static and animated plots.

Key Features:
1. Progress bars for simulation and saving processes.
2. Static 2D plots illustrating symmetry with a four-line cross and colored difference lines.
3. Dynamic animated GIF visualizing the evolution of symmetry over simulation steps.
4. Estimated time tracking for each major process.
5. Explicitly saves frame 640 of the animated visualization as a PNG.
"""

import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__)) 
parent_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, parent_dir)

import numpy as np
import csv
import time
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection
from symmetry import symmetry_equation

def simulate_symmetry(n_steps=1000):
    """
    Simulates the symmetry equation over a specified number of steps.

    Parameters
    ----------
    n_steps : int, optional
        The number of simulation steps to perform (default is 1000).

    Returns
    -------
    list
        A list of results, each containing the input value, result for x, and result for -x.
    """
    results = []
    print(f"Starting symmetry simulation with {n_steps} steps.")
    for _ in tqdm(range(n_steps), desc="Simulating Symmetry", unit="step"):
        x = np.random.randint(-100, 100)
        try:
            result_x, result_neg_x = symmetry_equation(x)
            results.append([x, result_x, result_neg_x])
        except Exception as e:
            print(f"Error in symmetry_equation at x={x}: {e}")
            results.append([x, np.nan, np.nan])
    print("Symmetry simulation completed.")
    return results

def save_results(results, filename):
    """
    Saves the simulation results to a CSV file.

    Parameters
    ----------
    results : list
        The list of results to save.
    filename : str
        The name of the CSV file to save the results to.
    """
    try:
        print(f"Saving results to CSV file: {filename}")
        start_time = time.time()
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Input (x)', 'Result for x', 'Result for -x'])
            for row in tqdm(results, desc="Saving CSV", unit="row"):
                writer.writerow(row)
        elapsed_time = time.time() - start_time
        print(f"Results successfully saved to {filename} in {elapsed_time:.2f} seconds.")
    except Exception as e:
        print(f"Failed to save results to {filename}: {e}")

def visualize_symmetry(results, filename_static, filename_animation):
    """
    Generates visualizations of the symmetry simulation results, including static and animated plots.

    Parameters
    ----------
    results : list
        The list of results to visualize.
    filename_static : str
        The filename for saving the static visualization.
    filename_animation : str
        The filename for saving the animated visualization.
    """
    # Extract values for plotting
    x_values = [row[0] for row in results]
    results_x = [row[1] for row in results]
    results_neg_x = [row[2] for row in results]

    x_values_np = np.array(x_values)
    results_x_np = np.array(results_x)
    results_neg_x_np = np.array(results_neg_x)
    difference = np.abs(results_x_np - results_neg_x_np)

    valid_mask = ~np.isnan(results_x_np) & ~np.isnan(results_neg_x_np)
    x_values_np = x_values_np[valid_mask]
    results_x_np = results_x_np[valid_mask]
    results_neg_x_np = results_neg_x_np[valid_mask]
    difference = difference[valid_mask]

    # Static Visualization
    try:
        print(f"Creating static visualization: {filename_static}")
        start_time = time.time()
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))

        angles = [45, -45, 135, -135]
        colors = ['blue', 'red', 'blue', 'red']
        labels = ['Line 1 (+45°)', 'Line 2 (-45°)', 'Line 3 (+135°)', 'Line 4 (-135°)']
        x = np.linspace(-100, 100, 400)
        for angle, color, label in zip(angles, colors, labels):
            theta = np.radians(angle)
            y = np.tan(theta) * x
            ax1.plot(x, y, color=color, alpha=0.7, label=label)

        ax1.set_title('Symmetry Test Results - Four Symmetric Lines Forming a Cross', fontsize=16)
        ax1.set_xlabel('Input Value (x)', fontsize=14)
        ax1.set_ylabel('Result', fontsize=14)
        ax1.legend()
        ax1.grid(True)

        ax2.set_title('Absolute Difference between Results', fontsize=16)
        ax2.set_xlabel('Input Value (x)', fontsize=14)
        ax2.set_ylabel('Absolute Difference', fontsize=14)
        ax2.grid(True)

        sorted_indices = np.argsort(x_values_np)
        sorted_x = x_values_np[sorted_indices]
        sorted_diff = difference[sorted_indices]
        points = np.array([sorted_x, sorted_diff]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        cmap = plt.get_cmap('viridis')
        norm = plt.Normalize(sorted_diff.min(), sorted_diff.max())
        lc = LineCollection(segments, cmap=cmap, norm=norm)
        lc.set_array(sorted_diff)
        lc.set_linewidth(2)
        line = ax2.add_collection(lc)
        cbar = fig.colorbar(line, ax=ax2)
        cbar.set_label('Absolute Difference', fontsize=14)
        ax2.set_xlim(sorted_x.min(), sorted_x.max())
        ax2.set_ylim(0, sorted_diff.max() * 1.1)

        plt.tight_layout()
        fig.savefig(filename_static)
        plt.close(fig)
        elapsed_time = time.time() - start_time
        print(f"Static visualization saved to {filename_static} in {elapsed_time:.2f} seconds.")
    except Exception as e:
        print(f"Failed to create static visualization: {e}")

    # Animated Visualization
    try:
        print(f"Creating animated visualization: {filename_animation}")
        start_time = time.time()
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim3d([-150.0, 150.0])
        ax.set_xlabel('X')
        ax.set_ylim3d([-150.0, 150.0])
        ax.set_ylabel('Y')
        ax.set_zlim3d([0.0, 300.0])
        ax.set_zlabel('Z')
        ax.set_title('3D Symmetry Simulation Evolution', fontsize=16)

        # Initialize lines for animation
        lines = []
        colors = ['blue', 'red', 'orange', 'purple']
        labels = ['Arc 1 (+0°)', 'Arc 2 (+90°)', 'Arc 3 (+180°)', 'Arc 4 (+270°)']
        for color, label in zip(colors, labels):
            line, = ax.plot([], [], [], lw=2, color=color, label=label)
            lines.append(line)
        ax.legend()

        def init():
            for line in lines:
                line.set_data([], [])
                line.set_3d_properties([])
            return lines

        def animate(frame):
            # rotation around Z for each frame
            angle = 360 * frame / n_frames_animation
            theta = np.radians(angle)
            rotation_matrix = np.array([
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta),  np.cos(theta), 0],
                [0,              0,             1]
            ])

            # define four arcs
            r = 50
            theta_arc = np.linspace(0, 2 * np.pi, 100)
            arcs = []
            for offset in [0, np.pi/2, np.pi, 3*np.pi/2]:
                x = r * np.cos(theta_arc + offset)
                y = r * np.sin(theta_arc + offset)
                z = np.linspace(0, 300, 100)
                arcs.append(np.vstack((x, y, z)))

            # rotate and update
            for line, arc in zip(lines, arcs):
                rotated = rotation_matrix @ arc
                line.set_data(rotated[0], rotated[1])
                line.set_3d_properties(rotated[2])

            # explicitly save frame 640 (1‑based index)
            if frame == 639:
                outpng_640 = os.path.join(script_dir, "symmetry_frame_640.png")
                plt.savefig(outpng_640, dpi=300)
                print(f"[INFO] Frame 640 saved: {outpng_640}")

            return lines

        # number of frames—must be ≥ 640 to capture frame 640
        n_frames_animation = 800

        ani = animation.FuncAnimation(
            fig, animate, init_func=init,
            frames=n_frames_animation, interval=50, blit=False
        )

        plt.tight_layout()

        # save with threading to show progress
        import threading
        save_event = threading.Event()

        def save_animation():
            try:
                ani.save(filename_animation, writer='pillow', fps=20)
                print("Animated GIF saved successfully.")
            except Exception as e:
                print(f"Failed to save animated GIF: {e}")
            finally:
                save_event.set()

        save_thread = threading.Thread(target=save_animation)
        save_thread.start()

        estimated_time = n_frames_animation * 0.05
        with tqdm(total=estimated_time, desc="Saving Animation GIF", unit="sec") as pbar:
            while not save_event.is_set():
                time.sleep(0.5)
                pbar.update(0.5)
        save_thread.join()

        elapsed_time = time.time() - start_time
        print(f"Animated visualization saved to {filename_animation} in {elapsed_time:.2f} seconds.")
        plt.close(fig)
    except Exception as e:
        print(f"Failed to create animated visualization: {e}")

def main():
    """
    Main function to execute the symmetry simulation and visualization.
    """
    print(f"Script directory: {script_dir}")

    n_simulations = 1000
    csv_file = os.path.join(script_dir, 'symmetry_simulation_results.csv')
    image_file_static = os.path.join(script_dir, 'symmetry_simulation_visualization.png')
    image_file_animation = os.path.join(script_dir, 'symmetry_simulation_animation.gif')

    results = simulate_symmetry(n_simulations)
    save_results(results, csv_file)
    visualize_symmetry(results, image_file_static, image_file_animation)

    violations = [row for row in results if not np.isclose(row[2], -row[1], atol=1e-6)]
    if violations:
        print(f"Symmetry violations found: {len(violations)} out of {n_simulations}.")
        print("The equation does not demonstrate perfect symmetry.")
    else:
        print("All simulations passed. The equation demonstrates perfect symmetry.")

if __name__ == "__main__":
    main()

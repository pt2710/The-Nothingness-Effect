"""
Author: B. McCrackn
Email: thenothingnesseffect@gmail.com
...

Symmetry Test and Visualization Script

Usage:
    Run this script directly to test symmetry and generate visualization.
"""

import os
import sys
import numpy as np
import csv
import time
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection

# --- Robust project root detection (adjust marker as needed)
def find_project_root(marker_file_or_folder="equations"):
    d = os.path.abspath(__file__)
    while True:
        d = os.path.dirname(d)
        if marker_file_or_folder in os.listdir(d):
            return d
        if d == os.path.dirname(d):
            break
    raise RuntimeError(f"Could not find project root with marker '{marker_file_or_folder}'.")

project_root = find_project_root()
sys.path.insert(0, project_root)

from equations.symmetry.symmetry import symmetry_equation

def test_symmetry(n_tests=1000):
    results = []
    print(f"Starting symmetry simulation with {n_tests} tests.")
    for _ in tqdm(range(n_tests), desc="Simulating Symmetry", unit="test"):
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
        for angle, color, label in zip(angles, colors, labels):
            theta = np.radians(angle)
            x = np.linspace(-100, 100, 400)
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
            angle = 360 * frame / n_frames_animation
            theta = np.radians(angle)
            rotation_matrix = np.array([
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta),  np.cos(theta), 0],
                [0,              0,             1]
            ])
            r1 = 50
            theta_arc = np.linspace(0, 2 * np.pi, 100)
            x1 = r1 * np.cos(theta_arc)
            y1 = r1 * np.sin(theta_arc)
            z1 = np.linspace(0, 300, 100)
            x2 = -r1 * np.cos(theta_arc)
            y2 = -r1 * np.sin(theta_arc)
            z2 = np.linspace(0, 300, 100)
            r2 = 50
            x3 = r2 * np.cos(theta_arc + np.pi/2)
            y3 = r2 * np.sin(theta_arc + np.pi/2)
            z3 = np.linspace(0, 300, 100)
            x4 = -r2 * np.cos(theta_arc + np.pi/2)
            y4 = -r2 * np.sin(theta_arc + np.pi/2)
            z4 = np.linspace(0, 300, 100)
            arc1 = np.vstack((x1, y1, z1))
            arc2 = np.vstack((x2, y2, z2))
            arc3 = np.vstack((x3, y3, z3))
            arc4 = np.vstack((x4, y4, z4))
            rotated_arc1 = rotation_matrix @ arc1
            rotated_arc2 = rotation_matrix @ arc2
            rotated_arc3 = rotation_matrix @ arc3
            rotated_arc4 = rotation_matrix @ arc4
            lines[0].set_data(rotated_arc1[0], rotated_arc1[1])
            lines[0].set_3d_properties(rotated_arc1[2])
            lines[1].set_data(rotated_arc2[0], rotated_arc2[1])
            lines[1].set_3d_properties(rotated_arc2[2])
            lines[2].set_data(rotated_arc3[0], rotated_arc3[1])
            lines[2].set_3d_properties(rotated_arc3[2])
            lines[3].set_data(rotated_arc4[0], rotated_arc4[1])
            lines[3].set_3d_properties(rotated_arc4[2])
            return lines
        n_frames_animation = 200
        ani = animation.FuncAnimation(
            fig, animate, init_func=init,
            frames=n_frames_animation, interval=50, blit=False
        )
        plt.tight_layout()
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
    if '__file__' in globals():
        script_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        script_dir = os.getcwd()
        print("Warning: __file__ is not defined. Using current working directory instead.")
    print(f"Script directory: {script_dir}")
    n_tests = 1000
    csv_file = os.path.join(script_dir, 'symmetry_test_results.csv')
    image_file_static = os.path.join(script_dir, 'symmetry_test_visualization.png')
    image_file_animation = os.path.join(script_dir, 'symmetry_test_animation.gif')
    results = test_symmetry(n_tests)
    save_results(results, csv_file)
    visualize_symmetry(results, image_file_static, image_file_animation)
    violations = [row for row in results if not np.isclose(row[2], -row[1], atol=1e-6)]
    if violations:
        print(f"Symmetry violations found: {len(violations)} out of {n_tests} tests.")
        print("The equation does not demonstrate perfect symmetry.")
    else:
        print("All tests passed. The equation demonstrates perfect symmetry.")

if __name__ == "__main__":
    main()

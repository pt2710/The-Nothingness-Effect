"""
Author: B. McCrackn
Email: thenothingnesseffect@gmail.com

Duality Test and Visualization Script

Usage:
    Run this script directly to test duality and generate visualization.
"""

import os
import sys

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

import csv
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tqdm import tqdm

from the_nothingness_effect.foundational_architecture.duality.duality import duality_equation

def test_duality(n_tests=1000):
    """
    Runs a series of tests on the duality equation to verify its properties.

    Returns
    -------
    list
        A list of results, each containing the input value, result for y, and result for -y.
    """
    results = []
    print(f"Starting duality simulation with {n_tests} tests.")
    for _ in tqdm(range(n_tests), desc="Simulating Duality", unit="test"):
        y = np.random.randint(-100, 100)
        try:
            result_y, result_neg_y = duality_equation(y)
            results.append([y, result_y, result_neg_y])
        except Exception as e:
            print(f"Error in duality_equation at y={y}: {e}")
            results.append([y, np.nan, np.nan])
    print("Duality simulation completed.")
    return results

def save_results(results, filename):
    """
    Saves the test results to a CSV file.
    """
    try:
        print(f"Saving results to CSV file: {filename}")
        start_time = time.time()
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Input (y)', 'Result for y', 'Result for -y'])
            for row in tqdm(results, desc="Saving CSV", unit="row"):
                writer.writerow(row)
        elapsed_time = time.time() - start_time
        print(f"Results successfully saved to {filename} in {elapsed_time:.2f} seconds.")
    except Exception as e:
        print(f"Failed to save results to {filename}: {e}")

def visualize_duality(results, filename_static, filename_animation):
    """
    Generates visualizations of the duality test results, including static and animated plots.
    """
    y_values = [row[0] for row in results]
    results_y = [row[1] for row in results]
    results_neg_y = [row[2] for row in results]

    y_values_np = np.array(y_values)
    results_y_np = np.array(results_y)
    results_neg_y_np = np.array(results_neg_y)
    difference = np.abs(results_y_np - results_neg_y_np)
    valid_mask = ~np.isnan(results_y_np) & ~np.isnan(results_neg_y_np)
    y_values_np = y_values_np[valid_mask]
    results_y_np = results_y_np[valid_mask]
    results_neg_y_np = results_neg_y_np[valid_mask]
    difference = difference[valid_mask]

    try:
        print(f"Creating static visualization: {filename_static}")
        start_time = time.time()
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
        ax1.scatter(y_values_np, results_y_np, label='Result for y', color='blue', alpha=0.5)
        ax1.scatter(y_values_np, results_neg_y_np, label='Result for -y', color='red', alpha=0.5)
        ax1.set_title('Duality Test Results')
        ax1.set_xlabel('Input Value (y)')
        ax1.set_ylabel('Result')
        ax1.legend()
        ax1.grid(True)
        ax2.scatter(y_values_np, difference, color='green', alpha=0.5)
        ax2.set_title('Absolute Difference between Results')
        ax2.set_xlabel('Input Value (y)')
        ax2.set_ylabel('Absolute Difference')
        ax2.grid(True)
        plt.tight_layout()
        plt.savefig(filename_static)
        plt.close()
        elapsed_time = time.time() - start_time
        print(f"Static visualization saved to {filename_static} in {elapsed_time:.2f} seconds.")
    except Exception as e:
        print(f"Failed to create static visualization: {e}")

    try:
        print(f"Creating animated visualization: {filename_animation}")
        start_time = time.time()
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        line1, = ax.plot([], [], [], lw=2, color='blue', label='Arc 1 (y)')
        line2, = ax.plot([], [], [], lw=2, color='red', label='Arc 2 (-y)')
        ax.set_xlim3d([-150.0, 150.0])
        ax.set_xlabel('X')
        ax.set_ylim3d([-150.0, 150.0])
        ax.set_ylabel('Y')
        ax.set_zlim3d([0.0, 300.0])
        ax.set_zlabel('Z')
        ax.set_title('3D Dual Arcs Spinning Around Z-axis')
        ax.legend()

        def init():
            line1.set_data([], [])
            line1.set_3d_properties([])
            line2.set_data([], [])
            line2.set_3d_properties([])
            return line1, line2

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
            r2 = 50
            x2 = -r2 * np.cos(theta_arc)
            y2 = -r2 * np.sin(theta_arc)
            z2 = np.linspace(0, 300, 100)
            arc1 = np.vstack((x1, y1, z1))
            arc2 = np.vstack((x2, y2, z2))
            rotated_arc1 = rotation_matrix @ arc1
            rotated_arc2 = rotation_matrix @ arc2
            line1.set_data(rotated_arc1[0], rotated_arc1[1])
            line1.set_3d_properties(rotated_arc1[2])
            line2.set_data(rotated_arc2[0], rotated_arc2[1])
            line2.set_3d_properties(rotated_arc2[2])
            return line1, line2

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
    csv_file = os.path.join(script_dir, 'duality_test_results.csv')
    image_file_static = os.path.join(script_dir, 'duality_test_visualization.png')
    image_file_animation = os.path.join(script_dir, 'duality_test_animation.gif')
    results = test_duality(n_tests)
    save_results(results, csv_file)
    visualize_duality(results, image_file_static, image_file_animation)
    violations = [row for row in results if not np.isclose(row[2], -row[1], atol=1e-6)]
    if violations:
        print(f"Duality violations found: {len(violations)} out of {n_tests} tests.")
        print("The equation does not demonstrate perfect duality.")
    else:
        print("All tests passed. The equation demonstrates perfect duality.")

if __name__ == "__main__":
    main()

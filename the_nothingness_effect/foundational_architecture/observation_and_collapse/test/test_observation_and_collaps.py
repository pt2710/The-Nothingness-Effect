"""
Author: B. McCrackn
Email: thenothingnesseffect@gmail.com
...

Observation and Collapse Test and Visualization Script

Usage:
    Run this script directly to test observation and collapse and generate visualizations.
"""

import os
import csv
import time
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

# --- Robust project root detection (adjust marker as needed)

from the_nothingness_effect.foundational_architecture.observation_and_collapse.observation_and_collapse import observation_and_collapse

def test_observation_and_collapse(n_tests=1000):
    results = []
    print(f"Starting observation and collapse test with {n_tests} tests.")

    for _ in tqdm(range(n_tests), desc="Testing Observation and Collapse", unit="test"):
        x = np.random.uniform(-100, 100)
        y = np.random.uniform(-100, 100)
        z = np.random.uniform(-100, 100)
        try:
            ci_result, ui_result = observation_and_collapse()(x, y, z)
            results.append([x, y, z, ci_result, ui_result])
        except Exception as e:
            print(f"Error in observation_and_collapse for inputs ({x}, {y}, {z}): {e}")

    print(f"All {n_tests} tests completed.")
    return results

def save_results(results, filename):
    try:
        print(f"Saving results to CSV file: {filename}")
        start_time = time.time()
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['X', 'Y', 'Z', 'Countable Infinity Result', 'Uncountable Infinity Result'])
            for row in tqdm(results, desc="Saving CSV", unit="row"):
                writer.writerow(row)
        elapsed_time = time.time() - start_time
        print(f"Results successfully saved to {filename} in {elapsed_time:.2f} seconds.")
    except Exception as e:
        print(f"Failed to save results to {filename}: {e}")

def visualize_observation_and_collapse(results, filename_static, filename_animation):
    if not results:
        print("No results to visualize.")
        return

    x_values = np.array([row[0] for row in results])
    y_values = np.array([row[1] for row in results])
    z_values = np.array([row[2] for row in results])
    ci_results = np.array([row[3] for row in results])
    ui_results = np.array([row[4] for row in results])

    x_values = np.array([float(x) if isinstance(x, (int, float)) else 0 for x in x_values])
    y_values = np.array([float(y) if isinstance(y, (int, float)) else 0 for y in y_values])
    z_values = np.array([float(z) if isinstance(z, (int, float)) else 0 for z in z_values])
    ci_results = np.array([float(ci) if isinstance(ci, (int, float)) else 0 for ci in ci_results])
    ui_results = np.array([float(ui) if isinstance(ui, (int, float)) else 0 for ui in ui_results])

    try:
        print(f"Creating static visualization: {filename_static}")
        start_time = time.time()
        fig = plt.figure(figsize=(15, 12))
        ax1 = fig.add_subplot(221, projection='3d')
        ax1.scatter(x_values, y_values, z_values, c=ci_results, s=5, alpha=0.5)
        ax1.set_title('3D Scatter Plot of Countable Infinity Results')
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        ax2 = fig.add_subplot(222, projection='3d')
        ax2.scatter(x_values, y_values, z_values, c=ui_results, s=5, alpha=0.5)
        ax2.set_title('3D Scatter Plot of Uncountable Infinity Results')
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_zlabel('Z')
        ax3 = fig.add_subplot(223)
        ax3.scatter(x_values, ci_results, color='green', alpha=0.5, label='Countable Infinity')
        ax3.scatter(x_values, ui_results, color='red', alpha=0.5, label='Uncountable Infinity')
        ax3.set_title('X vs Results')
        ax3.set_xlabel('X')
        ax3.set_ylabel('Result')
        ax3.legend()
        ax4 = fig.add_subplot(224)
        ax4.scatter(y_values, ci_results, color='green', alpha=0.5, label='Countable Infinity')
        ax4.scatter(y_values, ui_results, color='red', alpha=0.5, label='Uncountable Infinity')
        ax4.set_title('Y vs Results')
        ax4.set_xlabel('Y')
        ax4.set_ylabel('Result')
        ax4.legend()
        plt.tight_layout()
        plt.savefig(filename_static)
        plt.close(fig)
        elapsed_time = time.time() - start_time
        print(f"Static visualization saved to {filename_static} in {elapsed_time:.2f} seconds.")
    except Exception as e:
        print(f"Failed to create static visualization: {e}")

    try:
        print(f"Creating animated visualization: {filename_animation}")
        start_time = time.time()
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(111, projection='3d')
        def update(frame):
            ax.clear()
            ax.set_xlim3d([np.min(x_values), np.max(x_values)])
            ax.set_xlabel('X')
            ax.set_ylim3d([np.min(y_values), np.max(y_values)])
            ax.set_ylabel('Y')
            ax.set_zlim3d([np.min(z_values), np.max(z_values)])
            ax.set_zlabel('Z')
            ax.set_title('3D Observation and Collapse Test Results')
            current_x = x_values[:frame+1]
            current_y = y_values[:frame+1]
            current_z = z_values[:frame+1]
            current_ci = ci_results[:frame+1]
            current_ui = ui_results[:frame+1]
            scatter1 = ax.scatter(current_x, current_y, current_z, c=current_ci, s=5, alpha=0.5, label='Countable Infinity')
            scatter2 = ax.scatter(current_x, current_y, current_z, c=current_ui, s=5, alpha=0.5, label='Uncountable Infinity')
            ax.legend()
            print(f"Processing frame {frame+1}/{len(results)}")
        ani = animation.FuncAnimation(fig, update, frames=len(results), interval=50, repeat=False)
        plt.tight_layout()
        try:
            ani.save(filename_animation, writer='pillow', fps=20)
            print(f"Animated GIF saved successfully to {filename_animation}.")
        except Exception as e:
            print(f"Failed to save animated GIF: {e}")
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
    csv_file = os.path.join(script_dir, 'observation_and_collapse_test_results.csv')
    image_file_static = os.path.join(script_dir, 'observation_and_collapse_test_visualization.png')
    image_file_animation = os.path.join(script_dir, 'observation_and_collapse_test_animation.gif')

    results = test_observation_and_collapse(n_tests)
    save_results(results, csv_file)
    visualize_observation_and_collapse(results, image_file_static, image_file_animation)

    print("All tests and visualizations completed successfully.")

if __name__ == "__main__":
    main()

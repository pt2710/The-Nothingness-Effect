"""
Author: B. McCrackn
Email: thenothingnesseffect@gmail.com

Countable Infinity Test and Visualization Script

Usage:
    Run this script directly to test countable infinity and generate visualizations.
"""

import os
# --- Robust project root detection (adjust marker as needed)

import csv
import time
import random
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from the_nothingness_effect.foundational_architecture.countable_infinity.countable_infinity import countable_infinity

def test_countable_infinity(n_tests=1000):
    """
    Tests the countable infinity property by running the countable_infinity function for random inputs.

    Args:
        n_tests (int): Number of tests to perform

    Returns:
        list: A list of results, each containing [x, y, z, result]
    """
    results = []
    print(f"Starting countable infinity test with {n_tests} tests.")

    for _ in tqdm(range(n_tests), desc="Testing Countable Infinity", unit="test"):
        x = random.uniform(-100, 100)
        y = random.uniform(-100, 100)
        z = random.uniform(-100, 100)
        result = next(countable_infinity(x, y, z))
        results.append([x, y, z, result])

    print(f"All {n_tests} tests completed.")
    return results

def save_results(results, filename):
    """
    Saves the test results to a CSV file.

    Args:
        results (list): List of test results.
        filename (str): Path to the CSV file.
    """
    try:
        print(f"Saving results to CSV file: {filename}")
        start_time = time.time()
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Input X', 'Input Y', 'Input Z', 'Result'])
            for row in tqdm(results, desc="Saving CSV", unit="row"):
                writer.writerow(row)
        elapsed_time = time.time() - start_time
        print(f"Results successfully saved to {filename} in {elapsed_time:.2f} seconds.")
    except Exception as e:
        print(f"Failed to save results to {filename}: {e}")

def visualize_countable_infinity(results, filename_static, filename_animation):
    """
    Generates and saves static and animated visualizations of the countable infinity test results.

    Args:
        results (list): List of test results.
        filename_static (str): Path to save the static PNG plot.
        filename_animation (str): Path to save the animated GIF plot.
    """
    x_values = np.array([row[0] for row in results])
    y_values = np.array([row[1] for row in results])
    z_values = np.array([row[2] for row in results])
    results_values = np.array([row[3] for row in results])

    # Static Visualization
    try:
        print(f"Creating static visualization: {filename_static}")
        start_time = time.time()
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

        ax1.scatter(x_values, results_values, label='X vs Result', color='blue', alpha=0.5)
        ax1.scatter(y_values, results_values, label='Y vs Result', color='red', alpha=0.5)
        ax1.scatter(z_values, results_values, label='Z vs Result', color='green', alpha=0.5)
        ax1.set_title('Countable Infinity Test Results')
        ax1.set_xlabel('Input Value')
        ax1.set_ylabel('Result')
        ax1.legend()
        ax1.grid(True)

        ax2.scatter(range(len(results)), results_values, color='purple', alpha=0.5)
        ax2.set_title('Result Distribution')
        ax2.set_xlabel('Test Number')
        ax2.set_ylabel('Result')
        ax2.grid(True)

        plt.tight_layout()
        plt.savefig(filename_static)
        plt.close()
        elapsed_time = time.time() - start_time
        print(f"Static visualization saved to {filename_static} in {elapsed_time:.2f} seconds.")
    except Exception as e:
        print(f"Failed to create static visualization: {e}")

    # Animated Visualization (3D Scatter Plot)
    try:
        print(f"Creating animated visualization: {filename_animation}")
        start_time = time.time()
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        def update(frame):
            ax.clear()
            ax.set_xlim3d([np.min(x_values), np.max(x_values)])
            ax.set_xlabel('X')
            ax.set_ylim3d([np.min(y_values), np.max(y_values)])
            ax.set_ylabel('Y')
            ax.set_zlim3d([np.min(z_values), np.max(z_values)])
            ax.set_zlabel('Z')
            ax.set_title('3D Countable Infinity Test Results')

            current_x = x_values[:frame+1]
            current_y = y_values[:frame+1]
            current_z = z_values[:frame+1]
            current_results = results_values[:frame+1]

            scatter = ax.scatter(current_x, current_y, current_z, c=current_results, s=5, alpha=0.5)
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
    """
    Runs the countable infinity test and visualization.

    Returns:
        None
    """
    if '__file__' in globals():
        script_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        script_dir = os.getcwd()
        print("Warning: __file__ is not defined. Using current working directory instead.")
    print(f"Script directory: {script_dir}")

    n_tests = 1000
    csv_file = os.path.join(script_dir, 'countable_infinity_test_results.csv')
    image_file_static = os.path.join(script_dir, 'countable_infinity_test_visualization.png')
    image_file_animation = os.path.join(script_dir, 'countable_infinity_test_animation.gif')

    results = test_countable_infinity(n_tests)
    save_results(results, csv_file)
    visualize_countable_infinity(results, image_file_static, image_file_animation)

    print("All tests and visualizations completed successfully.")

if __name__ == "__main__":
    main()

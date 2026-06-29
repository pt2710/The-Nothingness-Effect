"""
Author: B. McCrackn
Email: thenothingnesseffect@gmail.com
...

Spatiality Test and Visualization Script

Usage:
    Run this script directly to test spatiality and generate visualizations.
"""

import os
import sys
import numpy as np
import csv
import time
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tqdm import tqdm
from matplotlib.lines import Line2D

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
script_dir = os.path.dirname(os.path.abspath(__file__))

from equations.spatiality.spatiality import spatiality_equation

def test_spatiality(n_tests=1000):
    results = []
    for _ in tqdm(range(n_tests), desc="Testing Spatiality", unit="test"):
        z = random.randint(-100, 100)
        try:
            result_z, result_neg_z = spatiality_equation(z)
            is_opposite = np.isclose(result_z, -result_neg_z, atol=1e-6)
            results.append([z, result_z, result_neg_z, is_opposite])
            if not is_opposite:
                print(f"Spatiality violation found for z = {z}: result_z = {result_z}, result_neg_z = {result_neg_z}")
        except Exception as e:
            print(f"Error in spatiality_equation at z = {z}: {e}")
            results.append([z, np.nan, np.nan, False])
    return results

def save_results(results, filename):
    start_time = time.time()
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Input (z)', 'Result for z', 'Result for -z', 'Is Opposite'])
        for row in tqdm(results, desc="Saving CSV", unit="row"):
            writer.writerow(row)
    elapsed_time = time.time() - start_time
    print(f"Results saved to {filename} in {elapsed_time:.2f} seconds.")

def visualize_spatiality_static(results, filename_static):
    z_values = np.array([row[0] for row in results])
    results_z = np.array([row[1] for row in results])
    results_neg_z = np.array([row[2] for row in results])
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
            [0, 0], color='red', linewidth=2)
    ax.plot([0, 0], [-axis_factor * max_value, axis_factor * max_value],
            [0, 0], color='green', linewidth=2)
    ax.plot([0, 0], [0, 0], [-axis_factor * max_value, axis_factor * max_value],
            color='yellow', linewidth=2)
    ax.set_title('Spatiality Test Results - 3D Sphere Plot', fontsize=16)
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
    print(f"Static visualization saved as '{filename_static}' in {elapsed_time:.2f} seconds.")

def visualize_spatiality_dynamic(results, filename_animation):
    z_values = np.array([row[0] for row in results])
    results_z = np.array([row[1] for row in results])
    results_neg_z = np.array([row[2] for row in results])
    max_value = max(np.abs(z_values).max(), 
                    np.abs(results_z).max(), 
                    np.abs(results_neg_z).max(), 1)
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
            [0, 0], color='red', linewidth=2)
    ax.plot([0, 0], [-axis_factor * max_value, axis_factor * max_value],
            [0, 0], color='green', linewidth=2)
    ax.plot([0, 0], [0, 0], [-axis_factor * max_value, axis_factor * max_value],
            color='yellow', linewidth=2)
    ax.set_title('Spatiality Test Results - 3D Animated Visualization', fontsize=16)
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
    print(f"Animated visualization saved as '{filename_animation}' in {elapsed_time:.2f} seconds.")
    plt.close(fig)

def main():
    print("Starting spatiality tests...")
    n_tests = 1000
    csv_file = os.path.join(script_dir, 'spatiality_test_results.csv')
    image_file_static = os.path.join(script_dir, 'spatiality_visualization_static.png')
    image_file_animation = os.path.join(script_dir, 'spatiality_visualization_animation.gif')
    results = test_spatiality(n_tests)
    save_results(results, csv_file)
    visualize_spatiality_static(results, image_file_static)
    visualize_spatiality_dynamic(results, image_file_animation)
    violations = [row for row in results if not np.isclose(row[1], -row[2], atol=1e-6)]
    if violations:
        print(f"Spatiality violations found: {len(violations)} out of {n_tests} tests.")
        print("The function did not demonstrate the expected opposite behavior for some inputs.")
    else:
        print("All tests passed. The function demonstrates the expected opposite behavior.")

if __name__ == "__main__":
    main()

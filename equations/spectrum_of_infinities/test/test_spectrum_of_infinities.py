"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...
"""

import os
import sys

# --- Robust project root detection (adjust marker if needed)
def find_project_root(marker="equations"):
    d = os.path.abspath(__file__)
    while True:
        d = os.path.dirname(d)
        if marker in os.listdir(d):
            return d
        if d == os.path.dirname(d):
            break
    raise RuntimeError(f"Could not find project root with marker '{marker}'.")

project_root = find_project_root()
sys.path.insert(0, project_root)

import csv
import time
import random
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import colorsys

from equations.flowpoint.flowpoint import fp
from equations.spectrum_of_infinities.spectrum_of_infinities import SpectrumOfInfinities

def test_spectrum_of_infinities(n_tests=1000):
    results = []
    print(f"Starting spectrum of infinities test with {n_tests} tests.")

    for i in tqdm(range(n_tests), desc="Testing Spectrum of Infinities", unit="test"):
        spectrum = SpectrumOfInfinities()
        result_basic = spectrum.soi()
        random_norm_val = random.randint(1, 100)
        result_symmetric = spectrum.soi(normalize_to=random_norm_val, adv_mode=True, type='symmetric')
        results.append([result_basic, result_symmetric[0], result_symmetric[1]])
        if i < 5:
            print(f"Result {i}: {results[-1]}")
    print(f"All {n_tests} tests completed.")
    return results

def save_results(results, filename):
    try:
        print(f"Saving results to CSV file: {filename}")
        start_time = time.time()
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Basic Spectrum', 'Symmetric Spectrum Positive', 'Symmetric Spectrum Negative'])
            for row in tqdm(results, desc="Saving CSV", unit="row"):
                writer.writerow(row)
        elapsed_time = time.time() - start_time
        print(f"Results successfully saved to {filename} in {elapsed_time:.2f} seconds.")
    except Exception as e:
        print(f"Failed to save results to {filename}: {e}")

def visualize_spectrum_of_infinities(results, filename_static, filename_animation_basic, filename_animation_symmetric):
    def to_real(val):
        if val is None:
            return 0.0
        if isinstance(val, complex):
            return val.real
        return float(val)

    basic_spectrum = np.array([to_real(row[0]) for row in results])
    symmetric_spectrum_pos = np.array([to_real(row[1]) for row in results])
    symmetric_spectrum_neg = np.array([to_real(row[2]) for row in results])

    print(f"Basic Spectrum: min={basic_spectrum.min()}, max={basic_spectrum.max()}")
    print(f"Symmetric Spectrum Pos: min={symmetric_spectrum_pos.min()}, max={symmetric_spectrum_pos.max()}")
    print(f"Symmetric Spectrum Neg: min={symmetric_spectrum_neg.min()}, max={symmetric_spectrum_neg.max()}")

    try:
        print(f"Creating static visualization: {filename_static}")
        fig = plt.figure(figsize=(12, 20))

        ax3 = fig.add_subplot(323)
        ax3.set_title('Basic Spectrum')
        ax3.set_xlabel('Test Number')
        ax3.set_ylabel('Normalized Value')
        ax3.grid(True)
        ax3.set_ylim([-150, 150])
        ax3.axhline(y=100, color='green', linestyle='-')
        ax3.axhline(y=0, color='red', linestyle='--')

        ax4 = fig.add_subplot(324)
        ax4.set_title('Symmetric Spectrum')
        ax4.set_xlabel('Test Number')
        ax4.set_ylabel('Normalized Value')
        ax4.grid(True)
        ax4.set_ylim([-150, 150])
        ax4.axhline(y=100, color='blue', linestyle='-')
        ax4.axhline(y=-100, color='blue', linestyle='-')
        ax4.axhline(y=0, color='red', linestyle='--')

        plt.tight_layout()
        plt.savefig(filename_static)
        plt.close(fig)
        print(f"Static visualization saved to {filename_static}.")
    except Exception as e:
        print(f"Failed to create static visualization: {e}")

    try:
        print(f"Creating Basic Spectrum Animated Visualization: {filename_animation_basic}")
        start_time = time.time()
        fig = plt.figure(figsize=(20, 12))
        ax = fig.add_subplot(111, projection='3d')

        radius = 10.0
        fp_generators = [fp(np.random.uniform(0, 1)) for _ in range(len(results))]

        theta = np.random.uniform(0, 2*np.pi, len(results))
        phi = np.random.uniform(0, np.pi, len(results))
        r = radius * (1 + 0.1 * np.random.uniform(-1, 1, len(results)))
        x_sphere = r * np.sin(phi) * np.cos(theta)
        y_sphere = r * np.sin(phi) * np.sin(theta)
        z_sphere = r * np.cos(phi)

        def update_basic(frame):
            ax.clear()
            ax.set_xlim3d([-radius-5, radius+5])
            ax.set_xlabel('X')
            ax.set_ylim3d([-radius-5, radius+5])
            ax.set_ylabel('Y')
            ax.set_zlim3d([-radius-5, radius+5])
            ax.set_zlabel('Z')
            ax.set_title('Basic Spectrum 3D Animation')

            rotation_angle = frame * 0.01
            rotated_x = x_sphere * np.cos(rotation_angle) - y_sphere * np.sin(rotation_angle)
            rotated_y = x_sphere * np.sin(rotation_angle) + y_sphere * np.cos(rotation_angle)
            rotated_z = z_sphere

            oscillated_x = rotated_x[:frame+1] + np.array([next(fp_generators[i]) for i in range(frame+1)])
            oscillated_y = rotated_y[:frame+1] + np.array([next(fp_generators[i]) for i in range(frame+1)])
            oscillated_z = rotated_z[:frame+1] + np.array([next(fp_generators[i]) for i in range(frame+1)])

            colors = [colorsys.hsv_to_rgb(next(fp_generators[i]) % 1, 1, 1) for i in range(frame+1)]

            ax.scatter(oscillated_x, oscillated_y, oscillated_z, c=colors, s=5, alpha=1.0)
            print(f"Processing Basic Spectrum frame {frame+1}/{len(results)}")

        ani_basic = FuncAnimation(fig, update_basic, frames=len(results), interval=50, repeat=False)
        plt.tight_layout()
        try:
            ani_basic.save(filename_animation_basic, writer='pillow', fps=30)
            print(f"Animated GIF saved successfully to {filename_animation_basic}.")
        except Exception as e:
            print(f"Failed to save animated GIF: {e}")

        elapsed_time = time.time() - start_time
        print(f"Animated visualization saved to {filename_animation_basic} in {elapsed_time:.2f} seconds.")
        plt.close(fig)
    except Exception as e:
        print(f"Failed to create Basic Spectrum animated visualization: {e}")

    try:
        print(f"Creating Symmetric Spectrum Animated Visualization: {filename_animation_symmetric}")
        start_time = time.time()
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(111, projection='3d')
        radius = 10.0
        half_n = len(results) // 2

        theta_green = np.random.uniform(0, 2*np.pi, half_n)
        phi_green = np.random.uniform(0, np.pi/2, half_n)
        r_green = radius * (1 + 0.1 * np.random.uniform(-1, 1, half_n))
        x_green = r_green * np.sin(phi_green) * np.cos(theta_green)
        y_green = r_green * np.sin(phi_green) * np.sin(theta_green)
        z_green = r_green * np.cos(phi_green)

        theta_red = np.random.uniform(0, 2*np.pi, half_n)
        phi_red = np.random.uniform(np.pi/2, np.pi, half_n)
        r_red = radius * (1 + 0.1 * np.random.uniform(-1, 1, half_n))
        x_red = r_red * np.sin(phi_red) * np.cos(theta_red)
        y_red = r_red * np.sin(phi_red) * np.sin(theta_red)
        z_red = r_red * np.cos(phi_red)

        fp_generators_green = [fp(np.random.uniform(0, 1)) for _ in range(half_n)]
        fp_generators_red = [fp(np.random.uniform(0, 1)) for _ in range(half_n)]

        def update_symmetric(frame):
            ax.clear()
            ax.set_xlim3d([-radius-5, radius+5])
            ax.set_xlabel('X')
            ax.set_ylim3d([-radius-5, radius+5])
            ax.set_ylabel('Y')
            ax.set_zlim3d([-radius-5, radius+5])
            ax.set_zlabel('Z')
            ax.set_title('Symmetric Spectrum 3D Animation')

            rotation_angle = frame * 0.01
            rotated_x_green = x_green[:frame+1] * np.cos(rotation_angle) - y_green[:frame+1] * np.sin(rotation_angle)
            rotated_y_green = x_green[:frame+1] * np.sin(rotation_angle) + y_green[:frame+1] * np.cos(rotation_angle)
            rotated_z_green = z_green[:frame+1]

            rotated_x_red = x_red[:frame+1] * np.cos(-rotation_angle) - y_red[:frame+1] * np.sin(-rotation_angle)
            rotated_y_red = x_red[:frame+1] * np.sin(-rotation_angle) + y_red[:frame+1] * np.cos(-rotation_angle)
            rotated_z_red = z_red[:frame+1]

            oscillated_x_green = rotated_x_green + np.array([next(fp_generators_green[i]) for i in range(min(frame+1, half_n))])
            oscillated_y_green = rotated_y_green + np.array([next(fp_generators_green[i]) for i in range(min(frame+1, half_n))])
            oscillated_z_green = rotated_z_green + np.array([next(fp_generators_green[i]) for i in range(min(frame+1, half_n))])

            oscillated_x_red = rotated_x_red + np.array([next(fp_generators_red[i]) for i in range(min(frame+1, half_n))])
            oscillated_y_red = rotated_y_red + np.array([next(fp_generators_red[i]) for i in range(min(frame+1, half_n))])
            oscillated_z_red = rotated_z_red + np.array([next(fp_generators_red[i]) for i in range(min(frame+1, half_n))])

            ax.scatter(oscillated_x_green, oscillated_y_green, oscillated_z_green, c=['green']*len(oscillated_x_green), s=5, alpha=1.0)
            ax.scatter(oscillated_x_red, oscillated_y_red, oscillated_z_red, c=['red']*len(oscillated_x_red), s=5, alpha=1.0)
            print(f"Processing Symmetric Spectrum frame {frame+1}/{len(results)}")

        ani_symmetric = FuncAnimation(fig, update_symmetric, frames=len(results), interval=50, repeat=False)
        plt.tight_layout()
        try:
            ani_symmetric.save(filename_animation_symmetric, writer='pillow', fps=30)
            print(f"Animated GIF saved successfully to {filename_animation_symmetric}.")
        except Exception as e:
            print(f"Failed to save animated GIF: {e}")

        elapsed_time = time.time() - start_time
        print(f"Animated visualization saved to {filename_animation_symmetric} in {elapsed_time:.2f} seconds.")
        plt.close(fig)
    except Exception as e:
        print(f"Failed to create Symmetric Spectrum animated visualization: {e}")

def main():
    if '__file__' in globals():
        script_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        script_dir = os.getcwd()
        print("Warning: __file__ is not defined. Using current working directory instead.")
    print(f"Script directory: {script_dir}")

    n_tests = 1000
    csv_file = os.path.join(script_dir, 'spectrum_of_infinities_test_results.csv')
    image_file_static = os.path.join(script_dir, 'spectrum_of_infinities_test_visualization.png')
    image_file_animation_basic = os.path.join(script_dir, 'basic_spectrum_animation.gif')
    image_file_animation_symmetric = os.path.join(script_dir, 'symmetric_spectrum_animation.gif')

    results = test_spectrum_of_infinities(n_tests)
    save_results(results, csv_file)
    visualize_spectrum_of_infinities(results, image_file_static, image_file_animation_basic, image_file_animation_symmetric)

    print("All tests and visualizations completed successfully.")

if __name__ == "__main__":
    main()

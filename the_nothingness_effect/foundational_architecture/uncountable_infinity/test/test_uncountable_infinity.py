"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com

...
Test Uncountable Infinity Script

This script demonstrates and tests the uncountable infinity concept.
"""
import os
import sys
import csv
import time
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import colorsys

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

from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.flowpoint import fp
from the_nothingness_effect.foundational_architecture.uncountable_infinity.uncountable_infinity import uncountable_infinity
from the_nothingness_effect.foundational_architecture.symmetry.symmetry import symmetry_equation
from the_nothingness_effect.foundational_architecture.duality.duality import duality_equation
from the_nothingness_effect.foundational_architecture.spatiality.spatiality import spatiality_equation

def test_uncountable_infinity(n_tests=1000):
    results = []
    print(f"Starting uncountable infinity test with {n_tests} tests.")
    for _ in tqdm(range(n_tests), desc="Testing Uncountable Infinity", unit="test"):
        x = np.random.uniform(-100, 100)
        y = np.random.uniform(-100, 100)
        z = np.random.uniform(-100, 100)
        result = next(uncountable_infinity(x, y, z))
        results.append([x, y, z, result])
    print(f"All {n_tests} tests completed.")
    return results

def save_results(results, filename):
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

def visualize_uncountable_infinity(results, filename_static, filename_animation):
    x_values = np.array([row[0] for row in results])
    y_values = np.array([row[1] for row in results])
    z_values = np.array([row[2] for row in results])
    results_values = np.array([row[3] for row in results])

    # Static Visualization
    try:
        print(f"Creating static visualization: {filename_static}")
        start_time = time.time()
        fig = plt.figure(figsize=(15, 12))

        # Apply spatiality, duality, and symmetry
        spatialized = np.array([spatiality_equation(val)[0] for val in results_values])
        dualized = np.array([duality_equation(val)[0] for val in spatialized])
        symmetrized = np.array([symmetry_equation(val)[0] for val in dualized])

        # Normalize and scale the values for 3D sphere
        radius = 100
        x_normalized = (x_values - np.min(x_values)) / (np.max(x_values) - np.min(x_values)) * 2 - 1
        y_normalized = (y_values - np.min(y_values)) / (np.max(y_values) - np.min(y_values)) * 2 - 1
        z_normalized = (z_values - np.min(z_values)) / (np.max(z_values) - np.min(z_values)) * 2 - 1

        theta = np.arctan2(y_normalized, x_normalized)
        phi = np.arccos(z_normalized)
        r = radius * (1 + 0.1 * symmetrized)

        x_sphere = r * np.sin(phi) * np.cos(theta)
        y_sphere = r * np.sin(phi) * np.sin(theta)
        z_sphere = r * np.cos(phi)

        ax1 = fig.add_subplot(221, projection='3d')
        ax1.scatter(x_sphere, y_sphere, z_sphere, c=symmetrized, s=5, alpha=1.0)
        ax1.scatter(x_sphere, np.zeros_like(x_sphere), color='green', s=5, alpha=1.0)
        ax1.scatter(np.zeros_like(y_sphere), y_sphere, color='orange', s=5, alpha=1.0)
        ax1.scatter(np.zeros_like(z_sphere), np.zeros_like(z_sphere), z_values, color='red', s=5, alpha=1.0)
        ax1.set_title('YXZ Results (Spatiality of Z)')
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')

        ax2 = fig.add_subplot(222, projection='3d')
        ax2.scatter(x_sphere, np.zeros_like(x_sphere), x_values, color='green', alpha=0.5)
        ax2.set_title('X Results (Symmetry of X)')
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_zlabel('Z')

        ax3 = fig.add_subplot(223, projection='3d')
        ax3.scatter(np.zeros_like(y_sphere), y_sphere, y_values, color='orange', alpha=0.5)
        ax3.set_title('Y Result (Duality of Y)')
        ax3.set_xlabel('X')
        ax3.set_ylabel('Y')
        ax3.set_zlabel('Z')

        plt.tight_layout()
        plt.savefig(filename_static)
        plt.close(fig)
        elapsed_time = time.time() - start_time
        print(f"Static visualization saved to {filename_static} in {elapsed_time:.2f} seconds.")
    except Exception as e:
        print(f"Failed to create static visualization: {e}")

    # Animated Visualization
    try:
        print(f"Creating animated visualization: {filename_animation}")
        start_time = time.time()
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(111, projection='3d')

        fp_generators = [fp(np.random.uniform(0, 1)) for _ in range(len(results))]

        def update(frame):
            ax.clear()
            ax.set_xlim3d([-radius, radius])
            ax.set_xlabel('X')
            ax.set_ylim3d([-radius, radius])
            ax.set_ylabel('Y')
            ax.set_zlim3d([-radius, radius])
            ax.set_zlabel('Z')
            ax.set_title('3D Uncountable Infinity Test Results')

            if frame == 0:
                global x_sphere, y_sphere, z_sphere, theta, phi, rotation_axes, rotation_directions
                theta = np.random.uniform(0, 2*np.pi, len(results))
                phi = np.random.uniform(0, np.pi, len(results))
                r = radius * (1 + 0.1 * np.random.uniform(-1, 1, len(results)))
                x_sphere = r * np.sin(phi) * np.cos(theta)
                y_sphere = r * np.sin(phi) * np.sin(theta)
                z_sphere = r * np.cos(phi)
                rotation_axes = np.random.choice(['xy', 'xz', 'yz', 'xyz'], len(results))
                rotation_directions = np.random.choice([-1, 1], len(results))

            rotation_angle = frame * 0.01
            rotated_x = x_sphere.copy()
            rotated_y = y_sphere.copy()
            rotated_z = z_sphere.copy()

            for i in range(len(results)):
                if rotation_axes[i] == 'xy':
                    rotated_x[i] = x_sphere[i] * np.cos(rotation_angle * rotation_directions[i]) - y_sphere[i] * np.sin(rotation_angle * rotation_directions[i])
                    rotated_y[i] = x_sphere[i] * np.sin(rotation_angle * rotation_directions[i]) + y_sphere[i] * np.cos(rotation_angle * rotation_directions[i])
                elif rotation_axes[i] == 'xz':
                    rotated_x[i] = x_sphere[i] * np.cos(rotation_angle * rotation_directions[i]) - z_sphere[i] * np.sin(rotation_angle * rotation_directions[i])
                    rotated_z[i] = x_sphere[i] * np.sin(rotation_angle * rotation_directions[i]) + z_sphere[i] * np.cos(rotation_angle * rotation_directions[i])
                elif rotation_axes[i] == 'yz':
                    rotated_y[i] = y_sphere[i] * np.cos(rotation_angle * rotation_directions[i]) - z_sphere[i] * np.sin(rotation_angle * rotation_directions[i])
                    rotated_z[i] = y_sphere[i] * np.sin(rotation_angle * rotation_directions[i]) + z_sphere[i] * np.cos(rotation_angle * rotation_directions[i])
                elif rotation_axes[i] == 'xyz':
                    rotated_x[i] = x_sphere[i] * np.cos(rotation_angle * rotation_directions[i]) - y_sphere[i] * np.sin(rotation_angle * rotation_directions[i])
                    rotated_y[i] = x_sphere[i] * np.sin(rotation_angle * rotation_directions[i]) + y_sphere[i] * np.cos(rotation_angle * rotation_directions[i])
                    rotated_z[i] = z_sphere[i] * np.cos(rotation_angle * rotation_directions[i]) + y_sphere[i] * np.sin(rotation_angle * rotation_directions[i])

            oscillated_x = rotated_x + np.array([next(fp_gen) for fp_gen in fp_generators])
            oscillated_y = rotated_y + np.array([next(fp_gen) for fp_gen in fp_generators])
            oscillated_z = rotated_z + np.array([next(fp_gen) for fp_gen in fp_generators])

            colors = [colorsys.hsv_to_rgb(next(fp_gen) % 1, 1, 1) for fp_gen in fp_generators]
            scatter = ax.scatter(oscillated_x[:frame+1], oscillated_y[:frame+1], oscillated_z[:frame+1], c=colors[:frame+1], s=5, alpha=1.0)
            print(f"Processing frame {frame+1}/{len(results)}")

        ani = animation.FuncAnimation(fig, update, frames=len(results), interval=50, repeat=False)
        plt.tight_layout()
        try:
            ani.save(filename_animation, writer='pillow', fps=30)
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
    csv_file = os.path.join(script_dir, 'uncountable_infinity_test_results.csv')
    image_file_static = os.path.join(script_dir, 'uncountable_infinity_test_visualization.png')
    image_file_animation = os.path.join(script_dir, 'uncountable_infinity_test_animation.gif')
    results = test_uncountable_infinity(n_tests)
    save_results(results, csv_file)
    visualize_uncountable_infinity(results, image_file_static, image_file_animation)
    print("All tests and visualizations completed successfully.")

if __name__ == "__main__":
    main()

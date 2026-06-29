"""
Author: B. McCrackn
Email: thenothingnesseffect@gmail.com

Test Script for Pi Approximation Using Flowpoint

This script tests the accuracy of the Pi approximation function (`fp_pi`) 
implemented using the Flowpoint (fp) module. It evaluates the approximation 
over different iterations, plots the convergence, and saves results to 
CSV and visualization files.
"""

import os
import sys
import math
import unittest
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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

current_dir = os.path.dirname(os.path.abspath(__file__))

from equations.flowpoint_pi.fp_pi_approximation import fp_pi

class TestPiModel(unittest.TestCase):
    def setUp(self):
        self.iterations_list = [1000, 10000, 100000]

    def pi(self, max_iterations=100000):
        return fp_pi(max_iterations)

    def test_pi_approximation(self):
        results = []
        for iterations in self.iterations_list:
            pi_approx = self.pi(max_iterations=iterations)
            difference = abs(pi_approx - math.pi)
            print(f"Iterations: {iterations}")
            print(f"Approximated Pi: {pi_approx}, Actual Pi: {math.pi}")
            print(f"Difference: {difference}")
            results.append({
                'Iterations': iterations,
                'Approximated Pi': pi_approx,
                'Actual Pi': math.pi,
                'Difference': difference
            })
            if iterations >= 10000:
                self.assertTrue(difference < 1e-4, f"Pi approximation is inaccurate with {iterations} iterations")
        self._generate_plots(results)
        self._save_results_to_csv(results)

    def _generate_plots(self, results):
        iterations = [result['Iterations'] for result in results]
        differences = [result['Difference'] for result in results]
        approximations = [result['Approximated Pi'] for result in results]
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        ax1.plot(iterations, differences, marker='o', linestyle='-', color='#3498db', linewidth=2, markersize=8)
        ax1.set_ylabel('Absolute Difference from Actual Pi', fontsize=12, fontweight='bold')
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax2.plot(iterations, approximations, marker='o', linestyle='-', color='#f39c12', linewidth=2, markersize=8)
        ax2.axhline(y=math.pi, color='#e74c3c', linestyle='--', linewidth=2, label='Actual Pi')
        ax2.set_xlabel('Number of Iterations', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Approximated Pi Value', fontsize=12, fontweight='bold')
        ax2.grid(True, linestyle='--', alpha=0.7)
        plt.suptitle('Convergence of Pi Approximation', fontsize=16, fontweight='bold')
        plt.tight_layout()
        static_file_path = os.path.join(current_dir, 'pi_convergence_static.png')
        plt.savefig(static_file_path, dpi=300)
        print(f"Static plot saved to {static_file_path}")

        def animate(i):
            ax1.plot(iterations[:i+1], differences[:i+1], marker='o', linestyle='-', color='#3498db', linewidth=2, markersize=8)
            ax2.plot(iterations[:i+1], approximations[:i+1], marker='o', linestyle='-', color='#f39c12', linewidth=2, markersize=8)
        ani = animation.FuncAnimation(fig, animate, frames=len(iterations), interval=500)
        gif_file_path = os.path.join(current_dir, 'pi_convergence_animation.gif')
        ani.save(gif_file_path, writer='pillow', fps=2)
        plt.close()
        print(f"Animated GIF saved to {gif_file_path}")

    def _save_results_to_csv(self, results):
        csv_file = os.path.join(current_dir, 'pi_approx_results.csv')
        with open(csv_file, 'w', newline='') as csvfile:
            fieldnames = ['Iterations', 'Approximated Pi', 'Actual Pi', 'Difference']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        print(f"Results saved to {csv_file}")

if __name__ == '__main__':
    unittest.main()

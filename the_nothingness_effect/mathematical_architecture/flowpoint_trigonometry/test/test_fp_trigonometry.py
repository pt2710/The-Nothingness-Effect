"""
Author: B. McCrackn
Email: thenothingnesseffect@gmail.com
...
"""

import os
# --- Robust project root detection (adjust marker as needed)

import math
import json
import numpy as np
import unittest
import matplotlib.pyplot as plt

from the_nothingness_effect.mathematical_architecture.flowpoint_trigonometry.fp_trigonometry import FlowpointTrigonometry

class TestFlowpointTrigonometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fp_trig = FlowpointTrigonometry(smoothing_window=10)

    def setUp(self):
        self.fp_trig = self.__class__.fp_trig

    def test_osc_range(self):
        for _ in range(100):
            val_cos = self.fp_trig.cos(theta=0)
            val_sin = self.fp_trig.sin(theta=0)
            self.assertTrue(-1 <= val_cos <= 1, f"cos value {val_cos} is out of range [-1, 1]")
            self.assertTrue(-1 <= val_sin <= 1, f"sin value {val_sin} is out of range [-1, 1]")

    def test_cos_function(self):
        for theta in np.linspace(0, 2 * math.pi, 100):
            obtained = self.fp_trig.cos(theta)
            expected = math.cos(theta)
            self.assertAlmostEqual(obtained, expected, places=0, msg=f"Cos mismatch at θ={theta}")

    def test_sin_function(self):
        for theta in np.linspace(0, 2 * math.pi, 100):
            obtained = self.fp_trig.sin(theta)
            expected = math.sin(theta)
            self.assertAlmostEqual(obtained, expected, places=0, msg=f"Sin mismatch at θ={theta}")

    def test_tan_function(self):
        for theta in np.linspace(0, 2 * math.pi, 100):
            obtained = self.fp_trig.tan(theta)
            expected = math.tan(theta)
            if abs(obtained) > 1e10 or abs(expected) > 1e10:
                self.assertTrue((obtained > 0) == (expected > 0))
            else:
                self.assertAlmostEqual(obtained, expected, places=0, msg=f"Tangent mismatch at θ={theta}")

    def test_cos_sin_sum(self):
        for _ in range(1000):
            theta = np.random.uniform(0, 2 * math.pi)
            sum_val = self.fp_trig.cos_sin(theta)
            self.assertTrue(-2 <= sum_val <= 2, f"Sum of cos and sin {sum_val} is out of range [-2, 2]")

    def test_pi_approximation(self):
        pi_approx = self.fp_trig.pi(precision=1e-4, max_iterations=100000)
        self.assertAlmostEqual(pi_approx, math.pi, places=4, msg="Pi approximation is inaccurate")

    def test_trig_functions_over_cycle(self):
        theta_values = np.linspace(0, 2 * math.pi, 100)
        for theta in theta_values:
            expected_cos = math.cos(theta)
            obtained_cos = self.fp_trig.cos(theta)
            self.assertAlmostEqual(obtained_cos, expected_cos, places=1, msg=f"Cos mismatch at θ={theta}")

            expected_sin = math.sin(theta)
            obtained_sin = self.fp_trig.sin(theta)
            self.assertAlmostEqual(obtained_sin, expected_sin, places=1, msg=f"Sin mismatch at θ={theta}")

            if abs(expected_cos) < 1e-6:
                continue
            expected_tan = math.tan(theta)
            obtained_tan = self.fp_trig.tan(theta)
            if abs(obtained_tan) > 1e10 or abs(expected_tan) > 1e10:
                self.assertTrue((obtained_tan > 0) == (expected_tan > 0), f"Tangent sign mismatch at θ={theta}")
            else:
                self.assertAlmostEqual(obtained_tan, expected_tan, places=1, msg=f"Tangent mismatch at θ={theta}")

def save_test_data(test_results):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, 'test_results.json')
    with open(output_file, 'w') as f:
        json.dump(test_results, f, indent=4)
    print(f"Test results saved to {output_file}")

def plot_test_results(test_results, pi_value):
    cos_fp = np.array(test_results['cos_values'])
    sin_fp = np.array(test_results['sin_values'])
    tan_fp = np.array(test_results['tan_values'])
    cos_fp_raw = np.array(test_results['fp_cos_values'])
    sin_fp_raw = np.array(test_results['fp_sin_values'])
    tan_fp_raw = np.array(test_results['fp_tan_values'])
    theta_values = np.linspace(0, 2 * pi_value, 100)
    cos_std = np.cos(theta_values)
    sin_std = np.sin(theta_values)
    tan_std = np.tan(theta_values)
    valid_indices = ~np.isclose(cos_std, 0)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = 'fp_modelled_trigs_math_modelled_trigs_test_comparison.png'
    file_path = os.path.join(script_dir, filename)

    plt.figure(figsize=(12, 14))
    plt.subplot(3, 1, 1)
    plt.plot(theta_values, cos_std, label='Standard Cosine', linestyle='-', color='blue', linewidth=2)
    plt.plot(theta_values, cos_fp, label='Flowpoint Cosine', linestyle='--', color='yellow', linewidth=2)
    plt.plot(theta_values, cos_fp_raw, label='FP Cosine (Raw)', linestyle=':', color='red', linewidth=2)
    plt.title('Cosine Function Comparison')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.ylim(-1.5, 1.5)
    plt.subplot(3, 1, 2)
    plt.plot(theta_values, sin_std, label='Standard Sine', linestyle='-', color='blue', linewidth=2)
    plt.plot(theta_values, sin_fp, label='Flowpoint Sine', linestyle='--', color='yellow', linewidth=2)
    plt.plot(theta_values, sin_fp_raw, label='FP Sine (Raw)', linestyle=':', color='red', linewidth=2)
    plt.title('Sine Function Comparison')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.ylim(-1.5, 1.5)
    plt.subplot(3, 1, 3)
    plt.plot(theta_values[valid_indices], tan_std[valid_indices], label='Standard Tangent', linestyle='-', color='blue', linewidth=2)
    plt.plot(theta_values[valid_indices], tan_fp[valid_indices], label='Flowpoint Tangent', linestyle='--', color='yellow', linewidth=2)
    plt.plot(theta_values[valid_indices], tan_fp_raw[valid_indices], label='FP Tangent (Raw)', linestyle=':', color='red', linewidth=2)
    plt.title('Tangent Function Comparison')
    plt.ylim(-10, 10)
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(file_path)
    plt.show()
    print(f"Function comparison plot saved as '{filename}' in {script_dir}")

def plot_trig_functions(fp_trig):
    theta_values = np.linspace(0, 2 * math.pi, 1000)
    cos_fp = []
    sin_fp = []
    tan_fp = []
    cos_fp_raw = []
    sin_fp_raw = []
    tan_fp_raw = []
    cos_std = []
    sin_std = []
    tan_std = []
    for theta in theta_values:
        cos_val = fp_trig.cos(theta)
        sin_val = fp_trig.sin(theta)
        tan_val = fp_trig.tan(theta)
        h = 1.0
        x = math.cos(theta) * h
        y = math.sin(theta) * h
        fp_cos_val = fp_trig.fp_cos(x, h)
        fp_sin_val = fp_trig.fp_sin(y, h)
        fp_tan_val = fp_trig.fp_tan(y, x)
        cos_fp.append(cos_val)
        sin_fp.append(sin_val)
        tan_fp.append(tan_val)
        cos_fp_raw.append(fp_cos_val)
        sin_fp_raw.append(fp_sin_val)
        tan_fp_raw.append(fp_tan_val)
        cos_std.append(math.cos(theta))
        sin_std.append(math.sin(theta))
        tan_std.append(math.tan(theta))
    theta_values = np.array(theta_values)
    cos_std = np.array(cos_std)
    sin_std = np.array(sin_std)
    tan_std = np.array(tan_std)
    cos_fp = np.array(cos_fp)
    sin_fp = np.array(sin_fp)
    tan_fp = np.array(tan_fp)
    cos_fp_raw = np.array(cos_fp_raw)
    sin_fp_raw = np.array(sin_fp_raw)
    tan_fp_raw = np.array(tan_fp_raw)
    valid_indices = ~np.isclose(cos_std, 0)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = 'fp_modelled_trigs_math_modelled_trigs_comparison.png'
    file_path = os.path.join(script_dir, filename)
    plt.figure(figsize=(14, 14))
    plt.subplot(3, 1, 1)
    plt.plot(theta_values, cos_std, label='Standard Cosine', linestyle='-', color='blue', linewidth=2)
    plt.plot(theta_values, cos_fp, label='Flowpoint Cosine', linestyle='--', color='yellow', linewidth=2)
    plt.plot(theta_values, cos_fp_raw, label='FP Cosine (Raw)', linestyle=':', color='red', linewidth=2)
    plt.title('Cosine Function Comparison')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.ylim(-1.5, 1.5)
    plt.subplot(3, 1, 2)
    plt.plot(theta_values, sin_std, label='Standard Sine', linestyle='-', color='blue', linewidth=2)
    plt.plot(theta_values, sin_fp, label='Flowpoint Sine', linestyle='--', color='yellow', linewidth=2)
    plt.plot(theta_values, sin_fp_raw, label='FP Sine (Raw)', linestyle=':', color='red', linewidth=2)
    plt.title('Sine Function Comparison')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.ylim(-1.5, 1.5)
    plt.subplot(3, 1, 3)
    plt.plot(theta_values[valid_indices], tan_std[valid_indices], label='Standard Tangent', linestyle='-', color='blue', linewidth=2)
    plt.plot(theta_values[valid_indices], tan_fp[valid_indices], label='Flowpoint Tangent', linestyle='--', color='yellow', linewidth=2)
    plt.plot(theta_values[valid_indices], tan_fp_raw[valid_indices], label='FP Tangent (Raw)', linestyle=':', color='red', linewidth=2)
    plt.title('Tangent Function Comparison')
    plt.ylim(-10, 10)
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(file_path)
    plt.show()
    print(f"Function comparison plot saved as '{filename}' in {script_dir}")

if __name__ == "__main__":
    fp_trig = FlowpointTrigonometry(smoothing_window=10)
    pi_approx = fp_trig.pi(precision=1e-4, max_iterations=100000)
    print(f"Approximated Pi: {pi_approx}, Actual Pi: {math.pi}")
    print(f"Difference: {abs(pi_approx - math.pi)}")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFlowpointTrigonometry)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    test_theta = np.linspace(0, 2 * math.pi, 100)
    cos_values = []
    sin_values = []
    tan_values = []
    fp_cos_values = []
    fp_sin_values = []
    fp_tan_values = []
    for theta in test_theta:
        cos_val = fp_trig.cos(theta)
        sin_val = fp_trig.sin(theta)
        tan_val = fp_trig.tan(theta)
        h = 1.0
        x = math.cos(theta) * h
        y = math.sin(theta) * h
        fp_cos_val = fp_trig.fp_cos(x, h)
        fp_sin_val = fp_trig.fp_sin(y, h)
        fp_tan_val = fp_trig.fp_tan(y, x)
        cos_values.append(cos_val)
        sin_values.append(sin_val)
        tan_values.append(tan_val)
        fp_cos_values.append(fp_cos_val)
        fp_sin_values.append(fp_sin_val)
        fp_tan_values.append(fp_tan_val)
    test_results = {
        'cos_values': cos_values,
        'sin_values': sin_values,
        'tan_values': tan_values,
        'fp_cos_values': fp_cos_values,
        'fp_sin_values': fp_sin_values,
        'fp_tan_values': fp_tan_values,
    }
    save_test_data(test_results)
    plot_test_results(test_results, pi_approx)
    plot_trig_functions(fp_trig)

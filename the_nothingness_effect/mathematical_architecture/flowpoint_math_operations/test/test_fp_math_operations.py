"""
Author: B. McCrackn
Email: thenothingnesseffect@gmail.com

test_fp_math_operations.py

Unit tests for the FlowpointMath class, which implements mathematical operations based on the Flowpoint (fp)
function. The Flowpoint function embodies dynamic equilibrium and idempotence (i.e. fp(a) = fp(-a)), and
this test suite verifies that the operations derived from fp conform to the theoretical framework.

Usage:
    Run the tests using:
        python -m unittest test_fp_math_operations.py
"""

import os
import math
import csv
import unittest
import numpy as np
import matplotlib.pyplot as plt

# --- Robust project root detection (adjust marker as needed)
script_dir = os.path.dirname(os.path.abspath(__file__))

from the_nothingness_effect.mathematical_architecture.flowpoint_math_operations.fp_math_operations import FlowpointMath

class TestFlowpointMath(unittest.TestCase):
    def setUp(self):
        self.fp_math = FlowpointMath()
        self.results = []

    def test_fp_addition(self):
        a = 3
        b = 5
        result = self.fp_math.fp_addition(a, b)
        expected = a + b
        self.assertAlmostEqual(result, expected, places=5)
        self.results.append(['addition', a, b, result, expected])

    def test_fp_subtraction(self):
        a = 10
        b = 4
        result = self.fp_math.fp_subtraction(a, b)
        expected = a - b
        print(f"Subtraction test: a={a}, b={b}, result={result}, expected={expected}")
        self.assertAlmostEqual(result, expected, places=5)
        self.results.append(['subtraction', a, b, result, expected])

    def test_fp_multiplication(self):
        a = 2
        b = 7
        result = self.fp_math.fp_multiplication(a, b)
        expected = a * b
        self.assertAlmostEqual(result, expected, places=5)
        self.results.append(['multiplication', a, b, result, expected])

    def test_fp_division(self):
        a = 15
        b = 3
        result = self.fp_math.fp_division(a, b)
        expected = a / b
        self.assertAlmostEqual(result, expected, places=5)
        self.results.append(['division', a, b, result, expected])

    def test_fp_division_by_zero(self):
        a = 10
        b = 0
        with self.assertRaises(ZeroDivisionError):
            self.fp_math.fp_division(a, b)
        self.results.append(['division_by_zero', a, b, 'Error', 'Error'])

    def test_fp_exponentiation(self):
        a = 4
        n = 2
        result = self.fp_math.fp_exponentiation(a, n)
        expected = a ** n
        self.assertAlmostEqual(result, expected, places=5)
        self.results.append(['exponentiation', a, n, result, expected])

    def test_fp_square_root(self):
        a = 16
        result = self.fp_math.fp_square_root(a)
        expected = math.sqrt(a)
        self.assertAlmostEqual(result, expected, places=5)
        self.results.append(['square_root', a, None, result, expected])

    def test_fp_square_root_negative(self):
        a = -9
        with self.assertRaises(ValueError):
            self.fp_math.fp_square_root(a)
        self.results.append(['square_root_negative', a, None, 'Error', 'Error'])

    def test_fp_value_oscillation(self):
        a = 5
        fp_a_first = self.fp_math.fp_value(a)
        fp_a_second = self.fp_math.fp_value(a)
        self.assertEqual(fp_a_first, a)
        self.assertEqual(fp_a_second, -a)
        self.results.append(['value_oscillation_first', a, None, fp_a_first, a])
        self.results.append(['value_oscillation_second', a, None, fp_a_second, -a])

    def test_fp_zero_input(self):
        a = 0
        b = 0
        addition_result = self.fp_math.fp_addition(a, b)
        self.assertEqual(addition_result, 0)
        self.results.append(['zero_input', a, b, addition_result, 0])

    def test_fp_negative_inputs(self):
        a = -3
        b = -7
        result = self.fp_math.fp_multiplication(a, b)
        expected = a * b
        self.assertAlmostEqual(result, expected, places=5)
        self.results.append(['negative_inputs', a, b, result, expected])

    def test_fp_sin(self):
        a = math.pi / 6
        result = self.fp_math.fp_sin(a)
        expected = math.sin(a)
        self.assertAlmostEqual(result, expected, places=5)
        self.results.append(['sin', a, None, result, expected])

    def test_fp_cos(self):
        a = math.pi / 3
        result = self.fp_math.fp_cos(a)
        expected = math.cos(a)
        self.assertAlmostEqual(result, expected, places=5)
        self.results.append(['cos', a, None, result, expected])

    def test_fp_tan(self):
        a = math.pi / 4
        result = self.fp_math.fp_tan(a)
        expected = math.tan(a)
        self.assertAlmostEqual(result, expected, places=5)
        self.results.append(['tan', a, None, result, expected])

    def tearDown(self):
        test_name = self._testMethodName
        self.save_results(test_name)
        self.visualize_results(test_name)

    def save_results(self, test_name):
        csv_file_path = os.path.join(script_dir, f'{test_name}_results.csv')
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Operation', 'Input1', 'Input2', 'Result', 'Expected'])
            writer.writerows(self.results)
        print(f"Results for {test_name} saved to {csv_file_path}")

    def visualize_results(self, test_name):
        if not self.results:
            print("No results to visualize.")
            return
        operations = set(row[0] for row in self.results)
        for op in operations:
            op_results = [row for row in self.results if row[0] == op]
            if len(op_results) < 1:
                print(f"Not enough data to visualize for operation: {op}")
                continue
            x = np.array([row[1] for row in op_results])
            y1 = np.array([float(row[3]) if row[3] != 'Error' else np.nan for row in op_results])
            y2 = np.array([float(row[4]) if row[4] != 'Error' else np.nan for row in op_results])
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
            ax1.plot(x, y1, 'bo-', label='Flowpoint Result')
            ax1.plot(x, y2, 'r--', label='Expected Result')
            ax1.set_title(f'{op.capitalize()} ({test_name}): Flowpoint vs Expected')
            ax1.set_xlabel('Input (a)')
            ax1.set_ylabel('Result')
            ax1.legend()
            ax1.grid(True)
            for i, row in enumerate(op_results):
                a = row[1]
                b = row[2]
                annotation = f"a={a}" + (f", b={b}" if b is not None else "")
                ax1.annotate(annotation, (a, y1[i]),
                             textcoords="offset points", xytext=(0, 10),
                             ha='center', fontsize=8, color='purple')
            difference = np.abs(y1 - y2)
            ax2.plot(x, difference, 'g^-')
            ax2.set_title(f'{op.capitalize()} ({test_name}): Absolute Difference')
            ax2.set_xlabel('Input (a)')
            ax2.set_ylabel('Absolute Difference')
            ax2.grid(True)
            for i, row in enumerate(op_results):
                a = row[1]
                b = row[2]
                annotation = f"a={a}" + (f", b={b}" if b is not None else "")
                ax2.annotate(annotation, (a, difference[i]),
                             textcoords="offset points", xytext=(0, 10),
                             ha='center', fontsize=8, color='purple')
            plt.tight_layout()
            image_file_path = os.path.join(script_dir, f'{test_name}_{op}_visualization.png')
            plt.savefig(image_file_path)
            plt.close()
            print(f"Visualization for {op} in {test_name} saved to {image_file_path}")

if __name__ == '__main__':
    unittest.main()

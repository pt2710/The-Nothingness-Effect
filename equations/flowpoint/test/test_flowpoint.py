"""
Author: B. McCrackn
Email: thenothingnesseffect@gmail.com

Nothingness Effect Test Script
------------------------------

This test script validates and visualizes the implementation of the Flowpoint (fp) function,
a central concept in *The Nothingness Effect* theory. The Flowpoint function oscillates between
a value and its negation, thereby exemplifying the system's dynamic equilibrium. This script performs:

1. Static Testing (plot + CSV)
2. Dynamic Animation (GIF)
3. Unit Testing (with results as CSV)
"""

import os
import sys
import unittest
import matplotlib.pyplot as plt

DEBUG = True

def debug(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

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

from equations.flowpoint.flowpoint import fp

script_dir = os.path.dirname(os.path.abspath(__file__))

def test_fp():
    print("Testing fp:")
    flowpoint = fp(1.0)
    values = [next(flowpoint) for _ in range(100)]
    plt.figure(figsize=(10, 6))
    plt.plot(values, marker='o')
    plt.title("Test Flowpoint (fp) Oscillation")
    plt.xlabel("Iteration")
    plt.ylabel("Value")
    plt.grid(True)
    osc_plot_path = os.path.join(script_dir, "test_fp_oscillation.png")
    plt.savefig(osc_plot_path)
    plt.close()
    print(f"Flowpoint oscillation visualized and saved as '{osc_plot_path}'")
    if os.path.exists(osc_plot_path):
        debug(f"Verified: {osc_plot_path} exists.")
    else:
        debug(f"Error: {osc_plot_path} was not created.")
    csv_path = os.path.join(script_dir, "test_fp_results.csv")
    import csv
    with open(csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Iteration", "Value"])
        for i, value in enumerate(values):
            writer.writerow([i, value])
    print(f"Flowpoint results saved as CSV in '{csv_path}'")
    if os.path.exists(csv_path):
        debug(f"Verified: {csv_path} exists.")
    else:
        debug(f"Error: {csv_path} was not created.")
    print("Static test completed successfully.")

def animate_fp():
    import matplotlib.animation as animation
    from matplotlib.animation import PillowWriter
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 100)
    ax.set_ylim(-1.5, 1.5)
    line, = ax.plot([], [], 'o-', lw=2)
    ax.set_title("Dynamic Test Flowpoint Simulation")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Value")
    ax.grid(True)
    data = []
    fp_gen = fp(1.0)
    def init():
        line.set_data([], [])
        return line,
    def update(frame):
        data.append(next(fp_gen))
        xdata = list(range(len(data)))
        line.set_data(xdata, data)
        return line,
    ani = animation.FuncAnimation(
        fig, update, frames=range(100), init_func=init, blit=True, interval=50, repeat=False
    )
    gif_path = os.path.join(script_dir, "test_fp_animation.gif")
    writer = PillowWriter(fps=20)
    ani.save(gif_path, writer=writer)
    print(f"Dynamic gif of test simulation saved as '{gif_path}'")
    if os.path.exists(gif_path):
        debug(f"Verified: {gif_path} exists.")
    else:
        debug(f"Error: {gif_path} was not created.")
    plt.show()
    print("Animation completed successfully.")

class CsvTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_results = []
    def addSuccess(self, test):
        super().addSuccess(test)
        self.test_results.append({"test": str(test), "status": "PASS", "message": ""})
    def addError(self, test, err):
        super().addError(test, err)
        self.test_results.append({"test": str(test), "status": "ERROR", "message": self._exc_info_to_string(err, test)})
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.test_results.append({"test": str(test), "status": "FAIL", "message": self._exc_info_to_string(err, test)})

class TestFlowpointOscillation(unittest.TestCase):
    def test_alternating_pattern(self):
        flowpoint = fp(1.0)
        for _ in range(5):
            a = next(flowpoint)
            b = next(flowpoint)
            self.assertEqual(b, -a, f"Expected {b} to be the negation of {a}")
        debug("Unit test 'test_alternating_pattern' passed.")

def run_unit_tests():
    debug("Running unit tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFlowpointOscillation)
    runner = unittest.TextTestRunner(resultclass=CsvTestResult, verbosity=2)
    result = runner.run(suite)
    csv_path = os.path.join(script_dir, "unittest_results.csv")
    import csv
    with open(csv_path, mode='w', newline='') as csvfile:
        fieldnames = ["Test Name", "Status", "Message"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for test_result in result.test_results:
            writer.writerow({
                "Test Name": test_result["test"],
                "Status": test_result["status"],
                "Message": test_result["message"]
            })
    print(f"Unit test results saved as CSV in '{csv_path}'")
    if not result.wasSuccessful():
        print("Unit tests failed!")
        sys.exit(1)
    else:
        debug("All unit tests passed successfully.")

def main():
    test_fp()
    run_unit_tests()
    animate_fp()
    print("All tests completed successfully.")

if __name__ == "__main__":
    main()

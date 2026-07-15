"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

simulate_fp_math_operations.py

This script simulates various mathematical operations using the Flowpoint function (fp). The Flowpoint 
function embodies dynamic equilibrium and idempotence (i.e. fp(a) = fp(-a)), which forms the basis for 
the derivation of operations such as addition, subtraction, multiplication, division, exponentiation, 
square root, and trigonometric functions (sine, cosine, tangent).

For each operation, the script computes both the Flowpoint-based result and the standard (classical) 
result. It then saves the computed results as CSV files, generates plots comparing the Flowpoint results 
against the standard results, and creates animations that visually illustrate the evolution of these values 
across a range of inputs.

Usage:
    Run the script to compute the results, generate plots/animations, and save CSV data in the same directory.
    Example:
        python simulate_fp_math_operations.py
"""

import os
import sys
import time
import math
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from fp_math_operations import FlowpointMath

# Set up the parent directory so that the 'FlowpointMath' class is accessible.
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Directory where this simulation script is located.
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define input arrays for simulation:
# For binary operations, we vary the first operand over a range (a_values) while keeping the second operand constant.
a_values = np.linspace(0, 10, 400)
b_addition       = 5
b_subtraction    = 5
b_multiplication = 7
b_division       = 3

# For operations like square root and division, inputs must be nonnegative.
a_values_nonneg = np.linspace(0, 10, 400)

def estimate_time_remaining(start_time, current_index, total_items):
    """
    Estimates the remaining time for a loop based on the elapsed time and current progress.

    Parameters:
        start_time (float): The time at which the loop started.
        current_index (int): The current iteration index.
        total_items (int): The total number of iterations.

    Returns:
        float: Estimated remaining time in seconds.
    """
    elapsed_time = time.time() - start_time
    if current_index == 0:
        return float('inf')
    estimated_total_time = elapsed_time * (total_items / current_index)
    remaining_time = estimated_total_time - elapsed_time
    return remaining_time

def compute_results():
    """
    Computes both Flowpoint-based and standard arithmetic results for various operations:
        - Addition, Subtraction, Multiplication, Exponentiation
        - Square Root, Division
        - Trigonometric functions: Sine, Cosine, Tangent

    For each operation, the function computes the result for each value in the input range and 
    stores both the Flowpoint (fp) result and the standard (std) result in separate numpy arrays.

    Returns:
        dict: A dictionary containing numpy arrays for each operation's Flowpoint and standard results.
    """
    # Initialize numpy arrays to hold the computed results for each operation.
    addition_results       = np.zeros_like(a_values)
    subtraction_results    = np.zeros_like(a_values)
    multiplication_results = np.zeros_like(a_values)
    exponentiation_results = np.zeros_like(a_values)
    square_root_results    = np.zeros_like(a_values_nonneg)
    division_results       = np.zeros_like(a_values_nonneg)

    # Arrays for trigonometric operations (computed over a_values).
    sin_results_fp = np.zeros_like(a_values)
    cos_results_fp = np.zeros_like(a_values)
    tan_results_fp = np.zeros_like(a_values)
    sin_results_std = np.zeros_like(a_values)
    cos_results_std = np.zeros_like(a_values)
    tan_results_std = np.zeros_like(a_values)

    # Standard (classical) results for comparison.
    standard_addition       = np.zeros_like(a_values)
    standard_subtraction    = np.zeros_like(a_values)
    standard_multiplication = np.zeros_like(a_values)
    standard_exponentiation = np.zeros_like(a_values)
    standard_square_root    = np.zeros_like(a_values_nonneg)
    standard_division       = np.zeros_like(a_values_nonneg)
    standard_sin = np.zeros_like(a_values)
    standard_cos = np.zeros_like(a_values)
    standard_tan = np.zeros_like(a_values)

    # Compute results for operations defined over a_values.
    start_time_ops = time.time()
    total_ops = len(a_values)
    for i, a in enumerate(a_values):
        # Create a new FlowpointMath instance for each iteration.
        fp_math = FlowpointMath()

        # Addition: fp_addition(a, b_addition)
        addition_results[i] = fp_math.fp_addition(a, b_addition)
        standard_addition[i] = a + b_addition

        # Subtraction: fp_subtraction(a, b_subtraction)
        # Note: Standard subtraction is defined here as b_subtraction - a to match the original implementation.
        subtraction_results[i] = fp_math.fp_subtraction(a, b_subtraction)
        standard_subtraction[i] = b_subtraction - a

        # Multiplication: fp_multiplication(a, b_multiplication)
        multiplication_results[i] = fp_math.fp_multiplication(a, b_multiplication)
        standard_multiplication[i] = a * b_multiplication

        # Exponentiation: fp_exponentiation(a, 2)
        exponentiation_results[i] = fp_math.fp_exponentiation(a, 2)
        standard_exponentiation[i] = a ** 2

        # Trigonometric functions:
        sin_results_fp[i] = fp_math.fp_sin(a)
        cos_results_fp[i] = fp_math.fp_cos(a)
        tan_results_fp[i] = fp_math.fp_tan(a)
        standard_sin[i] = math.sin(a)
        standard_cos[i] = math.cos(a)
        standard_tan[i] = math.tan(a)

        # Print progress every 50 iterations.
        if i % 50 == 0 or i == total_ops - 1:
            progress = (i + 1) / total_ops * 100
            remaining = estimate_time_remaining(start_time_ops, i + 1, total_ops)
            print(f"Computing (add/sub/mul/exp/trig): {progress:.2f}% complete. "
                  f"Estimated time remaining: {remaining:.2f} sec", end='\r')

    # Compute results for operations defined over a_values_nonneg.
    start_time_sqrt = time.time()
    total_sqrt = len(a_values_nonneg)
    for i, a in enumerate(a_values_nonneg):
        fp_math = FlowpointMath()
        # Square Root: fp_square_root(a)
        try:
            square_root_results[i] = fp_math.fp_square_root(a)
        except ValueError:
            square_root_results[i] = np.nan
        standard_square_root[i] = math.sqrt(a) if a >= 0 else np.nan

        # Division: fp_division(a, b_division)
        try:
            division_results[i] = fp_math.fp_division(a, b_division)
        except ZeroDivisionError:
            division_results[i] = np.nan
        standard_division[i] = a / b_division if b_division != 0 else np.nan

        # Print progress every 50 iterations.
        if i % 50 == 0 or i == total_sqrt - 1:
            progress = (i + 1) / total_sqrt * 100
            remaining = estimate_time_remaining(start_time_sqrt, i + 1, total_sqrt)
            print(f"Computing (sqrt/div): {progress:.2f}% complete. "
                  f"Estimated time remaining: {remaining:.2f} sec", end='\r')

    # Return a dictionary of results for further processing (e.g., saving CSV, plotting, animation).
    return {
        'addition_fp': addition_results,
        'addition_std': standard_addition,
        'subtraction_fp': subtraction_results,
        'subtraction_std': standard_subtraction,
        'multiplication_fp': multiplication_results,
        'multiplication_std': standard_multiplication,
        'exponentiation_fp': exponentiation_results,
        'exponentiation_std': standard_exponentiation,
        'square_root_fp': square_root_results,
        'square_root_std': standard_square_root,
        'division_fp': division_results,
        'division_std': standard_division,
        'sin_fp': sin_results_fp,
        'sin_std': standard_sin,
        'cos_fp': cos_results_fp,
        'cos_std': standard_cos,
        'tan_fp': tan_results_fp,
        'tan_std': standard_tan
    }

def save_results_csv_per_op(results):
    """
    Saves the simulation results to separate CSV files (one file per operation) in the script directory.
    Each CSV file includes columns: Input, FP_Result, Standard_Result.
    For operations computed over a_values, the input is taken from a_values.
    For square root and division, the input is taken from a_values_nonneg.
    """
    # Define the mapping between operation keys and their corresponding input arrays.
    operations = {
        'addition': {
            'inputs': a_values,
            'fp_key': 'addition_fp',
            'std_key': 'addition_std'
        },
        'subtraction': {
            'inputs': a_values,
            'fp_key': 'subtraction_fp',
            'std_key': 'subtraction_std'
        },
        'multiplication': {
            'inputs': a_values,
            'fp_key': 'multiplication_fp',
            'std_key': 'multiplication_std'
        },
        'exponentiation': {
            'inputs': a_values,
            'fp_key': 'exponentiation_fp',
            'std_key': 'exponentiation_std'
        },
        'square_root': {
            'inputs': a_values_nonneg,
            'fp_key': 'square_root_fp',
            'std_key': 'square_root_std'
        },
        'division': {
            'inputs': a_values_nonneg,
            'fp_key': 'division_fp',
            'std_key': 'division_std'
        },
        'sin': {
            'inputs': a_values,
            'fp_key': 'sin_fp',
            'std_key': 'sin_std'
        },
        'cos': {
            'inputs': a_values,
            'fp_key': 'cos_fp',
            'std_key': 'cos_std'
        },
        'tan': {
            'inputs': a_values,
            'fp_key': 'tan_fp',
            'std_key': 'tan_std'
        }
    }

    # Save a separate CSV file for each operation.
    for op, mapping in operations.items():
        filename = f"{op}_results.csv"
        filepath = os.path.join(script_dir, filename)
        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Input", "FP_Result", "Standard_Result"])
            inputs = mapping['inputs']
            fp_vals = results[mapping['fp_key']]
            std_vals = results[mapping['std_key']]
            for x, fp_val, std_val in zip(inputs, fp_vals, std_vals):
                writer.writerow([x, fp_val, std_val])
        print(f"CSV results for {op} saved: {filepath}")

def save_plot(fig, filename):
    """
    Saves the given figure as an image file (PNG) in the script directory.
    If a file with the same name exists, the function skips saving the figure.
    
    Parameters:
        fig (matplotlib.figure.Figure): The figure object to save.
        filename (str): The desired filename for the saved plot.
    """
    filepath = os.path.join(script_dir, filename)
    if os.path.exists(filepath):
        print(f"Plot {filepath} already exists, skipping.")
        plt.close(fig)
    else:
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Plot saved: {filepath}")

def create_animation(x_values, fp_results, standard_results,
                     title, xlabel, ylabel, fp_label, standard_label, filename=None):
    """
    Creates an animation comparing the Flowpoint-based results and the standard results over time.

    Parameters:
        x_values (array-like): The input values for the x-axis.
        fp_results (array-like): The Flowpoint-based results.
        standard_results (array-like): The standard results.
        title (str): The title for the plot.
        xlabel (str): The x-axis label.
        ylabel (str): The y-axis label.
        fp_label (str): Label for the Flowpoint curve.
        standard_label (str): Label for the standard curve.
        filename (str, optional): The filename for saving the animation. If provided and the file exists,
                                  saving is skipped; otherwise, the animation is saved using Pillow.

    Returns:
        If filename is not provided, returns the FuncAnimation object.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    total_frames = len(x_values)
    start_time_anim = time.time()

    def animate(i):
        ax.clear()
        ax.plot(x_values[:i], fp_results[:i], label=fp_label)
        ax.plot(x_values[:i], standard_results[:i], '--', label=standard_label)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        ax.grid(True)
        if filename is not None and (i % 50 == 0 or i == total_frames - 1):
            progress = (i + 1) / total_frames * 100
            elapsed = time.time() - start_time_anim
            est_total = elapsed * total_frames / (i + 1)
            remain = est_total - elapsed
            print(f"Animation '{filename}': {progress:.2f}% complete. "
                  f"Estimated time remaining: {remain:.2f} sec", end='\r')

    ani = animation.FuncAnimation(fig, animate, frames=total_frames,
                                  interval=50, repeat=False)

    if filename is not None:
        anim_path = os.path.join(script_dir, filename)
        if os.path.exists(anim_path):
            print(f"Animation {anim_path} already exists, skipping.")
        else:
            print(f"\nSaving animation '{filename}'...")
            ani.save(anim_path, writer='pillow')
            print(f"Animation saved: {anim_path}")
    else:
        return ani

def plot_and_animate_results(results):
    """
    Generates plots and animations for each operation using the computed results.

    The function creates visual comparisons (plots and animations) for:
        - Addition, Subtraction, Multiplication, Exponentiation
        - Square Root, Division
        - Trigonometric functions: Sine, Cosine, Tangent

    Each plot is saved as a PNG image and an accompanying animation is saved as a GIF.
    """
    # Unpack results for brevity.
    addition_fp    = results['addition_fp']
    addition_std   = results['addition_std']
    subtraction_fp = results['subtraction_fp']
    subtraction_std= results['subtraction_std']
    multiplication_fp = results['multiplication_fp']
    multiplication_std= results['multiplication_std']
    exponentiation_fp = results['exponentiation_fp']
    exponentiation_std= results['exponentiation_std']
    square_root_fp = results['square_root_fp']
    square_root_std= results['square_root_std']
    division_fp    = results['division_fp']
    division_std   = results['division_std']
    sin_fp = results['sin_fp']
    sin_std = results['sin_std']
    cos_fp = results['cos_fp']
    cos_std = results['cos_std']
    tan_fp = results['tan_fp']
    tan_std = results['tan_std']

    # 1) Addition
    fig = plt.figure(figsize=(10, 6))
    plt.plot(a_values, addition_fp, label='fp_addition(a, 5)', color='blue')
    plt.plot(a_values, addition_std, '--', label='a + 5', color='orange')
    plt.xlabel('a')
    plt.ylabel('Addition Result')
    plt.title('Addition: Flowpoint vs Standard')
    plt.legend()
    plt.grid(True)
    save_plot(fig, 'addition_plot.png')
    create_animation(a_values, addition_fp, addition_std,
                     'Addition: Flowpoint vs Standard', 'a', 'Result',
                     'fp_addition(a, 5)', 'a + 5', 'addition_animation.gif')

    # 2) Subtraction
    fig = plt.figure(figsize=(10, 6))
    plt.plot(a_values, subtraction_fp, label='fp_subtraction(a, 5)', color='blue')
    plt.plot(a_values, subtraction_std, '--', label='a - 5', color='orange')
    plt.xlabel('a')
    plt.ylabel('Subtraction Result')
    plt.title('Subtraction: Flowpoint vs Standard')
    plt.legend()
    plt.grid(True)
    save_plot(fig, 'subtraction_plot.png')
    create_animation(a_values, subtraction_fp, subtraction_std,
                     'Subtraction: Flowpoint vs Standard', 'a', 'Result',
                     'fp_subtraction(a, 5)', 'a - 5', 'subtraction_animation.gif')

    # 3) Multiplication
    fig = plt.figure(figsize=(10, 6))
    plt.plot(a_values, multiplication_fp, label='fp_multiplication(a, 7)', color='blue')
    plt.plot(a_values, multiplication_std, '--', label='a * 7', color='orange')
    plt.xlabel('a')
    plt.ylabel('Multiplication Result')
    plt.title('Multiplication: Flowpoint vs Standard')
    plt.legend()
    plt.grid(True)
    save_plot(fig, 'multiplication_plot.png')
    create_animation(a_values, multiplication_fp, multiplication_std,
                     'Multiplication: Flowpoint vs Standard', 'a', 'Result',
                     'fp_multiplication(a, 7)', 'a * 7', 'multiplication_animation.gif')

    # 4) Exponentiation
    fig = plt.figure(figsize=(10, 6))
    plt.plot(a_values, exponentiation_fp, label='fp_exponentiation(a, 2)', color='blue')
    plt.plot(a_values, exponentiation_std, '--', label='a^2', color='orange')
    plt.xlabel('a')
    plt.ylabel('Exponentiation Result')
    plt.title('Exponentiation: Flowpoint vs Standard')
    plt.legend()
    plt.grid(True)
    save_plot(fig, 'exponentiation_plot.png')
    create_animation(a_values, exponentiation_fp, exponentiation_std,
                     'Exponentiation: Flowpoint vs Standard', 'a', 'Result',
                     'fp_exponentiation(a, 2)', 'a^2', 'exponentiation_animation.gif')

    # 5) Square Root
    fig = plt.figure(figsize=(10, 6))
    plt.plot(a_values_nonneg, square_root_fp, label='fp_square_root(a)', color='blue')
    plt.plot(a_values_nonneg, square_root_std, '--', label='sqrt(a)', color='orange')
    plt.xlabel('a')
    plt.ylabel('Square Root Result')
    plt.title('Square Root: Flowpoint vs Standard')
    plt.legend()
    plt.grid(True)
    save_plot(fig, 'square_root_plot.png')
    create_animation(a_values_nonneg, square_root_fp, square_root_std,
                     'Square Root: Flowpoint vs Standard', 'a', 'Result',
                     'fp_square_root(a)', 'sqrt(a)', 'square_root_animation.gif')

    # 6) Division
    fig = plt.figure(figsize=(10, 6))
    plt.plot(a_values_nonneg, division_fp, label='fp_division(a, 3)', color='blue')
    plt.plot(a_values_nonneg, division_std, '--', label='a / 3', color='orange')
    plt.xlabel('a')
    plt.ylabel('Division Result')
    plt.title('Division: Flowpoint vs Standard')
    plt.legend()
    plt.grid(True)
    save_plot(fig, 'division_plot.png')
    create_animation(a_values_nonneg, division_fp, division_std,
                     'Division: Flowpoint vs Standard', 'a', 'Result',
                     'fp_division(a, 3)', 'a / 3', 'division_animation.gif')

    # 7) Sine
    fig = plt.figure(figsize=(10, 6))
    plt.plot(a_values, sin_fp, label='fp_sin(a)', color='blue')
    plt.plot(a_values, sin_std, '--', label='sin(a)', color='orange')
    plt.xlabel('a')
    plt.ylabel('Sine Result')
    plt.title('Sine: Flowpoint vs Standard')
    plt.legend()
    plt.grid(True)
    save_plot(fig, 'sin_plot.png')
    create_animation(a_values, sin_fp, sin_std,
                     'Sine: Flowpoint vs Standard', 'a', 'Result',
                     'fp_sin(a)', 'sin(a)', 'sin_animation.gif')

    # 8) Cosine
    fig = plt.figure(figsize=(10, 6))
    plt.plot(a_values, cos_fp, label='fp_cos(a)', color='blue')
    plt.plot(a_values, cos_std, '--', label='cos(a)', color='orange')
    plt.xlabel('a')
    plt.ylabel('Cosine Result')
    plt.title('Cosine: Flowpoint vs Standard')
    plt.legend()
    plt.grid(True)
    save_plot(fig, 'cos_plot.png')
    create_animation(a_values, cos_fp, cos_std,
                     'Cosine: Flowpoint vs Standard', 'a', 'Result',
                     'fp_cos(a)', 'cos(a)', 'cos_animation.gif')

    # 9) Tangent
    fig = plt.figure(figsize=(10, 6))
    plt.plot(a_values, tan_fp, label='fp_tan(a)', color='blue')
    plt.plot(a_values, tan_std, '--', label='tan(a)', color='orange')
    plt.xlabel('a')
    plt.ylabel('Tangent Result')
    plt.title('Tangent: Flowpoint vs Standard')
    plt.legend()
    plt.grid(True)
    save_plot(fig, 'tan_plot.png')
    create_animation(a_values, tan_fp, tan_std,
                     'Tangent: Flowpoint vs Standard', 'a', 'Result',
                     'fp_tan(a)', 'tan(a)', 'tan_animation.gif')

def main():
    """
    Main entry point for the simulation.
    
    This function performs the following steps:
        1. Computes the results for all operations using the FlowpointMath class.
        2. Generates plots and animations for each operation.
        3. Saves the computed results to CSV files.
    """
    print("Starting computations...")
    results = compute_results()
    print("\nComputations complete. Generating plots and animations...")
    plot_and_animate_results(results)
    print("Saving CSV results for each operation...")
    save_results_csv_per_op(results)
    print("All plots, animations, and CSV results have been saved in the same directory as this script.")

if __name__ == "__main__":
    main()

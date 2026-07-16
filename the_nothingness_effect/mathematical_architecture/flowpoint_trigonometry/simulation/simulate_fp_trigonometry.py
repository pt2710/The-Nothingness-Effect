"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

This script simulates and visualizes the modeling of trigonometric functions using the Flowpoint function,
including a dynamic 3D animation.

Goals:
1. Generate data for Flowpoint-based trigonometric functions
2. Compare Flowpoint-based models with standard trigonometric functions
3. Save simulation data for future analysis
4. Generate visualizations for easy interpretation of results
5. Create a dynamic 3D animation of the trigonometric functions

Success criteria:
1. The script runs without errors
2. Saved data shows the unique oscillatory behavior of Flowpoint functions
3. Visualizations clearly show the rapid oscillations of Flowpoint functions within the bounds of standard trigonometric functions
4. The 3D animation is visually appealing and informative
5. Process time and estimated time remaining are displayed in the terminal
6. Memory usage is optimized by avoiding unnecessary frame storage
"""

import os
import time
from datetime import timedelta
import math
import json
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Adjust the import path to locate FlowpointTrigonometry
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from the_nothingness_effect.mathematical_architecture.flowpoint_trigonometry.fp_trigonometry import FlowpointTrigonometry  # Adjust import as needed

def calculate_trigonometry(theta, fp_trig):
    x = math.cos(theta)
    y = math.sin(theta)
    h = 1.0  # Use h = 1.0 for simplicity
    # Calculate Flowpoint-based trigonometric values
    cos_fp_val = fp_trig.fp_cos(x, h)
    sin_fp_val = fp_trig.fp_sin(y, h)
    tan_fp_val = fp_trig.fp_tan(y, x)
    xy_fp_val = cos_fp_val + sin_fp_val
    return cos_fp_val, sin_fp_val, tan_fp_val, xy_fp_val

def generate_data(theta_values, fp_trig):
    """
    Generates Flowpoint-based trigonometric data.
    """
    cos_fp = []
    sin_fp = []
    tan_fp = []
    xy_fp = []

    start_time = time.time()
    total = len(theta_values)
    for i, theta in enumerate(theta_values):
        cos_fp_val, sin_fp_val, tan_fp_val, xy_fp_val = calculate_trigonometry(theta, fp_trig)
        cos_fp.append(cos_fp_val)
        sin_fp.append(sin_fp_val)
        tan_fp.append(tan_fp_val)
        xy_fp.append(xy_fp_val)

        # Progress reporting
        if (i + 1) % 1000 == 0 or (i + 1) == total:
            elapsed_time = time.time() - start_time
            progress = (i + 1) / total
            estimated_total_time = elapsed_time / progress
            estimated_time_remaining = estimated_total_time - elapsed_time
            print(f"\rProgress: {progress * 100:.2f}% | Elapsed: {timedelta(seconds=int(elapsed_time))} | Estimated remaining: {timedelta(seconds=int(estimated_time_remaining))}", end='')

    print()
    return cos_fp, sin_fp, tan_fp, xy_fp

def simulate_trigonometry():
    """
    Simulates and visualizes the modeling of trigonometric functions using the Flowpoint function.

    This function:
    1. Generates theta values from 0 to 20π (10 periods)
    2. Calculates standard trigonometric function values
    3. Uses the FlowpointTrigonometry class to calculate corresponding values
    4. Creates four plots comparing standard and Flowpoint-based functions
    5. Saves the simulation data to a JSON file
    6. Saves the visualizations as HTML and PNG files
    7. Creates a dynamic 3D animation of the trigonometric functions

    Returns:
    None
    """
    start_time = time.time()
    print("Simulation started. Estimated time may vary based on system performance.")

    fp_trig = FlowpointTrigonometry()
    
    # Use 10 periods (0 to 20π)
    theta_values = np.linspace(0, 20 * np.pi, 10000)
    
    # Standard trigonometric functions
    cos_std = np.cos(theta_values)
    sin_std = np.sin(theta_values)
    tan_std = np.tan(theta_values)
    xy_std = cos_std + sin_std
    
    # Generate Flowpoint-based trigonometric functions
    cos_fp, sin_fp, tan_fp, xy_fp = generate_data(theta_values, fp_trig)
    
    # Save simulation data
    simulation_data = {
        'theta_values': theta_values.tolist(),
        'cos_std': cos_std.tolist(),
        'sin_std': sin_std.tolist(),
        'tan_std': tan_std.tolist(),
        'xy_std': xy_std.tolist(),
        'cos_fp': cos_fp,
        'sin_fp': sin_fp,
        'tan_fp': tan_fp,
        'xy_fp': xy_fp
    }
    save_simulation_data(simulation_data)
    
    # Create plots
    save_visualization_plotly(theta_values, cos_std, cos_fp, 'Cosine Function', 'cosine_plot')
    save_visualization_plotly(theta_values, sin_std, sin_fp, 'Sine Function', 'sine_plot')
    save_visualization_plotly(theta_values, tan_std, tan_fp, 'Tangent Function', 'tangent_plot')
    save_visualization_plotly(theta_values, xy_std, xy_fp, 'Sum of Cosine and Sine', 'cos_plus_sin_plot', deviations=True)
    
    # Create 3D animation
    create_3d_animation(theta_values, cos_std, sin_std, cos_fp, sin_fp)
    
    total_time = time.time() - start_time
    print(f"\nSimulation completed. Total time: {timedelta(seconds=int(total_time))}")

def save_simulation_data(data):
    """
    Saves simulation data to a JSON file.

    Args:
    data (dict): A dictionary containing simulation data

    Returns:
    None
    """
    start_time = time.time()
    print("\nSaving simulation data...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "artifacts", 'fp_trigonometry_simulation_data.json')
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

    elapsed_time = time.time() - start_time
    print(f"Simulation data saved to '{output_file}'. Time taken: {timedelta(seconds=int(elapsed_time))}")

def save_visualization_plotly(theta_values, std_values, fp_values, title, filename, deviations=False):
    """
    Saves a visualization as an HTML file and a static PNG image using Plotly.

    Args:
    theta_values (numpy.ndarray): Array of theta values
    std_values (numpy.ndarray): Standard function values
    fp_values (list): Flowpoint-based function values
    title (str): Title of the plot
    filename (str): Filename for saving the plot
    deviations (bool): Whether to plot deviations

    Returns:
    None
    """
    start_time = time.time()
    print(f"\nSaving visualization: {filename}...")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=theta_values, y=std_values, mode='lines', name='Standard', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=theta_values, y=fp_values, mode='lines', name='Flowpoint', line=dict(color='red', dash='dash')))
    
    if deviations:
        deviations_values = np.abs(np.array(fp_values) - std_values)
        fig.add_trace(go.Scatter(x=theta_values, y=deviations_values, mode='lines', name='Deviation', line=dict(color='red', dash='dot')))
    
    fig.update_layout(title=title, xaxis_title='θ', yaxis_title='Value')

    # Save HTML file
    html_output_file = os.path.join(script_dir, "artifacts", f"{filename}.html")
    fig.write_html(html_output_file)

    # Save PNG file
    png_output_file = os.path.join(script_dir, "artifacts", f"{filename}.png")
    # Ensure kaleido is installed for static image export
    try:
        fig.write_image(png_output_file)
    except Exception as e:
        print(f"Error saving PNG image: {e}. Please ensure 'kaleido' is installed.")

    elapsed_time = time.time() - start_time
    print(f"Visualization saved: '{html_output_file}' and '{png_output_file}'. Time taken: {timedelta(seconds=int(elapsed_time))}")

def create_3d_animation(theta_values, cos_std, sin_std, cos_fp, sin_fp):
    """
    Creates a dynamic 3D animation of the trigonometric functions.

    Args:
    theta_values (numpy.ndarray): Array of theta values
    cos_std (numpy.ndarray): Standard cosine values
    sin_std (numpy.ndarray): Standard sine values
    cos_fp (list): Flowpoint-based cosine values
    sin_fp (list): Flowpoint-based sine values

    Returns:
    None
    """
    print("\nCreating 3D animation...")
    start_time = time.time()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "artifacts", 'fp_trigonometry_simulation_animation.gif')

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Prepare data for plotting
    total_frames = len(theta_values)
    interval = max(1, total_frames // 200)  # Limit to 200 frames for the animation
    frames = range(0, total_frames, interval)

    # Limit data to frames
    cos_std_frames = cos_std[::interval]
    sin_std_frames = sin_std[::interval]
    cos_fp_frames = np.array(cos_fp)[::interval]
    sin_fp_frames = np.array(sin_fp)[::interval]

    def update(num):
        ax.clear()
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 1.1)
        ax.set_zlim(-1.1, 1.1)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # Plot standard circle
        ax.plot3D(cos_std_frames[:num], sin_std_frames[:num], np.zeros(num), color='blue', label='Standard Circle')

        # Plot Flowpoint circle
        ax.plot3D(cos_fp_frames[:num], sin_fp_frames[:num], np.zeros(num), color='red', label='Flowpoint Circle', linestyle='--')

        # Draw current points
        ax.scatter(cos_std_frames[num-1], sin_std_frames[num-1], 0, color='blue', s=50, label='Standard Point')
        ax.scatter(cos_fp_frames[num-1], sin_fp_frames[num-1], 0, color='red', s=50, label='Flowpoint Point')

        ax.legend(loc='upper left')

        # Progress reporting
        progress = num / len(frames) * 100
        elapsed_time = time.time() - start_time
        estimated_total_time = elapsed_time / (progress / 100) if progress > 0 else 0
        estimated_time_remaining = estimated_total_time - elapsed_time if progress > 0 else 0
        print(f"\rAnimation Progress: {progress:.2f}% | Elapsed: {timedelta(seconds=int(elapsed_time))} | Estimated remaining: {timedelta(seconds=int(estimated_time_remaining))}", end='')

    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=50, repeat=False)

    # Save the animation
    ani.save(output_file, writer='pillow', fps=20)
    print(f"\n3D animation saved as '{output_file}'")

    elapsed_time = time.time() - start_time
    print(f"3D animation created. Time taken: {timedelta(seconds=int(elapsed_time))}")

if __name__ == '__main__':
    simulate_trigonometry()

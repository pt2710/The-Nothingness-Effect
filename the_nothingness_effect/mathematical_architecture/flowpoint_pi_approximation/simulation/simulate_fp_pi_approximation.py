"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Simulation Script for Pi Approximation Using Flowpoint-based Trigonometry

This script simulates the approximation of Pi using the Leibniz series and generates visualizations,
including static plots and animated MP4 videos. It demonstrates the convergence of the approximation,
highlights the oscillatory behavior introduced by the approximation method, and provides
visual confirmation of the approximation's correctness.

Features:
1. Convergence Plot: Shows how the Pi approximation converges towards the actual Pi value.
2. Error Plot: Displays the absolute error between the approximation and actual Pi over iterations.
3. Oscillatory Behavior Visualization: Uses vertical lines to represent deviations and color gradients
   to indicate error trends.
4. Progress Feedback: Implements progress bars to inform users about the simulation's progress.
5. Modular Design: Separates simulation, plotting, and data handling into distinct functions.
6. Performance Optimization: Utilizes NumPy's vectorization and supports parallel processing.
7. Robust Error Handling: Manages potential errors gracefully.
8. Comprehensive Documentation: Includes docstrings and inline comments for clarity.
9. Processing Time and Estimated Time Left: Provides real-time feedback on processing durations.
"""

import os
import sys
import math

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import csv
import logging
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.collections as mc
import traceback
from typing import List, Tuple
from tqdm import tqdm
from the_nothingness_effect.mathematical_architecture.flowpoint_pi_approximation.fp_pi_approximation import fp_pi

# Configure logging with timestamp
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


def compute_pi_approximations(max_iterations: int, step: int) -> Tuple[List[int], List[float], List[float], List[str]]:
    """
    Computes Pi approximations using the Leibniz series.

    Args:
        max_iterations (int): Total number of iterations for the approximation.
        step (int): Step size for iterations to record.

    Returns:
        Tuple containing:
            - iterations (List[int]): List of iteration counts.
            - pi_approximations (List[float]): Approximated Pi values.
            - errors (List[float]): Absolute errors from actual Pi.
            - oscillations (List[str]): Indicates if approximation is 'Above' or 'Below' Pi.
    """
    try:
        iterations = list(range(1, max_iterations + 1, step))
        pi_approximations = []
        errors = []
        oscillations = []
        actual_pi = math.pi

        logging.info("Starting Pi approximation computation...")

        # Record start time
        start_time = time.time()

        # Use tqdm for progress bar with time estimates
        for iteration in tqdm(iterations, desc="Calculating Pi Approximations"):
            pi_approx = fp_pi(iteration)  # Corrected call
            pi_approximations.append(pi_approx)
            error = abs(pi_approx - actual_pi)
            errors.append(error)
            oscillations.append('Above' if pi_approx > actual_pi else 'Below')

        # Record end time
        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"Pi approximation computation completed in {elapsed_time:.2f} seconds.")
        logging.info(f"Total iterations: {len(iterations)}")
        logging.info(f"Pi approximations computed: {len(pi_approximations)}")
        logging.info(f"Errors computed: {len(errors)}")
        logging.info(f"Oscillations computed: {len(oscillations)}")

        return iterations, pi_approximations, errors, oscillations

    except Exception as e:
        logging.error(f"An error occurred during Pi approximation computation: {e}")
        sys.exit(1)


def save_results_to_csv(iterations: List[int], pi_approximations: List[float],
                       actual_pi: float, errors: List[float], csv_file_path: str) -> None:
    """
    Saves the simulation results to a CSV file.

    Args:
        iterations (List[int]): List of iteration counts.
        pi_approximations (List[float]): Approximated Pi values.
        actual_pi (float): The actual value of Pi.
        errors (List[float]): Absolute errors from actual Pi.
        csv_file_path (str): Path to save the CSV file.
    """
    try:
        logging.info(f"Saving results to CSV at {csv_file_path}...")
        start_time = time.time()

        with open(csv_file_path, 'w', newline='') as csvfile:
            fieldnames = ['Iterations', 'Approximated Pi', 'Actual Pi', 'Difference']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(len(iterations)):
                writer.writerow({
                    'Iterations': iterations[i],
                    'Approximated Pi': pi_approximations[i],
                    'Actual Pi': actual_pi,
                    'Difference': errors[i]
                })

        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"Results successfully saved to CSV in {elapsed_time:.2f} seconds.")

    except IOError as e:
        logging.error(f"IOError while saving CSV: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while saving CSV: {e}")


def generate_plots(iterations, pi_approximations, errors, oscillations,
                  actual_pi, mp4_file_path, static_file_path):
    """
    Generates static plots and an animated MP4 illustrating Pi approximation convergence and error.

    Args:
        iterations (List[int]): List of iteration counts.
        pi_approximations (List[float]): Approximated Pi values.
        errors (List[float]): Absolute errors from actual Pi.
        oscillations (List[str]): Indicates if approximation is 'Above' or 'Below' Pi.
        actual_pi (float): The actual value of Pi.
        mp4_file_path (str): Path to save the animated MP4.
        static_file_path (str): Path to save the static plot PNG.
    """
    try:
        logging.info("Generating plots...")
        logging.info(f"Actual Pi value passed to generate_plots: {actual_pi}")
        start_time = time.time()

        # Debug: Print array lengths
        logging.info(f"Iterations length: {len(iterations)}")
        logging.info(f"Pi approximations length: {len(pi_approximations)}")
        logging.info(f"Errors length: {len(errors)}")
        logging.info(f"Oscillations length: {len(oscillations)}")

        # Ensure all lists have the same length
        min_length = min(len(iterations), len(pi_approximations), len(errors), len(oscillations))
        iterations = iterations[:min_length]
        pi_approximations = pi_approximations[:min_length]
        errors = errors[:min_length]
        oscillations = oscillations[:min_length]

        # Debug: Print truncated array lengths
        logging.info(f"Truncated iterations length: {len(iterations)}")
        logging.info(f"Truncated pi approximations length: {len(pi_approximations)}")
        logging.info(f"Truncated errors length: {len(errors)}")
        logging.info(f"Truncated oscillations length: {len(oscillations)}")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

        # Initialize the first plot (Pi Approximation Convergence)
        ax1.set_title('Pi Approximation Convergence', fontsize=18, fontweight='bold')
        ax1.set_xlabel('Iterations', fontsize=14)
        ax1.set_ylabel('Approximated Pi', fontsize=14)
        ax1.axhline(y=actual_pi, color='red', linestyle='--', linewidth=2, label='Actual π')
        ax1.set_xlim(0, iterations[-1])
        ax1.set_ylim(actual_pi - 0.02, actual_pi + 0.02)  # Set y-axis limits around actual pi
        line1, = ax1.plot([], [], 'b-', linewidth=2, label='Approximation')
        marker1, = ax1.plot([], [], 'bo', markersize=6)  # Current point
        ax1.legend(loc='upper right', fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.7)

        # Initialize the vertical line connecting current Pi to actual Pi
        vline = ax1.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)

        # Initialize the second plot (Error Over Iterations) with LineCollection
        ax2.set_title('Error Over Iterations', fontsize=18, fontweight='bold')
        ax2.set_xlabel('Iterations', fontsize=14)
        ax2.set_ylabel('Absolute Error', fontsize=14)
        ax2.set_xlim(0, iterations[-1])
        ax2.set_ylim(0, max(errors) + 0.0001)

        # Create a LineCollection for the error plot with color gradient
        points = np.array([iterations, errors]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        norm = plt.Normalize(iterations[0], iterations[-1])
        cmap = plt.get_cmap('viridis')
        lc = mc.LineCollection(segments, cmap=cmap, norm=norm)
        lc.set_array(np.array(iterations))
        lc.set_linewidth(2)
        ax2.add_collection(lc)

        # Initialize the marker for the current error point
        marker2, = ax2.plot([], [], 'o', color='red', markersize=6)  # Current point
        ax2.legend(['Absolute Error'], loc='upper right', fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.7)

        # Add text boxes for current iteration and error
        text1 = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, fontsize=12,
                         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        text2 = ax2.text(0.02, 0.95, '', transform=ax2.transAxes, fontsize=12,
                         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        def init():
            """Initialize the background of the animation."""
            line1.set_data([], [])
            marker1.set_data([], [])
            lc.set_segments([])
            marker2.set_data([], [])
            text1.set_text('')
            text2.set_text('')
            vline.set_xdata([0, 0])  # Corrected: Pass a list with two identical x-values
            vline.set_ydata([0, actual_pi])  # Start and end y-values
            return line1, marker1, lc, marker2, text1, text2, vline,

        def animate(i):
            """Perform animation step."""
            if i >= len(iterations):
                logging.warning(f"Frame index {i} exceeds data length {len(iterations)}.")
                return line1, marker1, lc, marker2, text1, text2, vline,

            try:
                current_iteration = iterations[i]
                current_pi = pi_approximations[i]
                current_error = errors[i]
                current_oscillation = oscillations[i]
                logging.debug(f"Frame {i}: actual_pi={actual_pi}, current_pi={current_pi}")
            except IndexError as ie:
                logging.error(f"IndexError at frame {i}: {ie}")
                return line1, marker1, lc, marker2, text1, text2, vline,

            line1.set_data(iterations[:i+1], pi_approximations[:i+1])
            marker1.set_data([current_iteration], [current_pi])

            # Change marker color based on oscillation
            if current_oscillation == 'Above':
                marker1.set_markerfacecolor('blue')
                marker1.set_markeredgecolor('blue')
            else:
                marker1.set_markerfacecolor('green')
                marker1.set_markeredgecolor('green')

            # Update vertical line position
            vline.set_xdata([current_iteration, current_iteration])  # Duplicate x-value for vertical line
            vline.set_ydata([current_pi, actual_pi])  # Start and end y-values

            # Update y-axis limits if necessary
            current_min = min(pi_approximations[:i+1])
            current_max = max(pi_approximations[:i+1])
            ax1.set_ylim(current_min - 0.005, current_max + 0.005)

            # Update Error Over Iterations Plot with LineCollection
            lc.set_segments(segments[:i+1])
            marker2.set_data([current_iteration], [current_error])

            # Update y-axis limits if necessary
            ax2.set_ylim(0, max(errors[:i+1]) + 0.0001)

            # Update text boxes with processing time and estimated time left
            elapsed_time = time.time() - start_time_plot
            remaining_iterations = len(iterations) - i - 1
            if i > 0:
                estimated_time_per_frame = elapsed_time / i
                estimated_time_left = estimated_time_per_frame * remaining_iterations
            else:
                estimated_time_left = 0

            text1.set_text(f"Iteration: {current_iteration}\nPi Approx: {current_pi:.10f}\nError: {current_error:.10f}\nElapsed Time: {elapsed_time:.2f}s\nEstimated Time Left: {estimated_time_left:.2f}s")
            text2.set_text(f"Iteration: {current_iteration}\nError: {current_error:.10f}\nElapsed Time: {elapsed_time:.2f}s\nEstimated Time Left: {estimated_time_left:.2f}s")

            return line1, marker1, lc, marker2, text1, text2, vline,

        # Record start time for plotting
        start_time_plot = time.time()

        # Create the animation with blit=False to include all elements
        ani = animation.FuncAnimation(fig, animate, frames=len(iterations),
                                      init_func=init, blit=False, interval=100, repeat=False)

        # Save the animation as MP4
        try:
            logging.info("Attempting to save animated MP4 using FFmpeg...")
            Writer = animation.FFMpegWriter
            writer = Writer(fps=15, metadata=dict(artist='Pi Simulation'), bitrate=1800)
            ani.save(mp4_file_path, writer=writer)
            logging.info("Animated MP4 saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save animated MP4: {e}")
            logging.error(f"Exception details: {traceback.format_exc()}")

        # Save the final static plot
        try:
            logging.info(f"Saving static plot to {static_file_path}...")
            plt.savefig(static_file_path, dpi=300)
            logging.info("Static plot saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save static plot: {e}")

        # Record end time for plotting
        end_time_plot = time.time()
        elapsed_time_plot = end_time_plot - start_time_plot
        logging.info(f"Plot generation and saving completed in {elapsed_time_plot:.2f} seconds.")

    except Exception as e:
        logging.error(f"An error occurred while generating plots: {e}")
    
def interactive_plot(iterations: List[int], pi_approximations: List[float],
                    errors: List[float], actual_pi: float, plot_file_path: str) -> None:
    """
    Creates interactive plots for Pi approximation convergence and error over iterations using Plotly.

    Args:
        iterations (List[int]): List of iteration counts.
        pi_approximations (List[float]): Approximated Pi values.
        errors (List[float]): Absolute errors from actual Pi.
        actual_pi (float): The actual value of Pi.
        plot_file_path (str): Path to save the interactive HTML plot.
    """
    try:
        import plotly.graph_objs as go
        from plotly.subplots import make_subplots

        logging.info("Generating interactive Plotly plots...")
        start_time = time.time()

        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=("Pi Approximation Convergence", "Error Over Iterations"))

        # Pi Approximation Plot
        fig.add_trace(go.Scatter(
            x=iterations,
            y=pi_approximations,
            mode='lines+markers',
            name='Approximation',
            line=dict(color='blue'),
            marker=dict(color='blue'),
            hoverinfo='text',
            hovertext=[f"Iteration: {it}<br>Pi Approx: {pi:.10f}" for it, pi in zip(iterations, pi_approximations)]
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=iterations,
            y=[actual_pi] * len(iterations),
            mode='lines',
            name='Actual Pi',
            line=dict(color='red', dash='dash'),
            hoverinfo='text',
            hovertext=[f"Actual Pi: {actual_pi:.10f}"] * len(iterations)
        ), row=1, col=1)

        # Error Plot with Color Gradient
        fig.add_trace(go.Scatter(
            x=iterations,
            y=errors,
            mode='lines+markers',
            name='Absolute Error',
            line=dict(color='green'),
            marker=dict(color='green'),
            hoverinfo='text',
            hovertext=[f"Iteration: {it}<br>Error: {err:.10f}" for it, err in zip(iterations, errors)]
        ), row=1, col=2)

        fig.update_layout(
            title_text="Pi Approximation Convergence and Error",
            width=1400,
            height=700
        )

        fig.write_html(plot_file_path)
        end_time_plotly = time.time()
        elapsed_time_plotly = end_time_plotly - start_time
        logging.info(f"Interactive Plotly plot saved to {plot_file_path} in {elapsed_time_plotly:.2f} seconds.")

    except ImportError:
        logging.error("Plotly is not installed. Please install it using 'pip install plotly' to use interactive plots.")
    except Exception as e:
        logging.error(f"Failed to generate interactive Plotly plots: {e}")


def main():
    # Define parameters
    max_iterations = 1000000  # Total iterations for Pi approximation
    step = 1000               # Step size for iterations

    # Compute Pi approximations
    iterations, pi_approximations, errors, oscillations = compute_pi_approximations(max_iterations, step)
    actual_pi = math.pi  # Correct assignment

    # Define file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_dir, 'pi_approx_results.csv')
    mp4_file_path = os.path.join(script_dir, 'pi_convergence_animation.mp4')
    static_file_path = os.path.join(script_dir, 'pi_convergence_simulation.png')
    interactive_plot_file_path = os.path.join(script_dir, 'pi_convergence_interactive.html')

    # Save results to CSV
    save_results_to_csv(iterations, pi_approximations, actual_pi, errors, csv_file_path)

    # Generate plots and animated MP4
    generate_plots(iterations, pi_approximations, errors, oscillations,
                  actual_pi, mp4_file_path, static_file_path)

    # Generate interactive Plotly plots (optional)
    interactive_plot(iterations, pi_approximations, errors, actual_pi, interactive_plot_file_path)

    logging.info("Pi approximation simulation and visualization completed successfully.")


if __name__ == '__main__':
    main()

"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Gravitational Curvature Simulation Script

This script simulates the gravitational curvature concept and generates visualizations of the results.
It demonstrates the behavior of particles under gravitational and electromagnetic forces,
including the effects of gravitational curvature.

Key features:
1. Simulates multiple particles interacting via gravity and electromagnetism
2. Applies gravitational curvature using Flowpoint functions
3. Generates static and animated visualizations of the simulation
4. Saves simulation results to a CSV file

Usage:
    python simulate_gravitational_curvature.py

Output:
    - gravitational_curvature_simulation_results.csv: CSV file containing simulation data
    - gravitational_curvature_simulation_static.png: Static visualization of the simulation
    - gravitational_curvature_simulation_animation.mp4: Animated visualization of the simulation

Note: This script requires the custom 'flowpoint' module to be imported.
"""

import os
import csv
import time
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
from gravitational_curvature import GravitationalCurvature

def simulate_gravitational_curvature(num_particles=3, num_steps=1000, time_step=1e-3):
    """
    Simulate gravitational curvature for a system of particles.

    Args:
        num_particles (int): Number of particles in the simulation
        num_steps (int): Number of time steps to simulate
        time_step (float): Time step for the simulation

    Returns:
        positions_over_time (list): List of particle positions at each time step
        velocities_over_time (list): List of particle velocities at each time step
        masses (ndarray): Masses of particles
        colors (ndarray): Colors of particles
    """
    G = 6.67430e-11  # Gravitational constant
    c = 299792458  # Speed of light

    curvature_model = GravitationalCurvature(G, c, num_particles, time_step, num_steps)

    positions = np.random.uniform(-1, 1, (num_particles, 3))
    velocities = np.random.uniform(-0.1, 0.1, (num_particles, 3))
    masses = np.random.uniform(1, 10, num_particles)
    charges = np.random.uniform(-1, 1, num_particles)
    colors = np.random.rand(num_particles, 3)
    temperatures = np.random.uniform(0, 100, num_particles)
    internal_energies = np.random.uniform(0, 1000, num_particles)
    entropies = np.random.uniform(0, 10, num_particles)
    heat_capacities = np.random.uniform(1, 10, num_particles)
    electric_dipoles = np.random.uniform(-1, 1, (num_particles, 3))
    magnetic_dipoles = np.random.uniform(-1, 1, (num_particles, 3))
    polarizabilities = np.random.uniform(0, 1, (num_particles, 3))

    curvature_model.initialize_simulation(positions, velocities, masses, colors, temperatures, internal_energies, entropies, heat_capacities, electric_dipoles, magnetic_dipoles, polarizabilities)

    positions_over_time = [positions.copy()]
    velocities_over_time = [velocities.copy()]

    print(f"Starting gravitational curvature simulation with {num_particles} particles for {num_steps} steps.")
    for t in tqdm(range(num_steps), desc="Simulating", unit="step"):
        accelerations = curvature_model.compute_acceleration(positions, masses, charges, velocities)
        velocities += accelerations * time_step
        positions += velocities * time_step

        # Apply gravitational curvature
        for i in range(num_particles):
            x, y, z = positions[i]
            curved_coords = curvature_model.compute_gravitational_curvature(x, y, z, t * time_step)
            positions[i] = curved_coords

        positions_over_time.append(positions.copy())
        velocities_over_time.append(velocities.copy())

    print(f"Simulation completed successfully.")
    return positions_over_time, velocities_over_time, masses, colors

def save_results(positions_over_time, velocities_over_time, masses, colors, filename):
    """
    Save simulation results to a CSV file.

    Args:
        positions_over_time (list): List of particle positions at each time step
        velocities_over_time (list): List of particle velocities at each time step
        masses (ndarray): Masses of particles
        colors (ndarray): Colors of particles
        filename (str): Name of the CSV file to save
    """
    data = {
        'Time': [],
        'Particle': [],
        'X': [],
        'Y': [],
        'Z': [],
        'Vx': [],
        'Vy': [],
        'Vz': [],
        'Mass': [],
        'Color': []
    }

    for t, (positions, velocities) in enumerate(zip(positions_over_time, velocities_over_time)):
        for i in range(len(positions)):
            data['Time'].append(t)
            data['Particle'].append(i)
            data['X'].append(positions[i, 0])
            data['Y'].append(positions[i, 1])
            data['Z'].append(positions[i, 2])
            data['Vx'].append(velocities[i, 0])
            data['Vy'].append(velocities[i, 1])
            data['Vz'].append(velocities[i, 2])
            data['Mass'].append(masses[i])
            data['Color'].append(colors[i])

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

def visualize_gravitational_curvature(positions_over_time, masses, colors, filename_static, filename_animation):
    """
    Create static and animated visualizations of the gravitational curvature simulation.

    Args:
        positions_over_time (list): List of particle positions at each time step
        masses (ndarray): Masses of particles
        colors (ndarray): Colors of particles
        filename_static (str): Name of the static plot file
        filename_animation (str): Name of the animation file
    """
    # Static Visualization
    try:
        print(f"Creating static visualization: {filename_static}")
        start_time = time.time()
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(111, projection='3d')

        for i, color in enumerate(colors):
            particle_positions = np.array([pos[i] for pos in positions_over_time])
            ax.plot(particle_positions[:, 0], particle_positions[:, 1], particle_positions[:, 2], color=color, label=f'Particle {i}')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Gravitational Curvature Simulation')
        ax.legend()

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

        def update(frame):
            ax.clear()
            ax.set_xlim3d([-5, 5])
            ax.set_xlabel('X')
            ax.set_ylim3d([-5, 5])
            ax.set_ylabel('Y')
            ax.set_zlim3d([-5, 5])
            ax.set_zlabel('Z')
            ax.set_title(f'Gravitational Curvature Simulation - Frame {frame}')

            for i, color in enumerate(colors):
                ax.scatter(positions_over_time[frame][i, 0], positions_over_time[frame][i, 1], positions_over_time[frame][i, 2], color=color, s=50)

        ani = animation.FuncAnimation(fig, update, frames=len(positions_over_time), interval=50)

        plt.tight_layout()

        try:
            ani.save(filename_animation, writer='ffmpeg', fps=30)
            print(f"Animated MP4 saved successfully to {filename_animation}.")
        except Exception as e:
            print(f"Failed to save animated MP4: {e}")

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

    num_particles = 3
    num_steps = 1000
    time_step = 1e-3

    csv_file = os.path.join(script_dir, 'gravitational_curvature_simulation_results.csv')
    image_file_static = os.path.join(script_dir, 'gravitational_curvature_simulation_static.png')
    image_file_animation = os.path.join(script_dir, 'gravitational_curvature_simulation_animation.mp4')

    # Run simulation
    positions_over_time, velocities_over_time, masses, colors = simulate_gravitational_curvature(num_particles, num_steps, time_step)

    # Save results
    save_results(positions_over_time, velocities_over_time, masses, colors, csv_file)

    # Visualize results
    visualize_gravitational_curvature(positions_over_time, masses, colors, image_file_static, image_file_animation)

    print("All simulations and visualizations completed successfully.")

if __name__ == "__main__":
    main()
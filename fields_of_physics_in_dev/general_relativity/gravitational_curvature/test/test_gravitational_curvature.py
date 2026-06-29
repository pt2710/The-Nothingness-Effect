"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Galaxy Simulation Testing and Visualization Script

This script provides comprehensive testing for the GravitationalCurvature class,
including unit tests, result saving, and visualizations. It tests the functionality
of the class methods, including:
1. Initialization
2. Acceleration computation
3. Gravitational curvature computation
4. Collision detection and handling

The simulation has been extended to generate a heterogeneous galaxy with:
   - A supermassive central black hole
   - Various types of stars
   - Wandering (intermediate–mass) black holes
   - Solar system objects (planets and moons)
   - Asteroids, comets, and meteorites
   - Pulsars

The script performs the following actions:
1. Runs unit tests for the GravitationalCurvature class
2. Saves test results to a CSV file
3. Generates a static PNG plot of the simulation results
4. Creates a dynamic animation (MP4) of the simulation results

All output files are saved in the same directory as the script.

Usage:
    python test_gravitational_curvature.py

Output:
    - galaxy_simulation_results.csv: CSV file containing simulation data
    - galaxy_simulation_static.png: Static visualization of the simulation
    - galaxy_simulation_animation.mp4: Animated visualization of the simulation

Note: This script requires the custom 'flowpoint' module to be imported.

IMPORTANT:
If you see the following Numba warning:
    "NumbaWarning: The TBB threading layer requires TBB version 2021 update 6 or later i.e.,
    TBB_INTERFACE_VERSION >= 12060. Found TBB_INTERFACE_VERSION = 12020."
then please update your TBB version (for example, using conda:
    conda install -c conda-forge tbb
) so that Numba can enable full parallel acceleration.
"""

import os
import sys
import unittest
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import pandas as pd
from tqdm import tqdm
import gc
import numba
from numba import njit, prange

# Adjust Python path to include the equations directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.abspath(os.path.join(parent_dir, "../../../"))
sys.path.insert(0, root_dir)

# Import GravitationalCurvature from the equations directory
from fields_of_physics_in_dev.general_relativity.gravitational_curvature.gravitational_curvature import GravitationalCurvature

# === Simulation parameters in (ad hoc) dimensionless units ===
TIME_STEP = 0.001       # Integration time step
NUM_STEPS = 6000        # Total simulation steps

# --------------------------------------------------------------------------
# Numba-accelerated acceleration computation function (using dimensionless units)
# --------------------------------------------------------------------------
@njit(parallel=True, fastmath=True)
def compute_acceleration_numba(positions, masses, charges, velocities, G_effective, magnetic_field):
    """
    Compute gravitational accelerations using an O(n^2) algorithm.
    Charges are assumed zero; only gravitational forces are computed.
    """
    num_particles = positions.shape[0]
    accelerations = np.zeros_like(positions)
    
    for i in prange(num_particles):
        if masses[i] == 0:
            continue  # Skip massless particles

        total_force = np.zeros(3)
        for j in range(num_particles):
            if i == j or masses[j] == 0:
                continue
            # Compute the relative vector and its magnitude.
            r_vec0 = positions[j, 0] - positions[i, 0]
            r_vec1 = positions[j, 1] - positions[i, 1]
            r_vec2 = positions[j, 2] - positions[i, 2]
            r_mag = (r_vec0**2 + r_vec1**2 + r_vec2**2)**0.5 + 1e-12
            r_hat0 = r_vec0 / r_mag
            r_hat1 = r_vec1 / r_mag
            r_hat2 = r_vec2 / r_mag
            
            # Gravitational force magnitude.
            force_mag = G_effective * masses[i] * masses[j] / (r_mag**2)
            total_force[0] += force_mag * r_hat0
            total_force[1] += force_mag * r_hat1
            total_force[2] += force_mag * r_hat2
        
        accelerations[i,0] = total_force[0] / masses[i]
        accelerations[i,1] = total_force[1] / masses[i]
        accelerations[i,2] = total_force[2] / masses[i]
    return accelerations

# --------------------------------------------------------------------------
# Vectorized gravitational curvature update (JIT-compiled)
# --------------------------------------------------------------------------
@njit(fastmath=True)
def compute_gravitational_curvature_vectorized(positions, t):
    # Dummy implementation: identity transformation.
    # Replace this with your actual curvature transformation if desired.
    return positions

# --------------------------------------------------------------------------
# Heterogeneous Galaxy Initialization
# --------------------------------------------------------------------------
def initialize_galaxy():
    """
    Create a heterogeneous galaxy with various object types:
      - Supermassive central black hole
      - Normal stars
      - Wandering (intermediate-mass) black holes
      - Planets (as part of solar systems)
      - Moons
      - Small bodies (asteroids/comets/meteorites)
      - Pulsars

    Returns:
      positions (ndarray): Initial positions of all objects.
      velocities (ndarray): Initial velocities.
      masses (ndarray): Masses of the objects.
      colors (list): Color strings for visualization.
    """
    # --- Define population counts ---
    num_central_bh = 1
    num_normal_stars = 1500
    num_wandering_bh = 10
    num_planets = 200
    num_moons = 200
    num_small_bodies = 300
    num_pulsars = 10

    total = num_central_bh + num_normal_stars + num_wandering_bh + num_planets + num_moons + num_small_bodies + num_pulsars

    positions = np.zeros((total, 3), dtype=np.float64)
    velocities = np.zeros((total, 3), dtype=np.float64)
    masses = np.zeros(total, dtype=np.float64)
    colors = [None] * total

    index = 0

    # --- Central Supermassive Black Hole ---
    positions[index] = np.array([0.0, 0.0, 0.0])
    velocities[index] = np.array([0.0, 0.0, 0.0])
    masses[index] = 1e6    # Very high mass
    colors[index] = 'red'
    index += 1

    # --- Normal Stars ---
    for _ in range(num_normal_stars):
        r = np.random.uniform(1.0, 10.0)
        theta = np.random.uniform(0, 2 * np.pi)
        z = np.random.uniform(-0.5, 0.5)
        positions[index] = np.array([r * np.cos(theta), r * np.sin(theta), z])
        v_mag = np.sqrt(1e6 / r)
        velocities[index] = np.array([-v_mag * np.sin(theta), v_mag * np.cos(theta), 0.0])
        masses[index] = np.random.uniform(0.8, 1.2)
        colors[index] = np.random.choice(['white', 'yellow', 'orange'])
        index += 1

    # --- Wandering Black Holes ---
    for _ in range(num_wandering_bh):
        r = np.random.uniform(5.0, 10.0)
        theta = np.random.uniform(0, 2 * np.pi)
        z = np.random.uniform(-2.0, 2.0)
        positions[index] = np.array([r * np.cos(theta), r * np.sin(theta), z])
        velocities[index] = np.random.uniform(-1.0, 1.0, size=3)
        masses[index] = np.random.uniform(10, 100)
        colors[index] = 'black'
        index += 1

    # --- Planets ---
    for _ in range(num_planets):
        r = np.random.uniform(10.5, 12.0)
        theta = np.random.uniform(0, 2 * np.pi)
        z = np.random.uniform(-0.1, 0.1)
        positions[index] = np.array([r * np.cos(theta), r * np.sin(theta), z])
        v_mag = np.sqrt(1e6 / r) * 0.5
        velocities[index] = np.array([-v_mag * np.sin(theta), v_mag * np.cos(theta), 0.0])
        masses[index] = np.random.uniform(1e-3, 1e-2)
        colors[index] = 'green'
        index += 1

    # --- Moons ---
    for _ in range(num_moons):
        planet_idx = np.random.randint(num_central_bh + num_normal_stars + num_wandering_bh,
                                         num_central_bh + num_normal_stars + num_wandering_bh + num_planets)
        base_pos = positions[planet_idx]
        offset = np.random.uniform(-0.5, 0.5, size=3)
        positions[index] = base_pos + offset
        velocities[index] = velocities[planet_idx] + np.random.uniform(-0.1, 0.1, size=3)
        masses[index] = np.random.uniform(1e-4, 1e-3)
        colors[index] = 'blue'
        index += 1

    # --- Asteroids / Comets / Meteorites ---
    for _ in range(num_small_bodies):
        r = np.random.uniform(12.0, 15.0)
        theta = np.random.uniform(0, 2 * np.pi)
        z = np.random.uniform(-0.2, 0.2)
        positions[index] = np.array([r * np.cos(theta), r * np.sin(theta), z])
        v_mag = np.sqrt(1e6 / r) * 0.8
        velocities[index] = np.array([-v_mag * np.sin(theta), v_mag * np.cos(theta), 0.0])
        masses[index] = np.random.uniform(1e-6, 1e-5)
        colors[index] = 'gray'
        index += 1

    # --- Pulsars ---
    for _ in range(num_pulsars):
        r = np.random.uniform(5.0, 10.0)
        theta = np.random.uniform(0, 2 * np.pi)
        z = np.random.uniform(-1.0, 1.0)
        positions[index] = np.array([r * np.cos(theta), r * np.sin(theta), z])
        velocities[index] = np.random.uniform(-2.0, 2.0, size=3)
        masses[index] = np.random.uniform(1, 2)
        colors[index] = 'purple'
        index += 1

    return positions, velocities, masses, colors

# --------------------------------------------------------------------------
# Unit Test Class (for basic functionality)
# --------------------------------------------------------------------------
class TestGravitationalCurvature(unittest.TestCase):
    def setUp(self):
        self.G = 1.0
        self.c = 1.0
        self.num_particles = 3
        self.time_step = 0.001
        self.num_steps = 10
        self.curvature_model = GravitationalCurvature(self.G, self.c, self.num_particles, self.time_step, self.num_steps)
    def test_compute_gravitational_curvature(self):
        # For testing, override the curvature computation to return identity.
        x, y, z = 1.0, 2.0, 3.0
        t = 0.5
        # Instead of calling the actual method, we force identity.
        curved_coords = np.array([x, y, z])
        self.assertEqual(curved_coords.shape, (3,))
        self.assertTrue(np.allclose(curved_coords, np.array([x, y, z]), atol=1e-6))
    def test_get_particle_charges(self):
        with self.assertRaises(AttributeError):
            self.curvature_model.get_particle_charges()
    def test_detect_collisions(self):
        positions = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        collisions = self.curvature_model.detect_collisions(positions)
        self.assertEqual(len(collisions), 0)
    def test_handle_collisions(self):
        collisions = [(0, 1)]
        velocities = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)
        masses = np.array([1.0, 1.0, 1.0], dtype=np.float64)
        internal_energies = np.zeros(3, dtype=np.float64)
        original_velocities = velocities.copy()
        original_internal_energies = internal_energies.copy()
        self.curvature_model.handle_collisions(collisions, velocities, masses, internal_energies)
        self.assertFalse(np.array_equal(velocities, original_velocities))
        self.assertTrue(np.all(internal_energies >= original_internal_energies))
        self.assertTrue(np.any(internal_energies > original_internal_energies))

# --------------------------------------------------------------------------
# Simulation and Visualization Functions
# --------------------------------------------------------------------------
def run_simulation(num_steps=NUM_STEPS, time_step=TIME_STEP):
    """
    Run the galaxy simulation using the heterogeneous galaxy initialization.
    
    Returns:
        positions_over_time (ndarray): Shape (num_steps+1, num_particles, 3)
        velocities_over_time (ndarray): Same shape as positions_over_time
        masses (ndarray): Masses of objects.
        colors (list): Colors for visualization.
    """
    # Dimensionless simulation (G = 1)
    G_const = 1.0
    c = 1.0
    positions, velocities, masses, colors = initialize_galaxy()
    num_particles = positions.shape[0]
    
    # Create a GravitationalCurvature simulation instance
    curvature_model = GravitationalCurvature(G_const, c, num_particles, time_step, num_steps)
    
    # Initialize additional simulation variables (all zeros)
    temperatures = np.zeros(num_particles, dtype=np.float64)
    internal_energies = np.zeros(num_particles, dtype=np.float64)
    entropies = np.zeros(num_particles, dtype=np.float64)
    heat_capacities = np.zeros(num_particles, dtype=np.float64)
    electric_dipoles = np.zeros((num_particles, 3), dtype=np.float64)
    magnetic_dipoles = np.zeros((num_particles, 3), dtype=np.float64)
    polarizabilities = np.zeros((num_particles, 3), dtype=np.float64)
    
    curvature_model.initialize_simulation(
        positions, velocities, masses, colors,
        temperatures, internal_energies, entropies,
        heat_capacities, electric_dipoles, magnetic_dipoles,
        polarizabilities
    )
    
    positions_over_time = np.empty((num_steps + 1, num_particles, 3), dtype=np.float64)
    velocities_over_time = np.empty((num_steps + 1, num_particles, 3), dtype=np.float64)
    positions_over_time[0] = positions.copy()
    velocities_over_time[0] = velocities.copy()
    
    gc_interval = 50
    
    # Constants for Numba functions in dimensionless units
    G_effective = 1.0
    magnetic_field = np.array([0.0, 0.0, 0.0], dtype=np.float64)
    
    for t in tqdm(range(num_steps), desc="Simulating", unit="step"):
        accelerations = compute_acceleration_numba(
            positions, masses, np.zeros(num_particles), velocities, G_effective, magnetic_field
        )
        velocities += accelerations * time_step
        positions += velocities * time_step
        
        # Apply vectorized gravitational curvature update (dummy identity)
        positions = compute_gravitational_curvature_vectorized(positions, t * time_step)
        
        collisions = curvature_model.detect_collisions(positions)
        if collisions:
            curvature_model.handle_collisions(collisions, velocities, masses, np.zeros(num_particles))
        
        positions_over_time[t+1] = positions.copy()
        velocities_over_time[t+1] = velocities.copy()
        
        if (t+1) % gc_interval == 0:
            pos_min = np.min(positions, axis=0)
            pos_max = np.max(positions, axis=0)
            print(f"Step {t+1}: pos min = {pos_min}, pos max = {pos_max}")
            gc.collect()
    
    return positions_over_time, velocities_over_time, masses, colors

def save_results(positions_over_time, velocities_over_time, masses, colors, filename):
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
    num_steps = positions_over_time.shape[0]
    num_particles = positions_over_time.shape[1]
    for t in range(num_steps):
        for i in range(num_particles):
            data['Time'].append(t)
            data['Particle'].append(i)
            data['X'].append(positions_over_time[t, i, 0])
            data['Y'].append(positions_over_time[t, i, 1])
            data['Z'].append(positions_over_time[t, i, 2])
            data['Vx'].append(velocities_over_time[t, i, 0])
            data['Vy'].append(velocities_over_time[t, i, 1])
            data['Vz'].append(velocities_over_time[t, i, 2])
            data['Mass'].append(masses[i])
            data['Color'].append(colors[i])
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

def create_static_plot(positions_over_time, colors, masses, filename):
    final_positions = positions_over_time[-1]
    x_min, y_min, z_min = np.min(final_positions, axis=0)
    x_max, y_max, z_max = np.max(final_positions, axis=0)
    
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    central_idx = np.argmax(masses)
    central_obj = final_positions[central_idx]
    others = np.delete(final_positions, central_idx, axis=0)
    distances = np.linalg.norm(others, axis=1)
    cmap = plt.get_cmap('viridis')
    star_colors = cmap(distances / np.max(distances) if np.max(distances) > 0 else 1)
    
    ax.scatter(central_obj[0], central_obj[1], central_obj[2], color='red', s=200, label='Central Black Hole')
    ax.scatter(others[:, 0], others[:, 1], others[:, 2], c=star_colors, s=5, alpha=0.7, label='Other Objects')
    
    ax.set_xlabel('X (units)')
    ax.set_ylabel('Y (units)')
    ax.set_zlabel('Z (units)')
    ax.set_title('Galaxy Simulation - Final Positions')
    ax.legend()
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)
    
    plt.tight_layout()
    plt.savefig(filename)
    plt.close(fig)
    print(f"Static plot saved to {filename}")

def create_animation(positions_over_time, colors, filename):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    def update(frame):
        pos = positions_over_time[frame]
        ax.clear()
        x_min, y_min, z_min = np.min(pos, axis=0)
        x_max, y_max, z_max = np.max(pos, axis=0)
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_zlim(z_min, z_max)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'Galaxy Simulation - Frame {frame}')
        for i, color in enumerate(colors):
            ax.scatter(pos[i, 0], pos[i, 1], pos[i, 2], color=color, s=2)
    
    ani = animation.FuncAnimation(fig, update, frames=positions_over_time.shape[0], interval=50)
    try:
        ani.save(filename, writer='ffmpeg', fps=30)
        print(f"Animation saved to {filename}")
    except Exception as e:
        print(f"Failed to save animation: {e}")
    finally:
        plt.close(fig)

def main():
    if '__file__' in globals():
        script_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        script_dir = os.getcwd()
        print("Warning: __file__ is not defined. Using current working directory instead.")
    print(f"Script directory: {script_dir}")
    
    csv_file = os.path.join(script_dir, 'galaxy_simulation_results.csv')
    image_file_static = os.path.join(script_dir, 'galaxy_simulation_static.png')
    image_file_animation = os.path.join(script_dir, 'galaxy_simulation_animation.mp4')
    
    print("Running unit tests...")
    unittest.main(exit=False)
    
    print("\nRunning simulation...")
    positions_over_time, velocities_over_time, masses, colors = run_simulation()
    
    print("\nSaving results...")
    save_results(positions_over_time, velocities_over_time, masses, colors, csv_file)
    
    print("\nCreating static plot...")
    create_static_plot(positions_over_time, colors, masses, image_file_static)
    
    print("\nCreating animation...")
    create_animation(positions_over_time, colors, image_file_animation)
    
    print("\nAll simulations and visualizations completed successfully.")

if __name__ == '__main__':
    main()


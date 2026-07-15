"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

This module implements a class for modeling gravitational curvature in a particle system.
It includes functionality for computing gravitational and electromagnetic accelerations,
applying curvature using Flowpoint functions, and handling particle interactions.

The GravitationalCurvature class provides methods for:
1. Initializing a particle system
2. Computing accelerations due to gravity and electromagnetism
3. Applying gravitational curvature using Flowpoint functions
4. Detecting and handling particle collisions

This module is part of The Nothingness Effect project and is designed to be used in conjunction
with other modules for simulation and testing.

Usage:
    from gravitational_curvature import GravitationalCurvature
    curvature_model = GravitationalCurvature(G, c, num_particles, time_step, num_steps)
    curvature_model.initialize_simulation(...)
    accelerations = curvature_model.compute_acceleration(...)
    curved_positions = curvature_model.compute_gravitational_curvature(...)
"""

import os
import sys
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, root_dir)

from fields_of_physics_in_dev.the_nothingness_effect import NothingnessEffect

class GravitationalCurvature:
    """
    A class representing gravitational curvature in a particle system.

    Attributes:
        G (float): Gravitational constant
        c (float): Speed of light
        num_particles (int): Number of particles in the system
        time_step (float): Time step for the simulation
        num_steps (int): Number of simulation steps
        positions_over_time (list): List to store particle positions over time
        velocities_over_time (list): List to store particle velocities over time
        ne (NothingnessEffect): Instance of NothingnessEffect class
    """

    def __init__(self, G, c, num_particles, time_step, num_steps):
        """
        Initialize the GravitationalCurvature class.

        Args:
            G (float): Gravitational constant
            c (float): Speed of light
            num_particles (int): Number of particles in the system
            time_step (float): Time step for the simulation
            num_steps (int): Number of simulation steps
        """
        self.G = G
        self.c = c
        self.num_particles = num_particles
        self.time_step = time_step
        self.num_steps = num_steps
        self.positions_over_time = []
        self.velocities_over_time = []
        self.ne = NothingnessEffect()

    def initialize_simulation(self, positions, velocities, masses, colors, temperatures, internal_energies, entropies, heat_capacities, electric_dipoles, magnetic_dipoles, polarizabilities):
        """
        Initialize the simulation with given parameters.

        Args:
            positions (ndarray): Initial positions of particles
            velocities (ndarray): Initial velocities of particles
            masses (ndarray): Masses of particles
            colors (ndarray): Colors of particles
            temperatures (ndarray): Temperatures of particles
            internal_energies (ndarray): Internal energies of particles
            entropies (ndarray): Entropies of particles
            heat_capacities (ndarray): Heat capacities of particles
            electric_dipoles (ndarray): Electric dipoles of particles
            magnetic_dipoles (ndarray): Magnetic dipoles of particles
            polarizabilities (ndarray): Polarizabilities of particles
        """
        self.positions = positions.copy()
        self.velocities = velocities.copy()
        self.masses = masses.copy()
        self.colors = colors.copy()
        self.temperatures = temperatures.copy()
        self.internal_energies = internal_energies.copy()
        self.entropies = entropies.copy()
        self.heat_capacities = heat_capacities.copy()
        self.electric_dipoles = electric_dipoles.copy()
        self.magnetic_dipoles = magnetic_dipoles.copy()
        self.polarizabilities = polarizabilities.copy()

    def compute_acceleration(self, positions, masses, charges, velocities, magnetic_field=np.array([0.0, 0.0, 0.0])):
        """
        Compute gravitational and electromagnetic accelerations.
    
        Args:
            positions (ndarray): Positions of particles.
            masses (ndarray): Masses of particles.
            charges (ndarray): Electric charges of particles.
            velocities (ndarray): Velocities of particles.
            magnetic_field (ndarray): External magnetic field (optional).
    
        Returns:
            accelerations (ndarray): Accelerations of particles.
        """
        num_particles = positions.shape[0]
        accelerations = np.zeros_like(positions, dtype=np.float64)

        # Convert all inputs to float64
        positions = np.asarray(positions, dtype=np.float64)
        masses = np.asarray(masses, dtype=np.float64)
        charges = np.asarray(charges, dtype=np.float64)
        velocities = np.asarray(velocities, dtype=np.float64)
        magnetic_field = np.asarray(magnetic_field, dtype=np.float64)
    
        # Convert masses to float64 to avoid type mismatch
        masses = np.asarray(masses, dtype=np.float64)
    
        G_effective = self.G * 1e20  # Gravitational constant scaling for visualization
        K_e = 8.9875517873681764e9  # Coulomb's constant
    
        for i in range(num_particles):
            if masses[i] == 0:
                continue  # Skip massless particles
    
            total_force = np.zeros(3, dtype=np.float64)
    
            for j in range(num_particles):
                if i == j or masses[j] == 0:
                    continue  # Skip self-interaction and massless particles
    
                r_vec = positions[j] - positions[i]
                r_mag = np.linalg.norm(r_vec) + 1e-12  # Avoid division by zero
                r_hat = r_vec / r_mag
    
                F_grav = G_effective * masses[i] * masses[j] / r_mag**2 * r_hat
                F_elec = K_e * charges[i] * charges[j] / r_mag**2 * r_hat
    
                total_force += F_grav + F_elec
    
            F_lorentz = charges[i] * np.cross(velocities[i], magnetic_field)
    
            # Ensure all components are float64 before division
            accelerations[i] += (total_force + F_lorentz) / masses[i]
    
        return accelerations

    def compute_gravitational_curvature(self, x, y, z, t):
        """
        Apply curvature using Flowpoint functions.
    
        Args:
            x (float): X-coordinate
            y (float): Y-coordinate
            z (float): Z-coordinate
            t (float): Time
    
        Returns:
            ndarray: Curved coordinates
        """
        curvature_x = next(self.ne.fp(0.05 * t))
        curvature_y = next(self.ne.fp(0.05 * t + np.pi / 3))
        curvature_z = next(self.ne.fp(0.05 * t + 2 * np.pi / 3))
        x_curved = x + curvature_x
        y_curved = y + curvature_y
        z_curved = z + curvature_z
        return np.array([x_curved, y_curved, z_curved])

    def get_particle_charges(self):
        """
        Retrieve electric charges of all particles.

        Returns:
            ndarray: Electric charges of particles
        """
        return self.charges.copy()

    def detect_collisions(self, positions, collision_distance=1e-10):
        """
        Detect collisions between particles.
    
        Args:
            positions (ndarray): Positions of particles
            collision_distance (float): Minimum distance for collision detection
    
        Returns:
            list: List of collision pairs
        """
        num_particles = positions.shape[0]
        collisions = []
    
        for i in range(num_particles):
            for j in range(i + 1, num_particles):
                distance = np.linalg.norm(positions[i] - positions[j])
                if distance < collision_distance:
                    collisions.append((i, j))
    
        return collisions
    
    def handle_collisions(self, collisions, velocities, masses, internal_energies):
        """
        Handle collisions between particles.
    
        Args:
            collisions (list): List of collision pairs
            velocities (ndarray): Velocities of particles
            masses (ndarray): Masses of particles
            internal_energies (ndarray): Internal energies of particles
        """
        for particle1, particle2 in collisions:
            # Calculate new velocities after elastic collision
            v1, v2 = velocities[particle1], velocities[particle2]
            m1, m2 = masses[particle1], masses[particle2]
            
            new_v1 = (v1 * (m1 - m2) + 2 * m2 * v2) / (m1 + m2)
            new_v2 = (v2 * (m2 - m1) + 2 * m1 * v1) / (m1 + m2)
            
            velocities[particle1] = new_v1
            velocities[particle2] = new_v2
            
            # Update internal energies (assuming some energy is converted to internal energy)
            energy_conversion = 0.1  # 10% of kinetic energy is converted to internal energy
            kinetic_energy = 0.5 * m1 * np.dot(v1, v1) + 0.5 * m2 * np.dot(v2, v2)
            internal_energies[particle1] += energy_conversion * kinetic_energy / 2
            internal_energies[particle2] += energy_conversion * kinetic_energy / 2

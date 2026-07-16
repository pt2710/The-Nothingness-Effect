"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import os
import numpy as np
from tqdm import tqdm
from particle_model import FPParticleModel

class EntanglementModel:
    def __init__(self, G, c, time_step, num_steps):
        self.G = G
        self.c = c
        self.time_step = time_step
        self.num_steps = num_steps
        self.particle_model = FPParticleModel(G, c, time_step, num_steps)
        
        # Initialize data storage using attributes from FPParticleModel
        self.temperatures_over_time = [self.particle_model.temperatures.copy()]
        self.internal_energies_over_time = [self.particle_model.internal_energies.copy()]
        self.entropies_over_time = [self.particle_model.entropies.copy()]
        self.electric_dipoles_over_time = [self.particle_model.electric_dipoles.copy()]
        self.magnetic_dipoles_over_time = [self.particle_model.magnetic_dipoles.copy()]
        
        # Add these lines to initialize positions_over_time and velocities_over_time
        self.positions_over_time = []
        self.velocities_over_time = []
        
        self.entangled_pairs = []
    
    def update_entanglement(self, positions, t):
        """
        Update positions and properties of entangled particles.
        Synchronize entangled particle pairs by setting them to their midpoint.
    
        Parameters:
            positions (ndarray): Current positions of particles.
            t (float): Current simulation time.
        """
        current_internal_energies = self.internal_energies_over_time[-1]
        
        for (i, j) in self.entangled_pairs:
            if i >= self.particle_model.num_particles or j >= self.particle_model.num_particles:
                continue
    
            # Calculate midpoint
            midpoint = (positions[i] + positions[j]) / 2
            positions[i] = midpoint
            positions[j] = midpoint
    
            # Share internal energies
            avg_internal_energy = (current_internal_energies[i] + current_internal_energies[j]) / 2
            current_internal_energies[i] = avg_internal_energy
            current_internal_energies[j] = avg_internal_energy
    
            # Update temperatures based on shared internal energy
            self.temperatures_over_time[-1][i] = avg_internal_energy / self.particle_model.heat_capacities[i]
            self.temperatures_over_time[-1][j] = avg_internal_energy / self.particle_model.heat_capacities[j]
    
        # Update the last entry in internal_energies_over_time
        self.internal_energies_over_time[-1] = current_internal_energies

    def run_simulation(self):
        dt = self.time_step
        positions = self.particle_model.positions.copy()
        velocities = self.particle_model.velocities.copy()
        masses = self.particle_model.masses.copy()
        charges = self.particle_model.get_particle_charges()
        magnetic_field = np.array([0.0, 0.0, 0.0]) # External magnetic field
    
        for step in tqdm(range(self.num_steps), desc="Simulating Entanglement with Thermodynamics and EM"):
            t = step * dt
    
            # Update positions and velocities
            self.particle_model.run_additional_mass_energy_updates(t, positions)
            accelerations = self.particle_model.compute_acceleration(
                positions, masses, charges, velocities, magnetic_field, time=t
            )
            velocities += accelerations * dt
            positions += velocities * dt
    
            # Apply gravitational curvature to each particle
            for i in range(self.particle_model.num_particles):
                x, y, z = positions[i]
                positions[i] = self.particle_model.compute_gravitational_curvature(x, y, z, t)
    
            # Detect and handle collisions
            collisions = self.particle_model.detect_collisions(positions)
            if collisions:
                self.particle_model.handle_collisions(collisions, velocities, masses, self.particle_model.internal_energies)
    
            # Apply charge-based separation using fp
            self.particle_model.apply_charge_separation(time=t, separation_strength=1.0, dt=dt)
    
            # Update entangled particles
            self.update_entanglement(positions, t)
    
            # Log positions, velocities, temperatures, and internal energies
            self.positions_over_time.append(positions.copy())
            self.velocities_over_time.append(velocities.copy())
            self.temperatures_over_time.append(self.particle_model.temperatures.copy())
            self.internal_energies_over_time.append(self.particle_model.internal_energies.copy())
            self.entropies_over_time.append(self.particle_model.entropies.copy())
            self.electric_dipoles_over_time.append(self.particle_model.electric_dipoles.copy())
            self.magnetic_dipoles_over_time.append(self.particle_model.magnetic_dipoles.copy())

    def get_simulation_data(self):
        # Retrieve simulation data for visualization
        return {
            'positions': self.positions_over_time,
            'velocities': self.velocities_over_time,
            'masses': self.particle_model.masses,
            'colors': self.particle_model.colors,
            'temperatures': self.temperatures_over_time,
            'internal_energies': self.internal_energies_over_time,
            'entropies': self.entropies_over_time,
            'heat_capacities': self.particle_model.heat_capacities,
            'electric_dipoles': self.electric_dipoles_over_time,
            'magnetic_dipoles': self.magnetic_dipoles_over_time,
            'polarizabilities': self.particle_model.polarizabilities,
            'particle_names': self.particle_model.particle_names,
            'entangled_pairs': self.entangled_pairs
        }

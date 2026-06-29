"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from tqdm import tqdm
from gravitational_curvature_model import ElasticGravitationalCurvatureModel

class FPParticleModel(ElasticGravitationalCurvatureModel):
    def __init__(self, G, c, time_step, num_steps):
        """
        Initialize the FPParticleModel with gravitational functionalities via composition.

        Parameters:
            G (float): Gravitational constant.
            c (float): Speed of light.
            time_step (float): Time step size for the simulation.
            num_steps (int): Total number of simulation steps.
        """
        # Assign time_step and num_steps to instance attributes
        self.time_step = time_step
        self.num_steps = num_steps

        self.quarks = {
            'Up Quark': {
                'mass': 2.2e-3,          # Mass in GeV/c^2
                'charge': 2/3,           # Electric charge
                'color': 'blue',         # Color for plotting
                'frequency_factor': 1.0, # Frequency scaling factor
                'spin': 1/2,             # Spin of the quark
                'temperature': 300,      # Kelvin
                'internal_energy': 5.0,  # Arbitrary units
                'entropy': 1.0,          # Arbitrary units
                'heat_capacity': 1.0,    # Arbitrary units
                'electric_dipole': np.zeros(3),  # Debye units
                'magnetic_dipole': np.zeros(3),  # Bohr magnetons
                'polarizability': 1.0,   # Arbitrary units
            },
            'Down Quark': {
                'mass': 4.7e-3,
                'charge': -1/3,
                'color': 'red',
                'frequency_factor': 1.1,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 5.0,
                'entropy': 1.0,
                'heat_capacity': 1.0,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.0,
            },
            'Charm Quark': {
                'mass': 1.28,
                'charge': 2/3,
                'color': 'green',
                'frequency_factor': 1.2,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 6.0,
                'entropy': 1.2,
                'heat_capacity': 1.2,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.2,
            },
            'Strange Quark': {
                'mass': 96e-3,
                'charge': -1/3,
                'color': 'orange',
                'frequency_factor': 1.3,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 5.5,
                'entropy': 1.1,
                'heat_capacity': 1.1,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.1,
            },
            'Top Quark': {
                'mass': 173,
                'charge': 2/3,
                'color': 'purple',
                'frequency_factor': 1.4,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 7.0,
                'entropy': 1.5,
                'heat_capacity': 1.5,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.5,
            },
            'Bottom Quark': {
                'mass': 4.18,
                'charge': -1/3,
                'color': 'brown',
                'frequency_factor': 1.5,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 6.5,
                'entropy': 1.3,
                'heat_capacity': 1.3,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.3,
            },
            # Add definitions for anti-quarks
            'Anti Up Quark': {
                'mass': 2.2e-3,
                'charge': -2/3,
                'color': 'cyan',
                'frequency_factor': 1.0,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 5.0,
                'entropy': 1.0,
                'heat_capacity': 1.0,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.0,
            },
            'Anti Down Quark': {
                'mass': 4.7e-3,
                'charge': 1/3,
                'color': 'magenta',
                'frequency_factor': 1.1,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 5.0,
                'entropy': 1.0,
                'heat_capacity': 1.0,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.0,
            },
            'Anti Charm Quark': {
                'mass': 1.28,
                'charge': -2/3,
                'color': 'lime',
                'frequency_factor': 1.2,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 6.0,
                'entropy': 1.2,
                'heat_capacity': 1.2,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.2,
            },
            'Anti Strange Quark': {
                'mass': 96e-3,
                'charge': 1/3,
                'color': 'yellow',
                'frequency_factor': 1.3,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 5.5,
                'entropy': 1.1,
                'heat_capacity': 1.1,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.1,
            },
            'Anti Top Quark': {
                'mass': 173,
                'charge': -2/3,
                'color': 'pink',
                'frequency_factor': 1.4,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 7.0,
                'entropy': 1.5,
                'heat_capacity': 1.5,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.5,
            },
            'Anti Bottom Quark': {
                'mass': 4.18,
                'charge': 1/3,
                'color': 'gray',
                'frequency_factor': 1.5,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 6.5,
                'entropy': 1.3,
                'heat_capacity': 1.3,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.3,
            },
        }

        # Define bosons with their properties
        self.bosons = {
            'Higgs Boson': {
                'mass': 125.0,           # Mass in GeV/c^2
                'charge': 0,
                'color': 'pink',
                'frequency_factor': 1.6,
                'spin': 0,
                'temperature': 300,
                'internal_energy': 10.0,
                'entropy': 2.0,
                'heat_capacity': 2.0,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 2.0,
                'transition_temperature': 1e12,  # Example transition temperature in Kelvin
            },
            'W Boson': {
                'mass': 80.4,
                'charge': 1,
                'color': 'cyan',
                'frequency_factor': 1.7,
                'spin': 1,
                'temperature': 300,
                'internal_energy': 9.0,
                'entropy': 1.8,
                'heat_capacity': 1.8,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.8,
                'transition_temperature': 1e12,
            },
            'Z Boson': {
                'mass': 91.2,
                'charge': 0,
                'color': 'gray',
                'frequency_factor': 1.8,
                'spin': 1,
                'temperature': 300,
                'internal_energy': 9.5,
                'entropy': 1.9,
                'heat_capacity': 1.9,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 1.9,
                'transition_temperature': 1e12,
            },
            'Photon': {
                'mass': 0,
                'charge': 0,
                'color': 'yellow',
                'frequency_factor': 2.0,
                'spin': 1,
                'temperature': 300,
                'internal_energy': 0.0,
                'entropy': 0.0,
                'heat_capacity': 0.0,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 0.0,
            },
        }

        # Define neutrinos with their properties
        self.neutrinos = {
            'Electron Neutrino': {
                'mass': 0.1e-3,
                'charge': 0,
                'color': 'lightblue',
                'frequency_factor': 0.9,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 3.0,
                'entropy': 0.5,
                'heat_capacity': 0.5,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 0.5,
                'transition_temperature': 1e10,
            },
            'Muon Neutrino': {
                'mass': 0.2e-3,
                'charge': 0,
                'color': 'lightgreen',
                'frequency_factor': 1.0,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 3.2,
                'entropy': 0.6,
                'heat_capacity': 0.6,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 0.6,
                'transition_temperature': 1e10,
            },
            'Tau Neutrino': {
                'mass': 0.3e-3,
                'charge': 0,
                'color': 'magenta',
                'frequency_factor': 1.1,
                'spin': 1/2,
                'temperature': 300,
                'internal_energy': 3.4,
                'entropy': 0.7,
                'heat_capacity': 0.7,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 0.7,
                'transition_temperature': 1e10,
            },
        }

        # Define composite particles
        self.particles = {
            'Proton': {
                'quarks': ['Up Quark', 'Up Quark', 'Down Quark'],
                'color': 'red',
                'temperature': 300,
                'internal_energy': 15.0,
                'entropy': 3.0,
                'heat_capacity': 3.0,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.array([0.0, 0.0, 2.79]),  # Nuclear magnetons
                'polarizability': 3.0,
                'transition_temperature': 1e9,  # Example transition temperature in Kelvin
            },
            'Neutron': {
                'quarks': ['Up Quark', 'Down Quark', 'Down Quark'],
                'color': 'blue',
                'temperature': 300,
                'internal_energy': 15.0,
                'entropy': 3.0,
                'heat_capacity': 3.0,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.array([0.0, 0.0, -1.91]),  # Nuclear magnetons
                'polarizability': 3.0,
                'transition_temperature': 1e9,
            },
            'Lambda Baryon': {
                'quarks': ['Up Quark', 'Down Quark', 'Strange Quark'],
                'color': 'green',
                'temperature': 300,
                'internal_energy': 16.0,
                'entropy': 3.2,
                'heat_capacity': 3.2,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.array([0.0, 0.0, -0.61]),
                'polarizability': 3.2,
                'transition_temperature': 1e9,
            },
            'Sigma Baryon': {
                'quarks': ['Up Quark', 'Up Quark', 'Strange Quark'],
                'color': 'orange',
                'temperature': 300,
                'internal_energy': 16.5,
                'entropy': 3.3,
                'heat_capacity': 3.3,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.array([0.0, 0.0, 1.76]),
                'polarizability': 3.3,
                'transition_temperature': 1e9,
            },
            'D Meson': {
                'quarks': ['Charm Quark', 'Anti Down Quark'],
                'color': 'purple',
                'temperature': 300,
                'internal_energy': 17.0,
                'entropy': 3.4,
                'heat_capacity': 3.4,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 3.4,
                'transition_temperature': 1e9,
            },
            'B Meson': {
                'quarks': ['Bottom Quark', 'Anti Up Quark'],
                'color': 'brown',
                'temperature': 300,
                'internal_energy': 17.5,
                'entropy': 3.5,
                'heat_capacity': 3.5,
                'electric_dipole': np.zeros(3),
                'magnetic_dipole': np.zeros(3),
                'polarizability': 3.5,
                'transition_temperature': 1e9,
            },
        }

        # Compile particle names and count
        self.particle_names = list(self.particles.keys()) + list(self.bosons.keys()) + list(self.neutrinos.keys())
        self.num_particles = len(self.particle_names)

        # Initialize gravitational curvature model via composition
        self.gravitational_model = ElasticGravitationalCurvatureModel(G, c, self.num_particles, time_step, num_steps)

        # Initialize particle properties
        self.positions = np.zeros((self.num_particles, 3))
        self.velocities = np.zeros((self.num_particles, 3))
        self.masses = np.zeros(self.num_particles)
        self.charges = np.zeros(self.num_particles)
        self.colors = []
        self.temperatures = np.zeros(self.num_particles)
        self.internal_energies = np.zeros(self.num_particles)
        self.entropies = np.zeros(self.num_particles)
        self.heat_capacities = np.zeros(self.num_particles)
        self.electric_dipoles = np.zeros((self.num_particles, 3))
        self.magnetic_dipoles = np.zeros((self.num_particles, 3))
        self.polarizabilities = np.zeros(self.num_particles)
        self.transition_temperatures = np.zeros(self.num_particles)
        self.initialize_particles()

        # Initialize dipole logs
        self.electric_dipoles_over_time = [self.electric_dipoles.copy()]
        self.magnetic_dipoles_over_time = [self.magnetic_dipoles.copy()]

    def initialize_particles(self):
        """
        Initialize particle properties including positions, velocities, masses, charges, and other attributes.
        """
        for i, name in enumerate(self.particle_names):
            if name in self.particles:
                particle_data = self.particles[name]
                # Sum the masses and charges of constituent quarks
                mass = sum(self.quarks[quark]['mass'] for quark in particle_data['quarks'])
                charge = sum(self.quarks[quark]['charge'] for quark in particle_data['quarks'])
                color = particle_data['color']
                temperature = particle_data.get('temperature', 300)
                internal_energy = particle_data.get('internal_energy', 5.0)
                entropy = particle_data.get('entropy', 1.0)
                heat_capacity = particle_data.get('heat_capacity', 1.0)
                electric_dipole = particle_data.get('electric_dipole', np.zeros(3))
                magnetic_dipole = particle_data.get('magnetic_dipole', np.zeros(3))
                polarizability = particle_data.get('polarizability', 1.0)
                transition_temperature = particle_data.get('transition_temperature', 0.0)
            elif name in self.bosons:
                particle_data = self.bosons[name]
                mass = particle_data['mass']
                charge = particle_data['charge']
                color = particle_data['color']
                temperature = particle_data.get('temperature', 300)
                internal_energy = particle_data.get('internal_energy', 10.0)
                entropy = particle_data.get('entropy', 2.0)
                heat_capacity = particle_data.get('heat_capacity', 2.0)
                electric_dipole = particle_data.get('electric_dipole', np.zeros(3))
                magnetic_dipole = particle_data.get('magnetic_dipole', np.zeros(3))
                polarizability = particle_data.get('polarizability', 2.0)
                transition_temperature = particle_data.get('transition_temperature', 0.0)
            elif name in self.neutrinos:
                particle_data = self.neutrinos[name]
                mass = particle_data['mass']
                charge = particle_data['charge']
                color = particle_data['color']
                temperature = particle_data.get('temperature', 300)
                internal_energy = particle_data.get('internal_energy', 3.0)
                entropy = particle_data.get('entropy', 0.5)
                heat_capacity = particle_data.get('heat_capacity', 0.5)
                electric_dipole = particle_data.get('electric_dipole', np.zeros(3))
                magnetic_dipole = particle_data.get('magnetic_dipole', np.zeros(3))
                polarizability = particle_data.get('polarizability', 0.5)
                transition_temperature = particle_data.get('transition_temperature', 0.0)
            else:
                continue  # Unknown particle

            # Assign random initial positions and velocities
            self.positions[i] = np.random.uniform(-1e-7, 1e-7, 3)  # Increased range to 10 micrometers
            self.velocities[i] = np.random.uniform(-1e-4, 1e-4, 3)  # Slightly increased velocity range
            self.masses[i] = mass * 1.78266192e-27  # Convert GeV/c^2 to kg
            self.charges[i] = charge
            self.colors.append(color)
            self.temperatures[i] = temperature
            self.internal_energies[i] = internal_energy
            self.entropies[i] = entropy
            self.heat_capacities[i] = heat_capacity
            self.electric_dipoles[i] = electric_dipole
            self.magnetic_dipoles[i] = magnetic_dipole
            self.polarizabilities[i] = polarizability
            self.transition_temperatures[i] = transition_temperature

    # Delegate gravitational-related methods to the gravitational model
    def compute_acceleration(self, positions, masses, charges, velocities, magnetic_field=np.array([0.0, 0.0, 0.0]), time=0.0):
        """
        Compute accelerations due to gravitational and electromagnetic forces.

        Parameters:
            positions (ndarray): Current positions of particles.
            masses (ndarray): Masses of particles.
            charges (ndarray): Electric charges of particles.
            velocities (ndarray): Current velocities of particles.
            magnetic_field (ndarray): External magnetic field vector.
            time (float): Current simulation time.

        Returns:
            accelerations (ndarray): Computed accelerations for each particle.
        """
        return self.gravitational_model.compute_acceleration(
            positions, masses, charges, velocities, magnetic_field, time
        )

    def fp(self, f, f_unit_scale=1.0, frequency=1.0, time=0.0):
        """
        Flowpoint function utilized in gravitational computations.

        Parameters:
            f (float): Input parameter.
            f_unit_scale (float): Scaling factor for 'f'.
            frequency (float): Frequency parameter.
            time (float): Current simulation time.

        Returns:
            fp_value (float): Computed flowpoint value.
        """
        return self.gravitational_model.fp(f, f_unit_scale, frequency, time)

    def fp_sin_kx_wt(self, x, t):
        """
        Compute fp_sin(kx + wt) using the gravitational model.

        Parameters:
            x (float): Spatial coordinate.
            t (float): Current simulation time.

        Returns:
            fp_value (float): Computed value.
        """
        return self.gravitational_model.fp_sin_kx_wt(x, t)

    def fp_cos_kx_wt(self, x, t):
        """
        Compute fp_cos(kx + wt) using the gravitational model.

        Parameters:
            x (float): Spatial coordinate.
            t (float): Current simulation time.

        Returns:
            fp_value (float): Computed value.
        """
        return self.gravitational_model.fp_cos_kx_wt(x, t)
    
    def fp_tan_kx_wt(self, x, t):
        """
        Compute fp_tan(kx + wt) using the gravitational model.

        Parameters:
            x (float): Spatial coordinate.
            t (float): Current simulation time.

        Returns:
            fp_value (float): Computed value.
        """
        return self.gravitational_model.fp_tan_kx_wt(x, t)
    
    def compute_gravitational_curvature(self, x, y, z, t):
        """
        Apply gravitational curvature to a particle's position.

        Parameters:
            x (float): X-coordinate.
            y (float): Y-coordinate.
            z (float): Z-coordinate.
            t (float): Current simulation time.

        Returns:
            ndarray: Curved position vector.
        """
        return self.gravitational_model.compute_gravitational_curvature(x, y, z, t)

    def update_mass_energy(self, mass, energy, fp_value):
        """
        Update mass and energy based on flowpoint interactions.

        Parameters:
            mass (float): Current mass.
            energy (float): Current energy.
            fp_value (float): Flowpoint value.

        Returns:
            (float, float): Updated mass and energy.
        """
        return self.gravitational_model.update_mass_energy(mass, energy, fp_value)

    def run_additional_mass_energy_updates(self, t, positions):
        self.gravitational_model.run_additional_mass_energy_updates(t, positions)

    def fp_temperature(self, temperature, transition_temp, f_unit_scale=1.0, frequency=1.0, time=0.0):
        """
        Flowpoint function for temperature-dependent property changes.

        Parameters:
            temperature (float): Current temperature.
            transition_temp (float): Transition temperature.
            f_unit_scale (float): Scaling factor for 'f'.
            frequency (float): Frequency parameter.
            time (float): Current simulation time.

        Returns:
            fp_value (float): Computed flowpoint value.
        """
        return self.gravitational_model.fp_temperature(temperature, transition_temp, f_unit_scale, frequency, time)

    def update_properties(self, i, time):
        """
        Update properties of a particle based on its temperature.

        Parameters:
            i (int): Index of the particle.
            time (float): Current simulation time.
        """
        temperature = self.temperatures[i]
        transition_temp = self.transition_temperatures[i]

        if transition_temp > 0:
            # Use fp_temperature instead of fp
            transition_factor = self.fp_temperature(
                temperature, transition_temp,
                f_unit_scale=0.01,
                frequency=0.1,
                time=time
            )
            self.magnetic_dipoles[i] *= (1 - np.tanh(transition_factor))
            self.polarizabilities[i] *= (1 - np.tanh(transition_factor))

    def apply_heat(self, i, heat_energy):
        """
        Apply heat energy to a particle, updating its temperature.

        Parameters:
            i (int): Index of the particle.
            heat_energy (float): Amount of heat energy in Joules.
        """
        self.temperatures[i] += heat_energy / (self.masses[i] * self.heat_capacities[i])

    def compute_fp_elasticity(self, time, weight=1.0):
        """
        Compute elasticity based on flowpoint functions.

        Parameters:
            time (float): Current simulation time.
            weight (float): Weighting factor, typically the mass of the particle.

        Returns:
            ndarray: Elasticity vector.
        """
        curvature_x = self.fp(0.05 * time, f_unit_scale=0.1, frequency=1.0, time=time) + \
                    self.fp(0.1 * time, f_unit_scale=0.05, frequency=2.0, time=time)
        curvature_y = self.fp(0.05 * time + np.pi / 3, f_unit_scale=0.1, frequency=1.0, time=time) + \
                    self.fp(0.02 * time, f_unit_scale=0.05, frequency=0.5, time=time)
        curvature_z = self.fp(0.05 * time + 2 * np.pi / 3, f_unit_scale=0.1, frequency=1.0, time=time) + \
                    self.fp(0.15 * time, f_unit_scale=0.05, frequency=3.0, time=time)
        return np.array([curvature_x, curvature_y, curvature_z])

    def apply_charge_separation(self, time, separation_strength, dt):
            pos_indices, neg_indices = self.categorize_particles_by_charge()
            separation_vector = self.fp(time, f_unit_scale=0.1, frequency=1.0, time=time) * separation_strength
            for i in pos_indices:
                self.positions[i] += separation_vector * self.heat_capacities[i] * dt
            for i in neg_indices:
                self.positions[i] -= separation_vector * self.heat_capacities[i] * dt

    def categorize_particles_by_charge(self):
        """
        Categorize particles into positive and negative charges.

        Returns:
            pos_indices (list): Indices of positively charged particles.
            neg_indices (list): Indices of negatively charged particles.
        """
        pos_indices = [i for i, q in enumerate(self.charges) if q > 0]
        neg_indices = [i for i, q in enumerate(self.charges) if q < 0]
        return pos_indices, neg_indices

    def simulate(self, total_time, time_step):
        """
        Simulate the particles over time, updating their properties.

        Parameters:
            total_time (float): Total simulation time.
            time_step (float): Time step for the simulation.
        """
        num_steps = int(total_time / time_step)
        for step in tqdm(range(num_steps), desc="Simulating Particles"):
            time = step * time_step
            for i in range(self.num_particles):
                # Apply heat (example: heating particles over time)
                self.apply_heat(i, heat_energy=1e-21 * time_step)  # Adjust heat energy as needed

                # Update properties based on temperature
                self.update_properties(i, time)

                # Update positions based on elasticity
                elasticity = self.compute_fp_elasticity(time, weight=self.masses[i])
                self.positions[i] += elasticity * time_step

            # Compute accelerations due to gravitational and electromagnetic forces
            accelerations = self.compute_acceleration(
                self.positions, self.masses, self.charges, self.velocities, time=time
            )

            # Update velocities
            self.velocities += accelerations * time_step

            # Update positions based on velocities
            self.positions += self.velocities * time_step

            # Apply gravitational curvature to each particle
            for i in range(self.num_particles):
                x, y, z = self.positions[i]
                self.positions[i] = self.compute_gravitational_curvature(x, y, z, time)

            # Detect and handle collisions
            collisions = self.detect_collisions(self.positions)
            if collisions:
                self.handle_collisions(collisions, self.velocities, self.masses, self.internal_energies)

            # Apply charge-based separation
            self.apply_charge_separation(time=time, separation_strength=1.0, dt=time_step)

            # Update mass and energy based on position and time
            self.run_additional_mass_energy_updates(time)

            # Log positions, velocities, temperatures, and internal energies
            self.positions_over_time.append(self.positions.copy())
            self.velocities_over_time.append(self.velocities.copy())
            self.temperatures_over_time.append(self.temperatures.copy())
            self.internal_energies_over_time.append(self.internal_energies.copy())
            self.entropies_over_time.append(self.entropies.copy())
            self.electric_dipoles_over_time.append(self.electric_dipoles.copy())
            self.magnetic_dipoles_over_time.append(self.magnetic_dipoles.copy())

    def get_particle_charges(self):
        """
        Retrieve electric charges of all particles.

        Returns:
            ndarray: Array of electric charges.
        """
        return self.charges.copy()

    def detect_collisions(self, positions, collision_distance=1e-10):
        """
        Detect collisions between particles.

        Parameters:
            positions (ndarray): Positions of particles.
            collision_distance (float): Distance threshold for collisions.

        Returns:
            collisions (list of tuples): List of particle index pairs that have collided.
        """
        collisions = []
        num_particles = positions.shape[0]
        for i in range(num_particles):
            for j in range(i + 1, num_particles):
                if np.linalg.norm(positions[i] - positions[j]) < collision_distance:
                    collisions.append((i, j))
        return collisions

    def handle_collisions(self, collisions, velocities, masses, internal_energies):
        """
        Handle energy exchange due to collisions.

        Parameters:
            collisions (list of tuples): Particle index pairs that have collided.
            velocities (ndarray): Current velocities of particles.
            masses (ndarray): Masses of particles.
            internal_energies (ndarray): Internal energies of particles.
        """
        for (i, j) in collisions:
            # Simple inelastic collision: particles stick together
            # Update internal energies based on kinetic energy loss
            relative_velocity = velocities[i] - velocities[j]
            relative_speed = np.linalg.norm(relative_velocity)
            kinetic_energy = 0.5 * masses[i] * relative_speed**2

            # Assume a fraction of kinetic energy is converted to internal energy
            energy_transfer = 0.1 * kinetic_energy  # 10% conversion
            internal_energies[i] += energy_transfer
            internal_energies[j] += energy_transfer

            # Update temperatures based on internal energy (simplified)
            self.temperatures[i] += energy_transfer / self.heat_capacities[i]
            self.temperatures[j] += energy_transfer / self.heat_capacities[j]

    def get_particle_info(self):
        """
        Retrieve particle information for analysis or visualization.

        Returns:
            info (list): List of dictionaries containing particle information.
        """
        info = []
        for i in range(self.num_particles):
            particle_info = {
                'name': self.particle_names[i],
                'position': self.positions[i],
                'velocity': self.velocities[i],
                'mass': self.masses[i],
                'charge': self.charges[i],
                'magnetic_dipole': self.magnetic_dipoles[i],
                'temperature': self.temperatures[i],
                'color': self.colors[i],
            }
            info.append(particle_info)
        return info
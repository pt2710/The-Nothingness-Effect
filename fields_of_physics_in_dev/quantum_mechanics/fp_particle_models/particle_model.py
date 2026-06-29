"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import numpy as np

class FPParticleModel:
    def __init__(self):
        # Define quarks with their properties
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

        # Map particle names to indices
        self.particle_names = list(self.particles.keys()) + list(self.bosons.keys()) + list(self.neutrinos.keys())
        self.num_particles = len(self.particle_names)

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

    def initialize_particles(self):
        # Initialize positions, velocities, masses, charges, and colors
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

            # Random initial positions and velocities
            self.positions[i] = np.random.uniform(-1e-9, 1e-9, 3)
            self.velocities[i] = np.random.uniform(-1e3, 1e3, 3)
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

    def fp(self, temperature, transition_temp, f_unit_scale=1.0, frequency=1.0, time=0.0):
        """
        Flowpoint function to model property changes based on temperature.

        Parameters:
            temperature (float): Current temperature of the particle.
            transition_temp (float): Transition temperature for property change.
            f_unit_scale (float): Scaling factor for the function.
            frequency (float): Frequency for the trigonometric component.
            time (float): Current simulation time.

        Returns:
            fp_value (float): Output of the flowpoint function.
        """
        delta_temp = temperature - transition_temp
        f_scaled = delta_temp * f_unit_scale
        logical_component = ((f_scaled != -f_scaled)**(f_scaled == -f_scaled)) ** \
                            ((-f_scaled != f_scaled) ** (-f_scaled == f_scaled))
        trigonometric_component = (np.sin(frequency * f_scaled + time) +
                                   0.5 * np.cos(2 * frequency * f_scaled + time) +
                                   0.25 * np.tan(0.5 * frequency * f_scaled + time))
        fp_value = logical_component * trigonometric_component
        return fp_value

    def update_properties(self, i, time):
        """
        Update properties of particles based on temperature using the fp function.

        Parameters:
            i (int): Index of the particle.
            time (float): Current simulation time.
        """
        temperature = self.temperatures[i]
        transition_temp = self.transition_temperatures[i]

        if transition_temp > 0:
            # Use the fp function to model the change in magnetic dipole moment
            transition_factor = self.fp(temperature, transition_temp, f_unit_scale=0.01, frequency=0.1, time=time)
            # Adjust magnetic dipole moment based on transition_factor
            self.magnetic_dipoles[i] *= (1 - np.tanh(transition_factor))

            # Optionally, adjust other properties like polarizability
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
        # Compute the FP elasticity for position updates
        curvature_x = self.fp(0.05 * time, 0.1, 1.0, time, weight) + \
                      self.fp(0.1 * time, 0.05, 2.0, time, weight)
        curvature_y = self.fp(0.05 * time + np.pi / 3, 0.1, 1.0, time, weight) + \
                      self.fp(0.02 * time, 0.05, 0.5, time, weight)
        curvature_z = self.fp(0.05 * time + 2 * np.pi / 3, 0.1, 1.0, time, weight) + \
                      self.fp(0.15 * time, 0.05, 3.0, time, weight)
        return np.array([curvature_x, curvature_y, curvature_z])

    def simulate(self, total_time, time_step):
        """
        Simulate the particles over time, updating their properties.

        Parameters:
            total_time (float): Total simulation time.
            time_step (float): Time step for the simulation.
        """
        num_steps = int(total_time / time_step)
        for step in range(num_steps):
            time = step * time_step
            for i in range(self.num_particles):
                # Apply heat (example: heating particles over time)
                self.apply_heat(i, heat_energy=1e-21 * time_step)  # Adjust heat energy as needed

                # Update properties based on temperature
                self.update_properties(i, time)

                # Update positions
                elasticity = self.compute_fp_elasticity(time, weight=self.masses[i])
                self.positions[i] += elasticity * time_step

    def get_particle_charges(self):
        # Retrieve electric charges of all particles
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

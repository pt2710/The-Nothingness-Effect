"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import os
import numpy as np

class ElasticGravitationalCurvatureModel:
    def __init__(self, G, c, num_particles, time_step, num_steps):
        self.G = G
        self.c = c
        self.num_particles = num_particles
        self.time_step = time_step
        self.num_steps = num_steps

        # Add these lines to initialize masses and internal_energies
        self.masses = np.zeros(num_particles)
        self.internal_energies = np.zeros(num_particles)

        # Data storage for simulation
        self.positions_over_time = []
        self.velocities_over_time = []
        self.masses_over_time = []
        self.energies_over_time = []

    def initialize_simulation(self, positions, velocities, masses, colors, temperatures, internal_energies, entropies, heat_capacities, electric_dipoles, magnetic_dipoles, polarizabilities):
        # Initialize simulation variables
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

    def compute_acceleration(self, positions, masses, charges, velocities, magnetic_field=np.array([0.0, 0.0, 0.0]), time=0.0):
        """
        Compute gravitational and electromagnetic accelerations, incorporating fp function.

        Parameters:
            positions (ndarray): Positions of particles.
            masses (ndarray): Masses of particles.
            charges (ndarray): Electric charges of particles.
            velocities (ndarray): Velocities of particles.
            magnetic_field (ndarray): External magnetic field (optional).
            time (float): Current simulation time.

        Returns:
            accelerations (ndarray): Accelerations of particles.
        """
        num_particles = positions.shape[0]
        accelerations = np.zeros_like(positions)

        # Constants
        G_effective = self.G * 1e20  # Gravitational constant scaling for visualization
        K_e = 8.9875517873681764e9  # Coulomb's constant

        for i in range(num_particles):
            if masses[i] == 0:
                continue  # Skip massless particles

            total_force = np.zeros(3)

            for j in range(num_particles):
                if i == j or masses[j] == 0:
                    continue  # Skip self-interaction and massless particles

                # Vector from i to j
                r_vec = positions[j] - positions[i]
                r_mag = np.linalg.norm(r_vec) + 1e-12  # Avoid division by zero
                r_hat = r_vec / r_mag

                # Compute fp value based on distance and time
                fp_value = self.fp(r_mag, f_unit_scale=1e10, frequency=1e-12, time=time)

                # Gravitational Force with fp modulation
                F_grav = fp_value * G_effective * masses[i] * masses[j] / r_mag**2 * r_hat

                # Electromagnetic Force (Coulomb's Law) with fp modulation
                F_elec = fp_value * K_e * charges[i] * charges[j] / r_mag**2 * r_hat

                # Total Force
                total_force += F_grav + F_elec

            # Lorentz Force (if magnetic field is present)
            F_lorentz = charges[i] * np.cross(velocities[i], magnetic_field)

            # Total Acceleration
            accelerations[i] += (total_force + F_lorentz) / masses[i]

        return accelerations

    def fp(self, f, f_unit_scale=1.0, frequency=1.0, time=0.0):
        # Flowpoint function for gravitational curvature
        f_scaled = f * f_unit_scale
        logical_component = ((f_scaled != -f_scaled) ** (f_scaled == -f_scaled)) ** ((-f_scaled != f_scaled) ** (-f_scaled == f_scaled))
        trigonometric_component = (np.sin(frequency * f_scaled + time) +
                                   0.5 * np.cos(2 * frequency * f_scaled + time) +
                                   0.25 * np.tan(0.5 * frequency * f_scaled + time))
        fp_value = logical_component * trigonometric_component
        return fp_value

    def fp_sin_kx_wt(self, x, t):
        """
        Compute fp_sin(kx + wt) using the fp function.
        """
        k = 1e-11  # Wave number
        omega = 1e-14  # Angular frequency
        f = k * x + omega * t
        return self.fp(f)

    def fp_cos_kx_wt(self, x, t):
        """
        Compute fp_cos(kx + wt) using the fp function.
        """
        k = 1e-11  # Wave number
        omega = 1e-14  # Angular frequency
        f = k * x + omega * t
        return self.fp(f + np.pi/2)

    def fp_tan_kx_wt(self, x, t):
        """
        Compute fp_tan(kx + wt) using the fp function.
        """
        k = 1e-11  # Wave number
        omega = 1e-14  # Angular frequency
        f = k * x + omega * t
        return self.fp(f) / self.fp(f + np.pi/2)

    def update_mass_energy(self, mass, energy, fp_value):
        """
        Update mass and energy of particles based on fp interactions.
        """
        # Define the magnitude of mass-energy fluctuation
        delta_E = fp_value * 1e30  # Adjust scaling factor as needed

        # Update energy
        energy_new = energy + delta_E

        # Ensure energy remains positive to avoid non-physical negative masses
        energy_new = np.where(energy_new > 0, energy_new, energy)

        # Update mass using E=mc^2
        mass_new = energy_new / self.c**2

        return mass_new, energy_new

    def compute_gravitational_curvature(self, x, y, z, t):
        # Apply curvature using fp functions
        curvature_x = self.fp_sin_kx_wt(0.05 * t, t)
        curvature_y = self.fp_cos_kx_wt(0.05 * t + np.pi / 3, t)
        curvature_z = self.fp_tan_kx_wt(0.05 * t + 2 * np.pi / 3, t)
        x_curved = x + curvature_x
        y_curved = y + curvature_y
        z_curved = z + curvature_z
        return np.array([x_curved, y_curved, z_curved])
    
    def run_additional_mass_energy_updates(self, t, positions):
        self.positions = positions 
        for i in range(self.num_particles):
            x, y, z = self.positions[i]
            fp_x = self.fp_sin_kx_wt(x, t)
            fp_y = self.fp_cos_kx_wt(y, t)
            fp_z = self.fp_tan_kx_wt(z, t)
    
            fp_total = fp_x + fp_y + fp_z
            mass, energy = self.update_mass_energy(
                self.masses[i], self.internal_energies[i], fp_total
            )
            self.masses[i] = mass
            self.internal_energies[i] = energy
    
        self.masses_over_time.append(self.masses.copy())
        self.energies_over_time.append(self.internal_energies.copy())

    def get_particle_charges(self):
        # Retrieve electric charges of all particles
        return self.charges.copy()

    def detect_collisions(self, positions, collision_distance=1e-10):
        # Collision detection method (can be implemented similarly as in FPParticleModel)
        pass  # Replace with actual method code

    def handle_collisions(self, collisions, velocities, masses, internal_energies):
        # Collision handling method (can be implemented similarly as in FPParticleModel)
        pass  # Replace with actual method code

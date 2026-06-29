"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
num_particles = 5000  # Number of particles
slit_width = 0.1      # Width of each slit
slit_gap = 0.4        # Gap between slits
screen_distance = 1.0 # Distance from slits to screen
observation_level = 0.25  # Static (-1) to Dynamic (1.0)

# Generate particles passing through slits
def generate_particles(num_particles, observation_level):
    positions = []
    for _ in range(num_particles):
        slit_choice = np.random.choice([-1, 1])  
        if observation_level < 0:  # Low observation: wave-like behavior
            offset = np.random.uniform(-slit_width/2, slit_width/2)
            angle = np.random.uniform(-np.pi/12, np.pi/12) * (1 + observation_level)
        else:  # High observation: particle-like behavior
            offset = 0
            angle = np.random.uniform(-np.pi/24, np.pi/24) * (1 - observation_level)
        
        positions.append((slit_choice * slit_gap / 2 + offset, angle))
    return np.array(positions)

# Simulate particle trajectories
def simulate_trajectories(positions, screen_distance):
    screen_hits = []
    for pos, angle in positions:
        screen_x = pos + screen_distance * np.tan(angle)
        screen_hits.append(screen_x)
    return np.array(screen_hits)

# Visualization setup
particles = generate_particles(num_particles, observation_level)
screen_hits = simulate_trajectories(particles, screen_distance)

# Plotting the results
plt.figure(figsize=(10, 6))
plt.hist(screen_hits, bins=100, color='blue', alpha=0.7, label='Particle Impact')
plt.title('Double-Slit Experiment Simulation')
plt.xlabel('Screen Position')
plt.ylabel('Impact Count')
plt.axvline(x=0, color='red', linestyle='--', label='Central Axis')
plt.legend()
plt.grid(True)
plt.show()

"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

3D Double-Slit Experiment Simulation with Dynamic Observation Levels

This script simulates a 3D version of the double-slit experiment to explore
how dynamic observation levels (inspired by the AC/DC analogy and 'The Nothingness Effect')
influence wave-particle behavior.

Purpose:
- To illustrate the transition from wave-like behavior (-1 observation level)
  to particle-like behavior (+1 observation level) with a neutral point (0 observation level).
- To visualize the influence of dynamic observation on particle motion and the resulting patterns.

AC/DC Analogy:
- Alternating Current (AC): Represents wave-like functionality where the particle's behavior is 
  distributed probabilistically across space, similar to how AC oscillates between polarities.
- Direct Current (DC): Represents the observed collapse, where the particle's position is fixed 
  to a specific state, akin to DC's constant and directed flow.
- This analogy highlights how observation acts as a "switch" between these two behaviors.

Success Criteria:
1. At observation level -1:
   - The simulation should show interference patterns, indicating wave-like behavior.
2. At observation level 0:
   - The simulation should represent a neutral system with minimal particle dynamics.
3. At observation level +1:
   - The simulation should display particle-like behavior, with sharp clusters on the screen.
4. Dynamic transitions:
   - The simulation should show smooth transitions between wave-like and particle-like behavior
     as the observation level changes over time.
5. Output:
   - A clear and accurate animation is generated as 'ac_dc_observation_simulation.gif'.

"""


import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation, PillowWriter

# Simulation parameters
num_steps = 1000  
slit_gap = 0.4    
slit_height = 0.2   
slit_width = 0.05 
source_to_slit_distance = 5.0  
slit_to_screen_distance = 10.0 
particle_source = (0, 0, 0) 
slit_distance = source_to_slit_distance
screen_distance = slit_distance + slit_to_screen_distance
batch_size = 50  

def dynamic_observation_level(frame, num_steps):
    """
    Dynamically adjusts the observation level based on the frame index.

    Parameters:
    - frame (int): Current frame index in the animation.
    - num_steps (int): Total number of frames in the simulation.

    Returns:
    - float: Observation level, transitioning from -1 to +1.
    """
    if frame <= num_steps // 2:
        return -1.0 + (frame / (num_steps // 2)) 
    else:
        return (frame - num_steps // 2) / (num_steps // 2) 

def generate_batch_particles(batch_size, observation_level):
    """
    Generates particles and determines their initial trajectories based on the observation level.

    Parameters:
    - batch_size (int): Number of particles to generate in this batch.
    - observation_level (float): Current observation level [-1, 1].

    Returns:
    - np.ndarray: Array containing particle positions and angles.
    """
    slit_choices = np.random.choice([-1, 1], size=batch_size)  
    x_offsets = np.random.uniform(-slit_width / 2, slit_width / 2, size=batch_size)
    y_offsets = np.random.uniform(-slit_height / 2, slit_height / 2, size=batch_size)

    if observation_level < 0:  # Wave-like behavior
        angles_x = np.random.uniform(-np.pi/12, np.pi/12, size=batch_size) * (1 + observation_level)
        angles_y = np.random.uniform(-np.pi/12, np.pi/12, size=batch_size) * (1 + observation_level)
    elif observation_level > 0:  # Particle-like behavior
        angles_x = np.random.uniform(-np.pi/24, np.pi/24, size=batch_size) * (1 - observation_level)
        angles_y = np.random.uniform(-np.pi/24, np.pi/24, size=batch_size) * (1 - observation_level)
    else:  # Neutral system
        angles_x = np.zeros(batch_size)
        angles_y = np.zeros(batch_size)

    return np.column_stack((
        np.full(batch_size, particle_source[0]),
        np.full(batch_size, particle_source[1]),
        np.full(batch_size, particle_source[2]),
        slit_choices * slit_gap / 2 + x_offsets,
        y_offsets,
        angles_x,
        angles_y
    ))

def simulate_batch_trajectories(particles, slit_distance, screen_distance):
    """
    Simulates particle trajectories through the slits and onto the screen.

    Parameters:
    - particles (np.ndarray): Array of particle positions and angles.
    - slit_distance (float): Z-coordinate of the slits.
    - screen_distance (float): Z-coordinate of the screen.

    Returns:
    - np.ndarray: Particle trajectories from source to screen.
    - np.ndarray: Final screen hit positions.
    """
    slit_z = slit_distance
    screen_z = screen_distance

    slit_x = particles[:, 3]
    slit_y = particles[:, 4]

    screen_x = slit_x + (screen_z - slit_z) * np.tan(particles[:, 5])
    screen_y = slit_y + (screen_z - slit_z) * np.tan(particles[:, 6])

    trajectories = np.column_stack((
        np.full((particles.shape[0], 3), particle_source),
        np.column_stack((slit_x, slit_y, np.full(particles.shape[0], slit_z))),
        np.column_stack((screen_x, screen_y, np.full(particles.shape[0], screen_z)))
    )).reshape(-1, 3, 3)

    return trajectories, np.column_stack((screen_x, screen_y, np.full(particles.shape[0], screen_z)))

# Setup for 3D plotting
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([0, screen_distance + 5])

trajectories = []
screen_hits = []

start_time = time.time()

def update(frame):
    """
    Updates the animation frame-by-frame.

    Parameters:
    - frame (int): Current frame index.

    Updates global variables:
    - trajectories: Stores all particle trajectories.
    - screen_hits: Stores particle hit positions on the screen.
    """
    global trajectories, screen_hits

    current_observation_level = dynamic_observation_level(frame, num_steps)
    particles = generate_batch_particles(batch_size, current_observation_level)
    batch_trajectories, batch_screen_hits = simulate_batch_trajectories(particles, slit_distance, screen_distance)

    trajectories.extend(batch_trajectories)
    screen_hits.extend(batch_screen_hits)

    ax.cla()

    for traj in trajectories:
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 'g-', alpha=0.2)

    hits = np.array(screen_hits)
    ax.scatter(hits[:, 0], hits[:, 1], hits[:, 2], c='blue', alpha=0.6, label='Screen Hits')
    ax.scatter(*particle_source, c='black', s=100, label='Particle Source')

    for slit_pos in [-slit_gap / 2, slit_gap / 2]:
        x_rect = [slit_pos - slit_width / 2, slit_pos + slit_width / 2, slit_pos + slit_width / 2, slit_pos - slit_width / 2, slit_pos - slit_width / 2]
        y_rect = [-slit_height / 2, -slit_height / 2, slit_height / 2, slit_height / 2, -slit_height / 2]
        z_rect = [slit_distance] * 5
        ax.plot(x_rect, y_rect, z_rect, 'k-', lw=2)

    ax.text2D(0.05, 0.95, f"Observation Level: {current_observation_level:.2f}", transform=ax.transAxes, fontsize=12, color='red')

    ax.set_title('3D Double-Slit Experiment with AC/DC Observation Transition')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_zlabel('Z Position')
    ax.legend()

    if frame % 10 == 0:
        elapsed_time = time.time() - start_time
        frames_processed = (frame + 1) * batch_size
        avg_time_per_particle = elapsed_time / frames_processed
        estimated_time_remaining = avg_time_per_particle * (num_steps - frames_processed)
        print(f"Processed {frames_processed}/{num_steps} particles: Elapsed Time = {elapsed_time:.2f}s, "
              f"Estimated Remaining Time = {estimated_time_remaining:.2f}s")

anim = FuncAnimation(fig, update, frames=num_steps // batch_size, interval=100)
anim.save('ac_dc_observation_simulation_with_docstrings.gif', writer=PillowWriter(fps=30))
plt.show()

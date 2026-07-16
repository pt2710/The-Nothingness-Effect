"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
from entanglement_model import EntanglementModel
import plotly.graph_objects as go
import imageio.v2 as imageio
import numpy as np

# Define constants and parameters
G = 6.67430e-11       # Gravitational constant
c = 299792458         # Speed of light
time_step = 1e-15     # Increased time step
num_steps = 500       # Increased number of steps

# Initialize the entanglement model
entanglement_model = EntanglementModel(G, c, time_step, num_steps)

# Define entangled pairs (ensure indices are valid)
entanglement_model.entangled_pairs = [(0, 1), (2, 3)]

# Run the simulation
entanglement_model.run_simulation()

# Retrieve simulation data
simulation_data = entanglement_model.get_simulation_data()
positions_over_time = simulation_data['positions']
velocities_over_time = simulation_data['velocities']
temperatures_over_time = simulation_data['temperatures']
internal_energies_over_time = simulation_data['internal_energies']
entropies_over_time = simulation_data['entropies']
electric_dipoles_over_time = simulation_data['electric_dipoles']
magnetic_dipoles_over_time = simulation_data['magnetic_dipoles']
particle_names = simulation_data['particle_names']
entangled_pairs = simulation_data['entangled_pairs']

def create_visualizations():
    print("Starting visualization creation...")
    frames = []
    num_frames = len(positions_over_time)
    print(f"Number of frames: {len(positions_over_time)}")

    # Calculate appropriate axis range
    all_positions = np.array(positions_over_time).reshape(-1, 3)
    axis_range = np.max(np.abs(all_positions)) * 1.1  # Add 10% padding

    # Define frame dimensions
    frame_width = 1024
    frame_height = 1024

    # Create directory to store frame images
    if not os.path.exists('frames'):
        os.makedirs('frames')

    # Ensure the 'entanglement' directory exists
    output_dir = 'fields_of_physics/quantum_mechanics/entanglement'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    scale_factor = 1e7  # Adjusted scale factor

    # Define distinct colors for particles
    colors = ['red', 'green', 'blue', 'orange', 'purple', 'brown', 'cyan', 'magenta', 'yellow', 'black']

    for frame in tqdm(range(num_frames), desc="Creating Frames"):
        positions = positions_over_time[frame]
        fig = go.Figure()

        # Plot particles with labels and distinct colors
        for i in range(len(positions)):
            fig.add_trace(go.Scatter3d(
                x=[positions[i][0] * scale_factor],
                y=[positions[i][1] * scale_factor],
                z=[positions[i][2] * scale_factor],
                mode='markers+text',
                marker=dict(size=10, color=colors[i % len(colors)]),
                text=[particle_names[i]],
                textposition='top center',
                name=particle_names[i],
                showlegend=True
            ))

        # Plot entanglement lines
        for (i, j) in entangled_pairs:
            fig.add_trace(go.Scatter3d(
                x=[positions[i][0] * scale_factor, positions[j][0] * scale_factor],
                y=[positions[i][1] * scale_factor, positions[j][1] * scale_factor],
                z=[positions[i][2] * scale_factor, positions[j][2] * scale_factor],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False
            ))

        # Set layout with adjusted axis range
        fig.update_layout(
            scene=dict(
                xaxis=dict(range=[-axis_range * scale_factor, axis_range * scale_factor], title='X Axis'),
                yaxis=dict(range=[-axis_range * scale_factor, axis_range * scale_factor], title='Y Axis'),
                zaxis=dict(range=[-axis_range * scale_factor, axis_range * scale_factor], title='Z Axis'),
                aspectmode='cube',
                bgcolor='white'
            ),
            title=f"Quantum Entanglement Simulation - Frame {frame}",
            margin=dict(l=0, r=0, t=50, b=0),
            width=frame_width,
            height=frame_height,
            showlegend=True
        )

        # Save frame as image
        frame_filename = f"frames/frame_{frame}.png"
        try:
            fig.write_image(frame_filename)
            frames.append(imageio.imread(frame_filename))
        except Exception as e:
            print(f"Error saving frame {frame}: {e}")

    # Save as GIF
    gif_filename = os.path.join(output_dir, 'simulation.gif')
    imageio.mimsave(gif_filename, frames, fps=10)
    print("Saved simulation.gif")

    # Save as MP4
    mp4_filename = os.path.join(output_dir, 'simulation.mp4')
    imageio.mimsave(mp4_filename, frames, fps=10)
    print("Saved simulation.mp4")

    # Save a static PNG (last frame)
    png_filename = os.path.join(output_dir, 'simulation.png')
    if frames:
        last_frame = frames[-1]
        imageio.imwrite(png_filename, last_frame)
        print("Saved simulation.png")
    else:
        print("No frames to save as PNG.")

    # Save as HTML (interactive)
    if frames:
        fig.write_html(os.path.join(output_dir, 'simulation.html'))
        print("Saved simulation.html")

    # Clean up frame images
    for frame in range(num_frames):
        try:
            os.remove(f"frames/frame_{frame}.png")
        except Exception as e:
            print(f"Error removing frame {frame}: {e}")
    try:
        os.rmdir('frames')
    except Exception as e:
        print(f"Error removing 'frames' directory: {e}")

    print("Visualization saved as GIF, MP4, PNG, and HTML.")

# Create the visualizations
create_visualizations()




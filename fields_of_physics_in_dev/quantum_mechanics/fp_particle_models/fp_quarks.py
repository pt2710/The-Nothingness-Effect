"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Define unique attributes for each quark
quarks = {
    'Up Quark': {
        'mass': 2.2e-3,          # Mass in GeV/c^2
        'charge': 2/3,           # Electric charge in elementary charge units
        'color': 'blue',         # Color for plotting
        'frequency_factor': 1.0  # Frequency scaling factor based on mass
    },
    'Down Quark': {
        'mass': 4.7e-3,
        'charge': -1/3,
        'color': 'red',
        'frequency_factor': 1.1
    },
    'Charm Quark': {
        'mass': 1.28,
        'charge': 2/3,
        'color': 'green',
        'frequency_factor': 1.2
    },
    'Strange Quark': {
        'mass': 96e-3,
        'charge': -1/3,
        'color': 'orange',
        'frequency_factor': 1.3
    },
    'Top Quark': {
        'mass': 173,
        'charge': 2/3,
        'color': 'purple',
        'frequency_factor': 1.4
    },
    'Bottom Quark': {
        'mass': 4.18,
        'charge': -1/3,
        'color': 'brown',
        'frequency_factor': 1.5
    }
}

# Define the generalized flowpoint function for quarks
def fp_quark(f, scale=1.0, frequency=1.0, time=0.0):
    """
    Generalized flowpoint (fp) function for quarks.
    
    Parameters:
    - f : Position value(s) (can be a float or an array of floats)
    - scale : Amplitude scaling factor
    - frequency : Frequency of oscillation
    - time : Time parameter for dynamic adjustment
    
    Returns:
    - Flowpoint value(s) between -scale and +scale
    """
    return scale * np.sin(frequency * f + time)

# Example usage of the fp functions
f_values = np.linspace(0, 2 * np.pi, 500)  # Increased resolution for smoother plots
time = 0.0  # Initial time

# Generate fp values for each quark based on their unique attributes
fp_values = {}
for quark, attributes in quarks.items():
    # Frequency is scaled by mass and frequency_factor
    frequency = attributes['frequency_factor'] * attributes['mass']
    fp_values[quark] = fp_quark(f_values, scale=1.0, frequency=frequency, time=time)

# Plotting the fp functions for all six quarks
plt.figure(figsize=(14, 8))
for quark, values in fp_values.items():
    plt.plot(f_values, values, label=quark, color=quarks[quark]['color'])

plt.title('Flowpoint (\(fp\)) Functions for Six Quarks', fontsize=16)
plt.xlabel('Position (\(f\))', fontsize=14)
plt.ylabel('Flowpoint Value', fontsize=14)
plt.legend(fontsize=12)
plt.grid(True)
plt.tight_layout()
plt.savefig('fields_of_physics/quantum_mechanics/fp_strange-matter_and_quarks/fp_six_quarks_model.png')  # Save the plot as a PNG file
plt.show()

# Define the animation function
def animate(time_step):
    plt.clf()
    for quark, attributes in quarks.items():
        frequency = attributes['frequency_factor'] * attributes['mass']
        fp = fp_quark(f_values, scale=1.0, frequency=frequency, time=time_step)
        plt.plot(f_values, fp, label=quark, color=quarks[quark]['color'])
    plt.title('Flowpoint (\(fp\)) Functions for Six Quarks', fontsize=16)
    plt.xlabel('Position (\(f\))', fontsize=14)
    plt.ylabel('Flowpoint Value', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.ylim(-1.5, 1.5)

# Create the animation
fig = plt.figure(figsize=(14, 8))
ani = animation.FuncAnimation(fig, animate, frames=np.linspace(0, 2*np.pi, 120), interval=50)

# Save the animation as an MP4 file
ani.save('fields_of_physics/quantum_mechanics/fp_strange-matter_and_quarks/fp_six_quarks_model_animation.mp4', writer='ffmpeg')

plt.show()


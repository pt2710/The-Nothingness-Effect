# the_nothingness_effect/fields_of_physics/quantum_mechanics/wave_functionality/fp_wave_Interference/fp_wave_with_interference.py
"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

# Define the base fp_pi function
def fp_pi(f, scale=1.0, frequency=1.0, time=0.0):
    return scale * np.sin(frequency * f + time * np.pi)

def wave_interference(x, y, z, time, amplitude1=1.0, frequency1=1.0, phase1=0.0, amplitude2=1.0, frequency2=1.1, phase2=np.pi/2):
    wave1 = fp_pi(np.sqrt(x**2 + y**2 + z**2), amplitude1, frequency1, time)
    wave2 = fp_pi(np.sqrt(x**2 + y**2 + z**2), amplitude2, frequency2, time + phase2)
    
    # Superpose the two waves
    wave_total = wave1 + wave2
    return wave_total

# Set up parameters
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
z = np.zeros_like(x) 
X, Y, Z = np.meshgrid(x, y, z)
frequency1 = 1.0
frequency2 = 1.1  
phase1 = 0.0
phase2 = np.pi / 2 

# Create the figure and 3D axis for the animation
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_title("Wave Interference Using fp_pi Function")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("Amplitude")

# Set consistent Z-limits
ax.set_zlim(-3, 3)  # Adjust these limits based on the amplitudes you expect

# Initial surface plot setup
wave = wave_interference(X, Y, Z, 0, amplitude1=1.0, frequency1=frequency1, phase1=phase1,
                         amplitude2=1.0, frequency2=frequency2, phase2=phase2)
surface = ax.plot_surface(X[:, :, 0], Y[:, :, 0], wave[:, :, 0], cmap='viridis')

# Save the static plot as PNG
plt.savefig('fields_of_physics/quantum_mechanics/wave_functionality/fp_wave_Interference/wave_interference_fp_pi_static.png')

# Update function for the animation
def update(frame):
    ax.clear()
    ax.set_zlim(-3, 3) 
    wave = wave_interference(X, Y, Z, frame, amplitude1=1.0, frequency1=frequency1, phase1=phase1,
                             amplitude2=1.0, frequency2=frequency2, phase2=phase2)
    ax.plot_surface(X[:, :, 0], Y[:, :, 0], wave[:, :, 0], cmap='viridis')
    ax.set_title(f"Time = {frame}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("Amplitude")
    return surface

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=np.linspace(0, 5, 100), interval=100)

# Save the animation as a GIF
ani.save('fields_of_physics/quantum_mechanics/wave_functionality/fp_wave_Interference/wave_interference_fp_pi.gif', writer='pillow')

# Show the final plot
plt.show()
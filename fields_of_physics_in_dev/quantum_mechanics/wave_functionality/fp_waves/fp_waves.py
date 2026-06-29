"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Define the fp_pi function
def fp_pi(f, scale=1.0, frequency=1.0, time=0.0):
    return scale * np.sin(frequency * f + time * np.pi)

# Define the fp_wave_pi function
def fp_wave_pi(x, y, z, time, fp_func, amplitude=1.0, frequency=0.5, phase=0.0):
    f_cos = np.cos(frequency * x + phase + time)
    f_sin = np.sin(frequency * y + phase + time)
    f_tan = np.tan(frequency * z + phase + time)

    transformed_cos = fp_func(f_cos, time=time)
    transformed_sin = fp_func(f_sin, time=time)
    transformed_tan = fp_func(f_tan, time=time)

    wave = amplitude * (transformed_cos + transformed_sin + transformed_tan)
    wave = np.clip(wave, -1.0, 1.0)
    return wave

# Set up parameters
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
z = np.linspace(-5, 5, 100)
X, Y, Z = np.meshgrid(x, y, z)
phase_shift = np.pi / 4
frequency = 1.5

# Create the figure and axis for the animation
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_title(f"FP Wave Function Evolution with Phase Shift={phase_shift}")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_xlim([-5, 5])
ax.set_ylim([-5, 5])

# Initial plot setup
contour = ax.contourf(X[:, :, 0], Y[:, :, 0], np.zeros_like(X[:, :, 0]), cmap='RdYlBu')
colorbar = fig.colorbar(contour)

# Update function for the animation
def update(frame):
    global contour
    wave = fp_wave_pi(X, Y, Z, frame, fp_func=fp_pi, frequency=frequency, phase=phase_shift)
    
    # Remove the previous contour
    for child in ax.get_children():
        if isinstance(child, matplotlib.collections.QuadMesh):
            child.remove()
    
    # Create a new contour
    contour = ax.contourf(X[:, :, 0], Y[:, :, 0], wave[:, :, 0], cmap='RdYlBu')
    
    ax.set_title(f"Time = {frame}")
    return contour

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=np.linspace(0, 5, 100), interval=100)

# Save the animation as a GIF
ani.save('fields_of_physics/quantum_mechanics/wave_functionality/fp_waves/fp_pi_wave_animation.gif', writer='pillow')

# Save a static frame as PNG
static_frame = fp_wave_pi(X, Y, Z, 0, fp_func=fp_pi, frequency=frequency, phase=phase_shift)
plt.imshow(static_frame[:, :, 0], extent=[-5, 5, -5, 5], cmap='RdYlBu')
plt.title("Static Frame of FP Wave Function")
plt.xlabel("x")
plt.ylabel("y")
plt.colorbar(label="Amplitude")
plt.savefig('fields_of_physics/quantum_mechanics/wave_functionality/fp_waves/fp_waves_static.png')

print("Animation saved as 'fp_pi_wave_animation.gif'")
print("Static frame saved as 'fp_pi_wave_static.png'")
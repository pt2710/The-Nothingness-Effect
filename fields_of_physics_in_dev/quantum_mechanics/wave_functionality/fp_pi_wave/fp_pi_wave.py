# the_nothingness_effect/fields_of_physics/quantum_mechanics/wave_functionality/fp_pi_wave/fp_pi_wave.py
"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

"""
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

# Generate values for f and another parameter (e.g., time)
f_values = np.linspace(0, 10, 400)
time_values = np.linspace(0, 5, 400)
F, T = np.meshgrid(f_values, time_values)

# Define the fp_pi function
def fp_pi(f, scale=1.0, frequency=1.0, time=0.0):
    return scale * np.sin(frequency * f + time * np.pi)

# Compute the fp_pi function for the 3D plot
fp_pi_values_3d = fp_pi(F, scale=1.0, frequency=1.0, time=T)

# Plotting
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# 3D surface plot
ax.plot_surface(F, T, fp_pi_values_3d, cmap='viridis')

# Labels and title
ax.set_title('3D Fluctuation of fp_pi with varying time and input f')
ax.set_xlabel('f')
ax.set_ylabel('time')
ax.set_zlabel('fp_pi(f, time)')

plt.savefig('fields_of_physics/quantum_mechanics/wave_functionality/fp_pi_wave/fp_pi_3d_plot.png', dpi=300, bbox_inches='tight')
plt.show()
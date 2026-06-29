# the_nothingness_effect/fields_of_physics/quantum_mechanics/wave_functionality/fp_sine_wave/fp_sine_wave.py
"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com

...

"""
import numpy as np
import matplotlib.pyplot as plt

def fp_sine_wave(f, scale=1.0, frequency=1.0, time=0.0):
    """
    FP function that constantly fluctuates between -1.0 and 1.0.
    Parameters:
    - f: Input value (can be a float or an array of values)
    - scale: Adjusts the amplitude of fluctuation
    - frequency: Adjusts the fluctuation rate
    - time: Time parameter for dynamic adjustment
    Returns:
    - A value between -1.0 and 1.0
    """
    return scale * np.sin(frequency * f + time)

# Generate input values
x = np.linspace(0, 10, 1000)

# Calculate y values
y = fp_sine_wave(x, scale=1.0, frequency=2.0, time=0.0)

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.title('FP Sine Wave')
plt.xlabel('Input Value')
plt.ylabel('FP Output')
plt.grid(True)

# Save the plot
plt.savefig('fields_of_physics/quantum_mechanics/wave_functionality/fp_sine_wave/fp_sine_wave_plot.png')
# Show the plot
plt.show()

print("Plot saved as 'fp_sine_wave_plot.png'")
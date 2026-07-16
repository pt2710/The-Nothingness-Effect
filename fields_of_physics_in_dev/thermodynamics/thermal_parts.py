"""
Author: B. McCrackn
Email : thenothingnesseffect@gmail.com
Usage : import thermal_motor_parts

Defines the synthetic 4-cylinder engine model with dynamic thermodynamic features for simulation and entropic analysis.
"""

import os
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
def thermal_motor_parts(time_array, element_scaling_factor):
    """
    Build a dictionary modeling a 4-cylinder engine setup with 4 cylinders, 4 pistons, and 1 crankshaft.
    Each part provides 'thermo_features' as time series: Temperature, Pressure, OilTemperature, FuelFlowRate, ExhaustTemperature.

    Parameters
    ----------
    time_array : np.ndarray
        Array of time points.
    element_scaling_factor : float
        Global scaling factor for engine geometry.

    Returns
    -------
    dict
        Dictionary of parts, each mapping to their shape, position, size, and features.
    """
    phase_offsets = [0, np.pi/2, np.pi, 3*np.pi/2]
    def cyc_sin(base, amplitude, time, offset=0, period=10):
        return base + amplitude * np.sin(2 * np.pi * time / period + offset)

    def cyc_cos(base, amplitude, time, offset=0, period=10):
        return base + amplitude * np.cos(2 * np.pi * time / period + offset)

    thermal_parts = {}

    for i in range(1, 5):
        phase = phase_offsets[i-1]
        cylinder_key = f'Cylinder {i}'
        cylinder_position = (2.5 + (i-1)*3.0, 7.0)
        thermal_parts[cylinder_key] = {
            'shape': 'rectangle',
            'position': cylinder_position,
            'size': (2.0 * element_scaling_factor, 2.0 * element_scaling_factor),
            'thermo_features': {
                'Temperature': cyc_sin(300, 100, time_array, offset=phase, period=10),
                'Pressure': cyc_sin(1.0e5, 5.0e4, time_array, offset=phase + np.pi/2, period=10),
                'OilTemperature': cyc_cos(100, 10, time_array, offset=phase, period=15),
                'FuelFlowRate': cyc_sin(0.01, 0.005, time_array, offset=phase, period=8),
                'ExhaustTemperature': cyc_sin(400, 50, time_array, offset=phase + np.pi/4, period=12),
            }
        }
        piston_key = f'Piston {i}'
        piston_position = (2.5 + (i-1)*3.0, 4.5)
        thermal_parts[piston_key] = {
            'shape': 'rectangle',
            'position': piston_position,
            'size': (2.0 * element_scaling_factor, 0.5 * element_scaling_factor),
            'thermo_features': {
                'Temperature': cyc_cos(300, 50, time_array, offset=phase, period=10),
                'Pressure': cyc_cos(1.0e5, 2.0e4, time_array, offset=phase + np.pi/2, period=10),
                'OilTemperature': cyc_cos(90, 5, time_array, offset=phase + 0.2, period=15),
                'FuelFlowRate': cyc_sin(0.008, 0.003, time_array, offset=phase, period=8),
                'ExhaustTemperature': cyc_sin(350, 30, time_array, offset=phase + np.pi/3, period=12),
            }
        }

    thermal_parts['Crankshaft'] = {
        'shape': 'circle',
        'position': (6.0, 2.0),
        'size': (1.0 * element_scaling_factor, 1.5 * element_scaling_factor),
        'thermo_features': {
            'Temperature': cyc_cos(300, 30, time_array, offset=0, period=10),
            'Pressure': cyc_sin(1.0e5, 1.0e4, time_array, offset=np.pi/2, period=10),
            'OilTemperature': cyc_cos(100, 8, time_array, offset=0.5, period=15),
            'FuelFlowRate': cyc_sin(0.005, 0.001, time_array, offset=np.pi, period=8),
            'ExhaustTemperature': cyc_sin(380, 20, time_array, offset=np.pi/4, period=12),
        }
    }
    return thermal_parts

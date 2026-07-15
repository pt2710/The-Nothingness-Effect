#!/usr/bin/env python3
"""
Author: B. McCrackn
Email : thenothingnesseffect@gmail.com
Usage : python thermodynamic_simulation.py

This thermodynamic simulation uses the DynamicFluctuationIndex for entropic analysis of engine components.
It computes the Relative_Entropy and Relative_Volume time series for all features, saves results in `data_results/`,
and visualizes via ThermalEntropyVisualization. All plots/animations are saved in `visualizations/`.
"""

import os
import sys
import time
import numpy as np
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
proj_root   = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, proj_root)

from thermal_parts import thermal_motor_parts
from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.dfi import DynamicFluctuationIndex
from visualization import ThermalEntropyVisualization

def main():
    """
    Main simulation routine. Generates synthetic thermodynamic data, computes DFI entropic features,
    saves results, and visualizes all outputs.
    """
    start_time = time.time()

    # Simulation parameters
    total_frames = 500
    time_array = np.linspace(0, 50, total_frames)
    element_scaling_factor = 1.0

    # Generate synthetic data
    thermal_parts = thermal_motor_parts(time_array, element_scaling_factor)

    # Merge all features into single DataFrame
    data = {}
    for part_name, part_info in thermal_parts.items():
        for feat_name, values in part_info['thermo_features'].items():
            col = f"{part_name}__{feat_name}"
            data[col] = values
    df = pd.DataFrame(data, index=time_array)

    # Compute DFI entropic features
    dfi_engine = DynamicFluctuationIndex()
    entropic_data = dfi_engine.dfi(df)

    # Distribute entropic results back into thermal_parts
    for col, metrics in entropic_data.items():
        part_name, feat_name = col.split("__", 1)
        if part_name in thermal_parts and feat_name in thermal_parts[part_name]['thermo_features']:
            thermal_parts[part_name].setdefault('dfi', {})[feat_name] = {
                'Relative_Entropy': metrics['Relative_Entropy'],
                'Relative_Volume':  metrics['Relative_Volume']
            }

    # Output directories
    out_data_dir = os.path.join(os.path.dirname(__file__), "data_results")
    out_vis_dir  = os.path.join(os.path.dirname(__file__), "visualizations")
    os.makedirs(out_data_dir, exist_ok=True)
    os.makedirs(out_vis_dir, exist_ok=True)

    # --- FIX: Unpack entropic_data dict into long-form DataFrame ---
    rows = []
    n_steps = len(time_array)
    for col, metrics in entropic_data.items():
        part, feature = col.split("__", 1)
        for metric_name, values in metrics.items():
            for t_idx in range(n_steps):
                rows.append({
                    "time": time_array[t_idx],
                    "part": part,
                    "feature": feature,
                    "metric": metric_name,
                    "value": values[t_idx]
                })
    df_long = pd.DataFrame(rows)

    csv_path = os.path.join(out_data_dir, "entropic_dfi_data.csv")
    df_long.to_csv(csv_path, index=False)
    print(f"💾  Wrote entropic data CSV → {csv_path}")


    # Visualize results (all outputs saved to visualizations/)
    viz = ThermalEntropyVisualization(
        thermal_parts=thermal_parts,
        time_array=time_array,
        total_frames=total_frames,
        element_scaling_factor=element_scaling_factor
    )
    viz.visualize(save_static_image=True)

    elapsed = time.time() - start_time
    print(f"\nTotal execution time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()

"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
Usage: python visualization.py
"""

import io
import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from matplotlib.animation import FFMpegWriter
from tqdm import tqdm
from PIL import Image

class ThermalEntropyVisualization:
    def __init__(self, thermal_parts, time_array, total_frames, element_scaling_factor):
        """
        Visualize the distribution of five thermal features across engine components.
        """
        self.thermal_parts = thermal_parts
        self.time_array = time_array
        self.total_frames = total_frames
        self.element_scaling_factor = element_scaling_factor

        # The features to visualize
        self.features = [
            'Temperature',
            'Pressure',
            'OilTemperature',
            'FuelFlowRate',
            'ExhaustTemperature'
        ]

        # Colormap for motor coloring by Temperature
        self.cmap = plt.get_cmap('coolwarm')
        self.temp_norm = None

        # Dictionaries to store axes for pie charts and legends
        self.pie_axes_dict = {}
        self.legend_axes_dict = {}

        # Axes for motor and table
        self.ax_motor = None
        self.label_ax = None

        self.fig = None

        # Scaling factor for motor parts (set to 1.0 for balanced proportions)
        self.motor_scale = 1.0

        # Output directory for all visual assets
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.out_dir = os.path.join(self.current_dir, "visualizations")
        os.makedirs(self.out_dir, exist_ok=True)

    def prepare_visualization(self):
        """Set up the figure and axes layout."""
        print("\nPreparing visualization...")
        start_vis = time.time()

        self.fig = plt.figure(figsize=(18, 10))

        # === Pie Charts & Legends ===
        top_pie_area_bottom = 0.75  
        top_pie_area_height = 0.15  
        n_feats = len(self.features)

        # Adjust horizontal margins and offsets.
        x_margin = 0.05          
        x_offset = 0.1    

        total_width_for_pies = 1 - 2 * x_margin  # Total available width.
        pie_width = total_width_for_pies / n_feats   # Base width per feature.
        pie_width_factor = 2.0      # Reduced factor to avoid overly stretched pies.
        pie_h = top_pie_area_height * 0.95  # Nearly full height.

        for i, feat_name in enumerate(self.features):
            # Compute the left coordinate and apply offset.
            block_left = x_margin + i * pie_width - x_offset
            block_bottom_pie = top_pie_area_bottom  # Use the adjusted bottom value.

            self.pie_axes_dict[feat_name] = self.fig.add_axes([
                block_left,
                block_bottom_pie,
                pie_width * pie_width_factor,
                pie_h
            ])
            self.pie_axes_dict[feat_name].set_title(
                f"{feat_name} Relative Volume",
                fontsize=8, fontweight='bold'
            )

            # Place legends so that they are centered between the pie charts and motor parts.
            legend_bottom = 0.60  # Slightly lower for clarity.
            legend_h = 0.08
            self.legend_axes_dict[feat_name] = self.fig.add_axes([
                block_left,
                legend_bottom,
                pie_width * pie_width_factor,
                legend_h
            ])
            self.legend_axes_dict[feat_name].axis('off')

        # === Motor Axis ===
        self.ax_motor = self.fig.add_axes([0.05, 0.07, 0.90, 0.38])  # Bottom at 0.07; height = 0.38.
        self.ax_motor.set_xlim(0, 13)
        self.ax_motor.set_ylim(0, 8)
        self.ax_motor.set_aspect('equal')
        self.ax_motor.axis('off')
        self.ax_motor.set_title('4-Cylinder Motor Components', fontsize=10, fontweight='bold')

        # === Table Axis ===
        self.label_ax = self.fig.add_axes([0.05, 0.01, 0.90, 0.08])  # Moved table slightly lower.
        self.label_ax.axis('off')

        # === Color Normalization ===
        all_temps = []
        for info in self.thermal_parts.values():
            all_temps.extend(info['thermo_features']['Temperature'])
        all_temps = np.array(all_temps)
        self.temp_norm = plt.Normalize(vmin=all_temps.min(), vmax=all_temps.max())

        end_vis = time.time()
        print(f"\nVisualization prepared in {end_vis - start_vis:.2f} seconds.")

    def draw_motor_thermal_parts(self, frame):
        """Render the motor components, dynamically colored by Temperature."""
        self.ax_motor.clear()
        self.ax_motor.set_xlim(0, 13)
        self.ax_motor.set_ylim(0, 8)
        self.ax_motor.set_aspect('equal')
        self.ax_motor.axis('off')

        motor_positions = {
            'Cylinder 1': (2.5, 7),
            'Piston 1':   (2.5, 4.5),
            'Cylinder 2': (5.5, 7),
            'Piston 2':   (5.5, 4.5),
            'Cylinder 3': (8.5, 7),
            'Piston 3':   (8.5, 4.5),
            'Cylinder 4': (11.5, 7),
            'Piston 4':   (11.5, 4.5),
        }

        for part_name, part_info in self.thermal_parts.items():
            if part_name.startswith('Cylinder') or part_name.startswith('Piston'):
                pos_x, pos_y = motor_positions.get(part_name, (0, 0))
                size = part_info['size']

                temperature = part_info['thermo_features']['Temperature'][frame]
                color = self.cmap(self.temp_norm(temperature))

                if isinstance(size, tuple):
                    width, height = size
                else:
                    width = height = size

                width  *= self.element_scaling_factor * self.motor_scale
                height *= self.element_scaling_factor * self.motor_scale

                if part_name.startswith('Cylinder'):
                    rect = patches.Rectangle(
                        (pos_x - width/2, pos_y - height),
                        width,
                        height * 2,
                        facecolor=color,
                        edgecolor='black', linewidth=2
                    )
                    self.ax_motor.add_patch(rect)
                elif part_name.startswith('Piston'):
                    pwidth  = width * 1.5
                    pheight = height * 2.0
                    rect = patches.Rectangle(
                        (pos_x - pwidth/2, pos_y - pheight/2),
                        pwidth,
                        pheight,
                        facecolor=color,
                        edgecolor='black', linewidth=2
                    )
                    self.ax_motor.add_patch(rect)

                try:
                    rel_vol_temp = part_info['dfi']['Temperature']['Relative_Volume'][frame] \
                        if ('dfi' in part_info and 'Temperature' in part_info['dfi']) else 0
                except Exception:
                    rel_vol_temp = 0

                self.ax_motor.text(
                    pos_x,
                    pos_y,
                    f"{part_name}\nT: {temperature:.1f}K\nΔS: {rel_vol_temp:.6f}",
                    ha='center', va='center', fontsize=9,
                    fontweight='bold',
                    color='white' if temperature > (self.temp_norm.vmin + self.temp_norm.vmax) / 2 else 'black'
                )

        # Draw Crankshaft (if available)
        if 'Crankshaft' in self.thermal_parts:
            part_info = self.thermal_parts['Crankshaft']
            temperature = part_info['thermo_features']['Temperature'][frame]
            color = self.cmap(self.temp_norm(temperature))
            try:
                rel_vol_temp = part_info['dfi']['Temperature']['Relative_Volume'][frame] \
                    if ('dfi' in part_info and 'Temperature' in part_info['dfi']) else 0
            except Exception:
                rel_vol_temp = 0
        else:
            temperature = 0
            color = 'gray'
            rel_vol_temp = 0

        leftmost = 2.5
        rightmost = 11.5
        crankshaft_x = leftmost
        crankshaft_width = rightmost - leftmost
        crankshaft_y = 4.0
        crankshaft_height = 0.8

        crankshaft_rect = patches.Rectangle(
            (crankshaft_x, crankshaft_y - crankshaft_height),
            crankshaft_width,
            crankshaft_height,
            facecolor=color,
            edgecolor='black',
            linewidth=2
        )
        self.ax_motor.add_patch(crankshaft_rect)

        self.ax_motor.text(
            crankshaft_x + crankshaft_width / 2,
            crankshaft_y - crankshaft_height / 2,
            f"Crankshaft\nT: {temperature:.1f}K\nΔS: {rel_vol_temp:.6f}",
            ha='center', va='center', fontsize=9, fontweight='bold',
            color='white' if temperature > (self.temp_norm.vmin + self.temp_norm.vmax) / 2 else 'black'
        )

    def update(self, frame):
        """
        Update the visualization for the current frame:
         - Render pie charts with updated data and legends,
         - Render the motor components (with dynamic crankshaft),
         - Update the table with relative entropy values.
        """
        for feat_name in self.features:
            pie_ax = self.pie_axes_dict[feat_name]
            pie_ax.clear()
            pie_ax.set_title(f"{feat_name} Relative Volume", fontsize=8, fontweight='bold')

            volume_vals = []
            labels = []
            colors = []

            for part_name, part_info in self.thermal_parts.items():
                vol_val = 0
                try:
                    if feat_name in part_info['dfi']:
                        vol_val = part_info['dfi'][feat_name]['Relative_Volume'][frame]
                except Exception:
                    pass
                volume_vals.append(vol_val)
                labels.append(part_name)
                try:
                    temp_val = part_info['thermo_features']['Temperature'][frame]
                    c = self.cmap(self.temp_norm(temp_val))
                except Exception:
                    c = 'grey'
                colors.append(c)

            # Fallback: if all volume values are zero, use equal proportions.
            if np.isclose(sum(volume_vals), 0):
                volume_vals = [1 for _ in volume_vals]

            pie_ax.pie(
                volume_vals,
                autopct='%1.1f%%',
                colors=colors,
                startangle=140,
                textprops={'fontsize': 7}
            )
            pie_ax.axis('equal')

            legend_ax = self.legend_axes_dict[feat_name]
            legend_ax.clear()
            legend_ax.axis('off')
            legend_handles = [
                patches.Patch(facecolor=cc, label=f"{lbl}: {val:.2f}")
                for lbl, val, cc in zip(labels, volume_vals, colors)
            ]
            legend_ax.legend(
                handles=legend_handles,
                loc="center",
                frameon=False,
                fontsize=8,
                labelspacing=1.2
            )

        self.draw_motor_thermal_parts(frame)

        self.label_ax.clear()
        self.label_ax.axis('off')
        all_parts = list(self.thermal_parts.keys())
        table_data = []
        for feat_name in self.features:
            row = [feat_name]
            for part_name in all_parts:
                try:
                    if feat_name in self.thermal_parts[part_name]['dfi']:
                        val = self.thermal_parts[part_name]['dfi'][feat_name]['Relative_Entropy'][frame]
                        row.append(f"{val:.6f}")
                    else:
                        row.append("N/A")
                except Exception:
                    row.append("N/A")
            table_data.append(row)

        column_labels = ['Feature'] + all_parts
        table = self.label_ax.table(
            cellText=table_data,
            colLabels=column_labels,
            loc='center',
            cellLoc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.0, 1.2)

    def visualize(self, save_static_image=False):
        """Run the animation and optionally save a static image."""
        self.prepare_visualization()

        print("\nCreating and saving animation...")
        start_anim = time.time()

        out_video = os.path.join(self.out_dir, 'entropical_change_simulation.mp4')

        writer = FFMpegWriter(fps=10, metadata=dict(title="Side-by-Side Pies", artist="B. McCrackn"))

        with tqdm(total=self.total_frames, desc="Saving Frames", unit="frame") as pbar:
            with writer.saving(self.fig, out_video, dpi=100):
                for i in range(self.total_frames):
                    self.update(i)
                    writer.grab_frame()
                    pbar.update(1)

        end_anim = time.time()
        duration = end_anim - start_anim
        print(f"\nAnimation saved successfully in {duration:.2f} seconds.")
        print(f"Visualization completed in {duration:.2f} seconds.")

        if save_static_image:
            self.save_static_image(self.out_dir)

        csv_file = os.path.join(self.out_dir, 'entropy_predictions_vs_actual_entropy.csv')
        if os.path.exists(csv_file):
            df_csv = pd.read_csv(csv_file)
            print("\nSample Data from CSV:")
            print(df_csv.head())
            print("\nData Description:")
            print(df_csv.describe())
        else:
            print(f"\nNo CSV file found at {csv_file}, skipping display.")

    def save_static_image(self, out_dir):
        """Save a static PNG from a mid-simulation frame."""
        frame_idx = self.total_frames // 2
        self.update(frame_idx)

        buffer = io.BytesIO()
        self.fig.savefig(buffer, format='png', dpi=300)
        img = Image.open(buffer)

        final_img_path = os.path.join(out_dir, 'final_simulation_state.png')
        img.save(final_img_path)
        print(f"\nStatic image of frame {frame_idx} saved to {final_img_path}")

    def plot_histogram(self, csv_file, histogram_path):
        if not os.path.exists(csv_file):
            print(f"Cannot plot histogram: {csv_file} does not exist.")
            return
        df = pd.read_csv(csv_file)
        if 'Predicted_Entropy' not in df.columns:
            print("No 'Predicted_Entropy' column in CSV; skipping histogram.")
            return

        plt.figure(figsize=(12, 8))
        plt.hist(df['Predicted_Entropy'], bins=50, color='skyblue', alpha=0.7)
        plt.xlabel('Predicted Entropy', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        plt.title('Histogram of Predicted Entropy', fontsize=16, fontweight='bold')
        plt.grid(True)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.tight_layout()
        plt.savefig(histogram_path, dpi=300)
        plt.close()
        print(f"\nHistogram saved to {histogram_path}")

    def plot_scatter(self, csv_file, scatter_plot_path):
        if not os.path.exists(csv_file):
            print(f"Cannot plot scatter: {csv_file} does not exist.")
            return
        df = pd.read_csv(csv_file)
        if 'Actual_Entropy' not in df.columns or 'Predicted_Entropy' not in df.columns:
            print("CSV missing 'Actual_Entropy' or 'Predicted_Entropy'; skipping scatter.")
            return

        plt.figure(figsize=(12, 8))
        plt.scatter(df['Actual_Entropy'], df['Predicted_Entropy'], alpha=0.5, color='green')
        plt.xlabel('Actual ΔS', fontsize=14)
        plt.ylabel('Predicted Entropy', fontsize=14)
        plt.title('Predicted vs Actual Entropy', fontsize=16, fontweight='bold')
        plt.grid(True)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.axvline(x=0, color='lightblue', linestyle='--', linewidth=2, label='Actual ΔS=0')
        plt.axhline(y=0, color='green', linestyle='--', linewidth=2, label='Predicted=0')
        plt.legend()
        plt.tight_layout()
        plt.savefig(scatter_plot_path, dpi=300)
        plt.close()
        print(f"Scatter plot saved to {scatter_plot_path}")

    def plot_error_metrics(self, metrics_df, metrics_plot_path):
        import seaborn as sns
        plt.figure(figsize=(12, 8))
        melted = metrics_df.melt(
            id_vars=['Spectrum', 'Feature'],
            value_vars=['MSE', 'MAE', 'R2_Score']
        )
        sns.barplot(x='variable', y='value', hue='Spectrum', data=melted)
        plt.xlabel('Error Metric', fontsize=14)
        plt.ylabel('Value', fontsize=14)
        plt.title('Error Metrics by Spectrum', fontsize=16, fontweight='bold')
        plt.legend(title='Spectrum', fontsize=12)
        plt.tight_layout()
        plt.savefig(metrics_plot_path, dpi=300)
        plt.close()
        print(f"Error metrics plot saved to {metrics_plot_path}")
        
    def plot_metrics(self, csv_file, histogram_path, scatter_plot_path, error_metrics_path):
        """
        Compute and visualize metrics for all engine components (cylinders, pistons, and crankshaft).
        """
        self.plot_histogram(csv_file, histogram_path)
        self.plot_scatter(csv_file, scatter_plot_path)
        df_metrics = pd.read_csv(csv_file)
        self.plot_error_metrics(df_metrics, error_metrics_path)

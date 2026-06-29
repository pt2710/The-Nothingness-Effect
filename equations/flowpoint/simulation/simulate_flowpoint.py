"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com

...
Flowpoint Simulation Script
---------------------------

This script simulates the dynamic behavior of the Flowpoint (fp) function within a 3D environment,
demonstrating its oscillatory nature as a key component of *The Nothingness Effect* theory. The simulation:

1. Instantiates three Flowpoint generators (for x, y, and z axes) using a base value of 2π.
2. Uses a trigonometric helper (FlowpointTrigonometry) to compute cosine and sine values for oscillatory phases.
3. Dynamically generates 6 points in 3D space, representing three pairs of opposing coordinates.
4. Animates the evolution of these points over a sequence of frames using matplotlib's 3D animation.
5. Explicitly saves static images at frame 420 and frame 800 of the animation.
6. Saves the animation in both MP4 and GIF formats.
7. Exports simulation data to a CSV file.
8. Generates a static figure with 6 subplots that detail the evolution of each point's coordinates over time.

Usage:
    Simply run the script:
        python simulation_flowpoint.py
    The simulation and all outputs will be generated in the script's directory.
"""

import os
import sys
import time
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter

# Set up paths to import modules from the parent directory.
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import the Flowpoint function and the trigonometry helper class.
from flowpoint import fp
from flowpoint_trigonometry import FlowpointTrigonometry

# Instantiate the trigonometry helper and retrieve the π constant.
flowpoint_trig = FlowpointTrigonometry()
PI = flowpoint_trig.pi_value()

# Initialize Flowpoint generators for x, y, and z axes using a base value of 2π.
fp_gen_x = fp(2 * PI)
fp_gen_y = fp(2 * PI)
fp_gen_z = fp(2 * PI)

# Define the update interval for refreshing the Flowpoint values.
update_interval = 10

# Obtain initial Flowpoint values for each axis.
current_fp_x = next(fp_gen_x)
current_fp_y = next(fp_gen_y)
current_fp_z = next(fp_gen_z)

# Simulation parameters.
FRAMES = 800             # Total number of animation frames.
SPEED_FACTOR = 2         # Factor to control the speed of phase progression.
INTERVAL_MS = 25         # Interval between frames in milliseconds.
LAST_FRAME = FRAMES - 1  # Index of the final frame.
anim_start_time = None   # Will record the start time of the animation.

# Set up the 3D plot.
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_title("Flowpoint Oscillation: Using fp for Dynamic Toggle", color='black')
ax.set_xlabel("X", color='black')
ax.set_ylabel("Y", color='black')
ax.set_zlabel("Z", color='black')
ax.set_box_aspect([1, 1, 1])  # Ensure equal aspect ratio in all dimensions.

# Initialize the scatter plot with 6 points (initially all zeros).
xs = [0] * 6
ys = [0] * 6
zs = [0] * 6
scatter = ax.scatter(xs, ys, zs, s=80, alpha=0.8)

def init():
    """
    Initialize the 3D scatter plot for the animation.
    
    Returns
    -------
    tuple
        The scatter plot object as a tuple.
    """
    scatter._offsets3d = (xs, ys, zs)
    return scatter,

# Define radii for three distinct pairs of points.
R1 = 1.0  # Radius for the first pair.
R2 = 1.5  # Radius for the second pair.
R3 = 2.0  # Radius for the third pair.

# Prepare CSV data storage with header.
csv_data = []
header = ["frame"]
for i in range(1, 7):
    header.extend([f"pt{i}_x", f"pt{i}_y", f"pt{i}_z"])
csv_data.append(header)

def blend_color(d, r, sign):
    """
    Compute a blended color based on distance and sign.
    
    If 'sign' is positive, blend toward green; if negative, blend toward red.
    
    Parameters
    ----------
    d : float
        The computed distance from the origin.
    r : float
        The reference radius for the point.
    sign : int
        A value (1 or -1) indicating the directional sign.
    
    Returns
    -------
    tuple
        A tuple of (red, green, blue) color values.
    """
    nd = d / r if r > 0 else 0
    nd = max(0, min(1, nd))
    if sign > 0:
        # Blend toward green.
        rC = (1 - nd) * 1 + nd * 0
        gC = 1.0
        bC = 0.0
    else:
        # Blend toward red.
        rC = 1.0
        gC = (1 - nd) * 1 + nd * 0
        bC = 0.0
    return (rC, gC, bC)

def clean_small_values(val, thresh=1e-10):
    """
    Clean values close to zero for clarity.
    
    Parameters
    ----------
    val : float
        The value to clean.
    thresh : float, optional
        Threshold below which values are set to zero (default is 1e-10).
    
    Returns
    -------
    float
        0.0 if |val| < thresh, else the original value.
    """
    return 0.0 if abs(val) < thresh else val

def animate(frame_index):
    """
    Update function for each animation frame.
    
    This function computes the new positions of 6 points based on the current frame index,
    the oscillatory phases determined by Flowpoint generators, and trigonometric functions.
    It updates the scatter plot and logs data for CSV export, and explicitly saves
    static PNGs at frame 420 and frame 800.
    
    Parameters
    ----------
    frame_index : int
        The current frame number in the animation.
    
    Returns
    -------
    tuple
        The updated scatter plot object.
    """
    global anim_start_time, current_fp_x, current_fp_y, current_fp_z

    # Initialize animation start time.
    if anim_start_time is None:
        anim_start_time = time.time()

    # Print progress information every 100 frames or on the last frame.
    if frame_index % 100 == 0 or frame_index == LAST_FRAME:
        elapsed = time.time() - anim_start_time
        avg_time = elapsed / (frame_index + 1)
        remaining = avg_time * (FRAMES - frame_index - 1)
        print(f"[INFO] Frame {frame_index+1}/{FRAMES}, ~{remaining:.2f}s left.")

    # Update Flowpoint values at defined intervals.
    if frame_index % update_interval == 0:
        current_fp_x = next(fp_gen_x)
        current_fp_y = next(fp_gen_y)
        current_fp_z = next(fp_gen_z)

    # Calculate the base phase for oscillation.
    base_phase = 2 * PI * SPEED_FACTOR * (frame_index / FRAMES)

    # Determine effective phase based on the sign of the current Flowpoint value.
    effective_phase_x = base_phase if current_fp_x > 0 else -base_phase
    effective_phase_y = base_phase if current_fp_y > 0 else -base_phase
    effective_phase_z = base_phase if current_fp_z > 0 else -base_phase

    # Compute positions for the first pair (points p1 and p2) on the YZ plane.
    y1 = R1 * flowpoint_trig.cos(effective_phase_x)
    z1 = R1 * flowpoint_trig.sin(effective_phase_x)
    y2 = R1 * flowpoint_trig.cos(effective_phase_x + PI)
    z2 = R1 * flowpoint_trig.sin(effective_phase_x + PI)
    p1 = (0.0, clean_small_values(y1), clean_small_values(z1))
    p2 = (0.0, clean_small_values(y2), clean_small_values(z2))

    # Compute positions for the second pair (points p3 and p4) on the XZ plane.
    x3 = R2 * flowpoint_trig.cos(effective_phase_y)
    z3 = R2 * flowpoint_trig.sin(effective_phase_y)
    x4 = R2 * flowpoint_trig.cos(effective_phase_y + PI)
    z4 = R2 * flowpoint_trig.sin(effective_phase_y + PI)
    p3 = (clean_small_values(x3), 0.0, clean_small_values(z3))
    p4 = (clean_small_values(x4), 0.0, clean_small_values(z4))

    # Compute positions for the third pair (points p5 and p6) on the XY plane.
    x5 = R3 * flowpoint_trig.cos(effective_phase_z)
    y5 = R3 * flowpoint_trig.sin(effective_phase_z)
    x6 = R3 * flowpoint_trig.cos(effective_phase_z + PI)
    y6 = R3 * flowpoint_trig.sin(effective_phase_z + PI)
    p5 = (clean_small_values(x5), clean_small_values(y5), 0.0)
    p6 = (clean_small_values(x6), clean_small_values(y6), 0.0)

    # Group the computed points.
    points_3d = [p1, p2, p3, p4, p5, p6]

    # Determine directional signs for color blending based on current Flowpoint values.
    sign_x = 1 if current_fp_x > 0 else -1
    sign_y = 1 if current_fp_y > 0 else -1
    sign_z = 1 if current_fp_z > 0 else -1
    signs = [sign_x, -sign_x, sign_y, -sign_y, sign_z, -sign_z]

    # Prepare lists for updated coordinates and colors.
    xcoords, ycoords, zcoords, colors = [], [], [], []
    for pt, s, r in zip(points_3d, signs, [R1, R1, R2, R2, R3, R3]):
        xx, yy, zz = pt
        xcoords.append(xx)
        ycoords.append(yy)
        zcoords.append(zz)
        # Calculate distance from the origin for color blending.
        dist = np.sqrt(xx**2 + yy**2 + zz**2)
        colors.append(blend_color(dist, r, s))

    # Update the scatter plot with new positions and colors.
    scatter._offsets3d = (xcoords, ycoords, zcoords)
    scatter.set_facecolors(colors)

    # Record the current frame data for CSV export.
    row = [frame_index]
    for pt in points_3d:
        row.extend(pt)
    csv_data.append(row)

    # Explicitly save static PNG at frame 420 (1-based index).
    if frame_index == 419:
        outpng_420 = os.path.join(script_dir, "flowpoint_frame_420.png")
        plt.savefig(outpng_420, dpi=300)
        print(f"[INFO] Frame 420 saved: {outpng_420}")

    # Explicitly save static PNG at frame 800 (final frame).
    if frame_index == LAST_FRAME:
        outpng_800 = os.path.join(script_dir, "flowpoint_frame_800.png")
        plt.savefig(outpng_800, dpi=300)
        print(f"[INFO] Frame 800 saved: {outpng_800}")

    return scatter,

# Create the animation using the defined update function.
ani = animation.FuncAnimation(
    fig, animate,
    frames=FRAMES,
    interval=INTERVAL_MS,
    init_func=init,
    blit=True
)

# Set fixed limits for the 3D axes.
ax.set_xlim3d(-5, 5)
ax.set_ylim3d(-5, 5)
ax.set_zlim3d(-5, 5)

# Save the animation as an MP4 video.
mp4_file = os.path.join(script_dir, "flowpoint_oscillation_simulation_animation.mp4")
ani.save(mp4_file, writer=animation.FFMpegWriter(fps=30, bitrate=1800))
print(f"[INFO] MP4 saved: {mp4_file}")

# Save the animation as a GIF.
gif_file = os.path.join(script_dir, "flowpoint_oscillation_simulation_animation.gif")
ani.save(gif_file, writer=PillowWriter(fps=20))
print(f"[INFO] GIF saved: {gif_file}")

# Export the simulation data to a CSV file.
csv_file = os.path.join(script_dir, "flowpoint_oscillation_simulation_data.csv")
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(csv_data)
print(f"[INFO] CSV saved: {csv_file}")

# Close the animation figure.
plt.close(fig)

# Generate a static figure with 6 subplots for detailed analysis.
print("[INFO] Generating a single figure with 6 subplots...")
data_array = np.array(csv_data[1:], dtype=float)  # Exclude header row.
num_rows_to_plot = 400
data_subset = data_array[:num_rows_to_plot, :]
frames_subset = data_subset[:, 0]
radii_lookup = {0: R1, 1: R1, 2: R2, 3: R2, 4: R3, 5: R3}

# Create subplots arranged in 3 rows and 2 columns.
fig, axes = plt.subplots(3, 2, figsize=(12, 12))
axes = axes.flatten()

# Plot x, y, z data for each of the 6 points.
for i in range(6):
    col_x = 1 + 3 * i  # Column index for x-coordinate.
    col_y = col_x + 1  # Column index for y-coordinate.
    col_z = col_x + 2  # Column index for z-coordinate.
    xvals = data_subset[:, col_x]
    yvals = data_subset[:, col_y]
    zvals = data_subset[:, col_z]
    
    ax = axes[i]
    ax.plot(frames_subset, xvals, label='x')
    ax.plot(frames_subset, yvals, label='y')
    ax.plot(frames_subset, zvals, label='z')
    ax.legend()
    ax.set_title(f"Point {i+1}")
    ax.set_xlabel("Frame")
    ax.set_ylabel("Value")
    
    # Set y-axis limits based on the corresponding radius.
    amp = radii_lookup[i]
    ax.set_ylim(-1.2 * amp, 1.2 * amp)

fig.tight_layout()

# Save the static subplot figure.
fig_out = os.path.join(script_dir, "flowpoint_oscillation_simulation_subplots.png")
fig.savefig(fig_out, dpi=300)
print(f"[INFO] Single figure with 6 subplots saved: {fig_out}")
plt.close(fig)

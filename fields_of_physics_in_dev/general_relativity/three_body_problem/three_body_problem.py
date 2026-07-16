"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Three-Body Problem Simulation using The Nothingness Effect and a Velocity Verlet Integrator

This script integrates The Nothingness Effect framework (fp, DFIT, DFT) into a 3-body simulation.
"""

import os
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # For 3D plotting
import matplotlib.animation as animation
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
from fields_of_physics_in_dev.the_nothingness_effect import NothingnessEffect

# -----------------------------------------------------------------------------
# Constants & Real-World Approximations
# -----------------------------------------------------------------------------
G_NORMALIZED = 1.0
G_REAL = 6.67430e-11  # Gravitational constant in m^3/(kg*s^2)

MASS_SUN = 1.98847e30    # kg
MASS_EARTH = 5.97237e24  # kg
MASS_MOON = 7.3477e22    # kg

DIST_SUN_EARTH = 1.496e11  # meters (~1 AU)
DIST_EARTH_MOON = 3.84e8   # meters

VEL_EARTH_AROUND_SUN = 29.78e3  # m/s (~29.78 km/s)
VEL_MOON_AROUND_EARTH = 1.022e3 # m/s (~1.02 km/s)

time_scale_factor = 3600 * 24  # 1 "sim day" per real second
distance_scale_factor = 1.0    # No scaling; adjust if necessary

# -----------------------------------------------------------------------------
# Define a simple Body class
# -----------------------------------------------------------------------------
class Body:
    def __init__(self, mass, position, velocity, label):
        self.mass = mass
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.label = label

# -----------------------------------------------------------------------------
# Body Setup Function: Real-World or Normalized
# -----------------------------------------------------------------------------
def setup_bodies(use_real_data=False):
    """
    Creates either a normalized 3-body system or a real Sun–Earth–Moon system.

    Returns:
        bodies (list of Body)
        G_val (float): Gravitational constant to use
    """
    if not use_real_data:
        # Normalized scenario: 3 equal masses in a plane
        G_val = G_NORMALIZED
        body1 = Body(1.0, [1.0,  0.0, 0.0], [0.0,  0.3, 0.0], "Primary")
        body2 = Body(1.0, [-1.0, 0.0, 0.0], [0.0, -0.3, 0.0], "Secondary")
        body3 = Body(1.0, [0.0,  1.0, 0.0], [0.3,  0.0, 0.0], "Tertiary")
        bodies = [body1, body2, body3]
    else:
        # Real-world scenario: Sun, Earth, Moon
        G_val = G_REAL
        sun_pos = np.array([0.0, 0.0, 0.0])
        earth_pos = np.array([DIST_SUN_EARTH * distance_scale_factor, 0.0, 0.0])
        moon_pos = earth_pos + np.array([DIST_EARTH_MOON * distance_scale_factor, 0.0, 0.0])

        sun_vel = np.array([0.0, 0.0, 0.0])
        earth_vel = np.array([0.0, VEL_EARTH_AROUND_SUN, 0.0]) * time_scale_factor
        moon_vel = np.array([0.0, VEL_EARTH_AROUND_SUN + VEL_MOON_AROUND_EARTH, 0.0]) * time_scale_factor

        sun = Body(MASS_SUN, sun_pos, sun_vel, "Sun")
        earth = Body(MASS_EARTH, earth_pos, earth_vel, "Earth")
        moon = Body(MASS_MOON, moon_pos, moon_vel, "Moon")
        bodies = [sun, earth, moon]

    return bodies, G_val

# -----------------------------------------------------------------------------
# Gravitational acceleration computation
# -----------------------------------------------------------------------------
def compute_acceleration(body, others, G):
    """
    Computes the gravitational acceleration on 'body' due to all bodies in 'others'.
    """
    acceleration = np.zeros(3)
    for other in others:
        r_vec = other.position - body.position
        distance = np.linalg.norm(r_vec)
        if distance < 1e-5:
            continue  # Prevent division by zero or extremely large forces
        acceleration += G * other.mass * r_vec / distance**3
    return acceleration

# -----------------------------------------------------------------------------
# Velocity Verlet Integration Step
# -----------------------------------------------------------------------------
def velocity_verlet_step(body, accel_current, dt):
    """
    Applies one step of velocity Verlet update for a single body.

    Args:
        body (Body): The body to update.
        accel_current (np.array): Current acceleration.
        dt (float): Time step.

    Returns:
        new_position (np.array): Updated position.
        half_step_vel (np.array): Velocity at half-step.
    """
    half_step_vel = body.velocity + 0.5 * accel_current * dt
    new_position = body.position + half_step_vel * dt
    return new_position, half_step_vel

# -----------------------------------------------------------------------------
# DFT predictions demonstration.
# -----------------------------------------------------------------------------
def run_dft_predictions(ne, dfit_history, duration, dt, boltzmann_constant=1.0, scaling_factor=1.0, normalize_to=100):
    """
    Generates sample entropy predictions using The Nothingness Effect's DFT capabilities.
    Relative_Entropy is defined as (correction - 1).

    Args:
        ne (NothingnessEffect): Instance of NothingnessEffect.
        dfit_history (dict): Dictionary mapping body index to a list of DFIT correction factors.
        duration (float): Total duration of simulation.
        dt (float): Time step.
        boltzmann_constant (float, optional): Boltzmann constant for entropy calculations. Defaults to 1.0.
        scaling_factor (float, optional): Scaling factor for entropy predictions. Defaults to 1.0.
        normalize_to (float, optional): Normalization value for the spectrum. Defaults to 100.

    Returns:
        list of dict: Predicted entropy data.
    """
    num_steps = int(duration / dt)
    time_array = np.linspace(0, duration, num_steps)

    # Prepare spectrum_data for DFT
    # Assuming each body corresponds to a variable, use Relative_Volume as the variable's value
    spectrum_data = {}
    for i, corrections in dfit_history.items():
        # Sørg for, at corrections er reelle
        corrections_real = np.real(np.array(corrections))
        spectrum_data[f"Body_{i}"] = corrections_real

    # Compute DFT predictions using NothingnessEffect
    predictions = ne.compute_dft(
        boltzmann_constant=boltzmann_constant,
        scaling_factor=scaling_factor,
        spectrum_data=spectrum_data,
        time_array=time_array,
        normalize_to=normalize_to
    )

    return predictions

# -----------------------------------------------------------------------------
# Main simulation function with DFIT & DFT via NothingnessEffect
# -----------------------------------------------------------------------------
def simulate_three_body_dynamic(duration=50, dt=0.01, use_real_data=False, normalize_to=100):
    """
    Simulerer tre-krops problemet ved hjælp af The Nothingness Effect's DFIT og DFT.

    Returns:
        bodies (list of Body): Kroppe efter simuleringen.
        traj (dict): Dictionary der kortlægger kropsindeks til en liste af 3D positioner.
        dfit_history (dict): Dictionary der kortlægger kropsindeks til en liste af DFIT korrektion faktorer.
        num_steps (int): Total antal simulation skridt.
        ne (NothingnessEffect): Instans af NothingnessEffect klassen brugt.
        G_sim (float): Gravitationskonstant brugt i simuleringen.
    """
    # Initialiser NothingnessEffect
    ne = NothingnessEffect()

    # Opsæt kroppe og gravitationskonstant
    bodies, G_sim = setup_bodies(use_real_data=use_real_data)
    num_steps = int(duration / dt)
    traj = {i: [bodies[i].position.copy()] for i in range(len(bodies))}
    dfit_history = {i: [] for i in range(len(bodies))}

    # Initial accelerations
    accelerations = []
    for i, body in enumerate(bodies):
        others = [b for j, b in enumerate(bodies) if j != i]
        a_grav = compute_acceleration(body, others, G_sim)
        accelerations.append(a_grav)

    # Hovedsimulerings loop
    for step in range(num_steps):
        current_time = step * dt
        spectrum_data = {f"Body_{i}": np.linalg.norm(a) for i, a in enumerate(accelerations)}
        entropical_data = ne.dfit(
            spectrum_data,
            normalize_to=normalize_to,
            adv_mode=True,
            type='symmetric'
        )

        new_positions = [None] * len(bodies)
        half_step_vels = [None] * len(bodies)

        for i, body in enumerate(bodies):
            spectrum_key = f"Body_{i}"
            var_name = "Relative_Volume"

            # Hent DFIT komponenter for den aktuelle krop
            DFIT = entropical_data.get(spectrum_key, {}).get(var_name, {})
            correction = DFIT.get("Relative_Volume", 1.0)

            # Type check: Sikre at korrektionen er en skalar
            if not isinstance(correction, (float, int)):
                raise TypeError(f"Relative_Volume for {spectrum_key} er ikke en skalar: {correction}")

            a_corrected = accelerations[i] * correction

            new_pos, h_vel = velocity_verlet_step(body, a_corrected, dt)
            new_positions[i] = new_pos
            half_step_vels[i] = h_vel

            # Record the correction factor in history
            dfit_history[i].append(correction)

        # Beregn nye accelerations
        for i, body in enumerate(bodies):
            body.position = new_positions[i]
        accelerations = [
            compute_acceleration(body, [b for j, b in enumerate(bodies) if j != i], G_sim)
            for i, body in enumerate(bodies)
        ]

        # Endelig velocity opdatering
        for i, body in enumerate(bodies):
            spectrum_key = f"Body_{i}"
            var_name = "Relative_Volume"  # Juster dette til det korrekte var_name hvis nødvendigt

            # Hent DFIT komponenter for den aktuelle krop
            DFIT = entropical_data.get(spectrum_key, {}).get(var_name, {})
            correction = DFIT.get("Relative_Volume", 1.0)

            # Type check: Sikre at korrektionen er en skalar
            if not isinstance(correction, (float, int)):
                raise TypeError(f"Relative_Volume for {spectrum_key} er ikke en skalar: {correction}")

            a_corrected_new = accelerations[i] * correction
            body.velocity = half_step_vels[i] + 0.5 * a_corrected_new * dt
            body.position = new_positions[i]
            traj[i].append(body.position.copy())

    # Debug: Print slutpositioner for hver krop
    for i, body in enumerate(bodies):
        print(f"Final position of {body.label} = {body.position}")

    return bodies, traj, dfit_history, num_steps, ne, G_sim

# -----------------------------------------------------------------------------
# Dynamic Animation Function
# -----------------------------------------------------------------------------
def animate_simulation(bodies, traj, dfit_history, num_steps, dt, ne):
    """
    Creates a 3D animation of the simulation with DFIT corrections and DFT entropy predictions.
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Define colors for up to 6 bodies; extend if needed
    colors = ['red', 'blue', 'green', 'orange', 'magenta', 'cyan']

    # Initial scatter plot using positions at time zero
    init_positions = np.array([traj[i][0] for i in range(len(bodies))])
    scatter = ax.scatter(init_positions[:, 0],
                         init_positions[:, 1],
                         init_positions[:, 2],
                         s=100,
                         c=[colors[i % len(colors)] for i in range(len(bodies))])

    # Create text annotations for DFIT factors and for predicted entropy
    annotations = []
    entropy_annotations = []
    for i in range(len(bodies)):
        pos = init_positions[i]
        body_label = bodies[i].label
        a_text = ax.text(pos[0], pos[1], pos[2],
                         f"{body_label}\nDFIT: {dfit_history[i][0]:.3f}",
                         color=colors[i % len(colors)], fontsize=9)
        annotations.append(a_text)
        e_text = ax.text(pos[0], pos[1], pos[2],
                         f"Entropy: ---",
                         color=colors[i % len(colors)], fontsize=9)
        entropy_annotations.append(e_text)

    # ---------------------------------------------------------------
    # MANUAL AXIS LIMITS & BOX ASPECT
    # ---------------------------------------------------------------
    # Determine if we're using real-world data
    use_real_data = ("Sun" in [b.label for b in bodies])
    ax.set_box_aspect((1, 1, 1))  # Equal aspect ratio

    if use_real_data:
        # Set larger axis limits for real-world scenario
        ax.set_xlim(-2.0e11, 2.0e11)
        ax.set_ylim(-2.0e11, 2.0e11)
        ax.set_zlim(-2.0e11, 2.0e11)
    else:
        # Smaller axis limits for normalized scenario
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_zlim(-3, 3)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Dynamic Three-Body Simulation with DFIT and Entropy Predictions")

    # Precompute DFT predictions
    predictions = run_dft_predictions(ne, dfit_history, duration=num_steps * dt, dt=dt, normalize_to=100)

    # Organize predictions by Body_{i}
    predictions_by_body = {f"Body_{i}": [] for i in range(len(bodies))}
    for pred in predictions:
        # Assuming 'feature' corresponds to 'Body_i'
        feature = pred.get('feature', '')
        if feature in predictions_by_body:
            predictions_by_body[feature].append(pred)

    # For simplicity, we'll display the average predicted entropy for each body
    avg_predicted_entropy = {}
    for i in range(len(bodies)):
        body_key = f"Body_{i}"
        preds_for_body = predictions_by_body[body_key]
        if preds_for_body:
            avg = np.mean([p['Predicted_Entropy'] for p in preds_for_body])
            avg_predicted_entropy[body_key] = avg
        else:
            avg_predicted_entropy[body_key] = 0.0

    # Animation update function
    def update(frame):
        positions = np.array([traj[i][frame] for i in range(len(bodies))])

        # Update scatter positions
        scatter._offsets3d = (positions[:, 0], positions[:, 1], positions[:, 2])

        # Update DFIT and Entropy annotations
        for i in range(len(bodies)):
            corr = dfit_history[i][frame]
            pos = positions[i]
            annotations[i].set_position((pos[0], pos[1]))
            annotations[i].set_3d_properties(pos[2])
            annotations[i].set_text(f"{bodies[i].label}\nDFIT: {corr:.3f}")

            # Average predicted entropy (static, precomputed)
            entropy_val = avg_predicted_entropy.get(f"Body_{i}", 0.0)
            entropy_annotations[i].set_position((pos[0], pos[1]))
            entropy_annotations[i].set_3d_properties(pos[2])
            entropy_annotations[i].set_text(f"Entropy: {entropy_val:.3f}")

        # Show progress every 50 frames
        if frame % 50 == 0 and frame > 0:
            elapsed = time.time() - start_time_anim
            est_total = (elapsed / frame) * (num_steps - 1)
            remaining = est_total - elapsed
            print(f"Frame {frame}/{num_steps}, est. remaining time: {remaining:.2f} s")

        return scatter, *annotations, *entropy_annotations

    # Start time for progress estimation
    start_time_anim = time.time()

    ani = animation.FuncAnimation(fig, update, frames=num_steps, interval=10, blit=False)

    # Attempt to save animation
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_filename = os.path.join(script_dir, "three_body_dynamic_simulation.mp4")
    try:
        writer = animation.FFMpegWriter(fps=30, metadata=dict(artist='TheNothingnessEffect'), bitrate=1800)
        ani.save(video_filename, writer=writer)
        print(f"Dynamic simulation saved to '{video_filename}'.")
    except Exception as e:
        print(f"FFmpeg writer failed ({e}); saving as GIF instead.")
        gif_filename = os.path.join(script_dir, "three_body_dynamic_simulation.gif")
        ani.save(gif_filename, writer="pillow", fps=30)
        print(f"Dynamic simulation saved to '{gif_filename}'.")

    plt.show()

    # Save DFIT history to CSV for numerical analysis
    df_dfit = {}
    for i in range(len(bodies)):
        df_dfit[f"{bodies[i].label}_DFIT"] = dfit_history[i]
    df_dfit = pd.DataFrame(df_dfit)
    dfit_csv = os.path.join(script_dir, "dfit_history.csv")
    df_dfit.to_csv(dfit_csv, index=False)
    print(f"DFIT history saved to '{dfit_csv}'.")

    # Also save DFT predictions
    predictions = run_dft_predictions(ne, dfit_history, duration=num_steps * dt, dt=dt, boltzmann_constant=1.0, scaling_factor=1.0, normalize_to=100)
    df_dft = pd.DataFrame(predictions)
    dft_csv = os.path.join(script_dir, "dft_predictions.csv")
    df_dft.to_csv(dft_csv, index=False)
    print(f"DFT predictions saved to '{dft_csv}'.")

# -----------------------------------------------------------------------------
# Static Plot Function
# -----------------------------------------------------------------------------
def plot_trajectories(traj, dfit_history, bodies):
    """
    Plots final 3D trajectories of each body, including a DFIT annotation near 
    the final position of each body.

    Args:
        traj (dict): Trajectories of each body.
        dfit_history (dict): DFIT history for each body.
        bodies (list of Body): List of bodies.
    """
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # For 3D plotting

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    colors = ['red', 'blue', 'green', 'orange', 'magenta', 'cyan']

    # Distinct annotation offsets for each body (just for clarity)
    annotation_offsets = [
        np.array([0.1, 0.1, 0.1]),
        np.array([0.1, -0.1, 0.1]),
        np.array([-0.1, 0.1, 0.1]),
        np.array([0.2, 0.2, 0.2]),
        np.array([-0.2, -0.2, 0.2]),
        np.array([0.2, -0.2, 0.2])
    ]

    # Plot each body’s trajectory
    for i in range(len(traj)):
        pos_array = np.array(traj[i])
        ax.plot(pos_array[:, 0], pos_array[:, 1], pos_array[:, 2],
                label=f"{bodies[i].label}",
                color=colors[i % len(colors)],
                linewidth=2)
        final_pos = pos_array[-1]
        final_corr = dfit_history[i][-1]
        ax.scatter(final_pos[0], final_pos[1], final_pos[2],
                   s=100, c=colors[i % len(colors)], marker='o')

        # Håndter forskellige typer af final_corr (float, tuple, ndarray)
        if isinstance(final_corr, (tuple, list, np.ndarray)):
            # Konverter til en streng med alle komponenter, formateret til 3 decimaler
            final_corr_str = ', '.join([f"{val:.3f}" for val in final_corr])
        else:
            # Hvis det er en skalar, formater som før
            final_corr_str = f"{final_corr:.3f}"

        # Annoter med DFIT
        offset = annotation_offsets[i % len(annotation_offsets)]
        annotation_pos = final_pos + offset
        ax.text(annotation_pos[0],
                annotation_pos[1],
                annotation_pos[2],
                f"{bodies[i].label}\nDFIT: {final_corr_str}",
                color=colors[i % len(colors)],
                fontsize=9)

    ax.set_title("Final Three-Body Trajectories with DFIT Stabilization", fontsize=14)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_box_aspect((1, 1, 1))  # Equal aspect ratio

    # Determine if we're using real-world data
    use_real_data = ("Sun" in [b.label for b in bodies])
    if use_real_data:
        ax.set_xlim(-2.0e11, 2.0e11)
        ax.set_ylim(-2.0e11, 2.0e11)
        ax.set_zlim(-2.0e11, 2.0e11)
    else:
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_zlim(-3, 3)

    ax.legend()

    # Bestem sti til at gemme billedet
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(script_dir, "three_body_trajectories.png")
    plt.savefig(save_path)
    plt.show()
    print(f"Static trajectory plot saved to '{save_path}'.")


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------
def main():
    """
    Executes the full simulation pipeline:
      1. Simulate (either a normalized or real-world scenario).
      2. Produce a static plot of the trajectories.
      3. Create an animated 3D visualization with DFIT and DFT.
      4. Print out sample DFT predictions.
    """
    # --------------------------------------
    # Choose scenario
    # --------------------------------------
    use_real_data = True  # Set to False for normalized 3-body example.

    # Time step and total duration:
    # For real-world scenario with scaled velocities, a smaller dt is necessary for accuracy.
    dt = 0.001 if use_real_data else 0.01
    duration = 5.0 if use_real_data else 50.0
    # Explanation:
    #   - In the real-world scenario, we set a short 5 second "demo" 
    #     (which might correspond to 5 days, if time_scale_factor=1 day per second). 
    #   - Adjust as needed to see partial orbit arcs.

    # 1) Run the simulation
    bodies, traj, dfit_history, num_steps, ne, G_sim = simulate_three_body_dynamic(
        duration=duration, 
        dt=dt,
        use_real_data=use_real_data,
        normalize_to=100
    )

    # 2) Static trajectories
    plot_trajectories(traj, dfit_history, bodies)

    # 3) Dynamic animation
    animate_simulation(bodies, traj, dfit_history, num_steps, dt, ne)

    # 4) Display a few DFT predictions (Entropy forecast)
    predictions = run_dft_predictions(
        ne=ne, 
        dfit_history=dfit_history, 
        duration=duration, 
        dt=dt, 
        boltzmann_constant=1.0,  # Sæt korrekt værdi
        scaling_factor=1.0,      # Sæt korrekt værdi
        normalize_to=100
    )
    print("\nSample Entropy Predictions (first 5):")
    for pred in predictions[:5]:
        print(pred)

if __name__ == "__main__":
    main()


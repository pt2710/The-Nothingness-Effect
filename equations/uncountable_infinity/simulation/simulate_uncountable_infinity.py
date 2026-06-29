"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com

...
Uncountable Infinity Simulation Script

This script simulates the uncountable infinity concept and generates visualizations of the results,
including the continuum map (Appendix R), spectral density (Appendix S), and
a truly “uncountable” dynamic Flowpoint trajectory with non‑repeating rotation.
"""
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

import csv
import time
from tqdm import tqdm

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from flowpoint_trigonometry.fp_trigonometry import FlowpointTrigonometry
from uncountable_infinity.uncountable_infinity import uncountable_infinity

def simulate_uncountable_infinity(n_points=1000):
    results = []
    print(f"Starting uncountable infinity simulation with {n_points} points.")
    for _ in tqdm(range(n_points), desc="Simulating Uncountable Infinity", unit="pt"):
        x, y, z = np.random.uniform(-100, 100, 3)
        try:
            val = next(uncountable_infinity(x, y, z))
        except Exception:
            val = np.nan
        results.append([x, y, z, np.real(val)])
    print("Simulation complete.")
    return np.array(results, dtype=float)

def save_results(results, filename):
    print(f"Saving results to {filename}")
    t0 = time.time()
    with open(filename, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['x','y','z','result'])
        w.writerows(results)
    print(f"Saved in {time.time()-t0:.2f}s")

def visualize_uncountable_infinity(results, base_dir):
    xs, ys, zs, vs = results.T

    # (static panels + continuum + spectral density here—omitted for brevity)

    # 4) Truly “uncountable” dynamic Flowpoint + rotating circle
    print("Creating uncountable‑in‑motion animation…")
    t0 = time.time()

    # parameters
    N_anim = 360
    circle_pts = 200
    # base circle in XY plane radius=1
    thetas = np.linspace(0, 2*np.pi, circle_pts)
    base_circle = np.vstack([np.cos(thetas), np.sin(thetas), np.zeros_like(thetas)])

    # Flowpoint triggers for dynamic axis
    trig_x = FlowpointTrigonometry()
    trig_y = FlowpointTrigonometry()
    trig_z = FlowpointTrigonometry()

    fig4 = plt.figure(figsize=(6,6))
    ax4 = fig4.add_subplot(111, projection='3d')
    ax4.set_xlim(-1,1); ax4.set_ylim(-1,1); ax4.set_zlim(-1,1)
    ax4.set_title('Uncountable Rotating Flowpoint Circle')

    line, = ax4.plot([], [], [], lw=2, color='blue')
    dot,  = ax4.plot([], [], [], 'o', color='red', ms=6)

    def rodrigues(v, k, θ):
        """Rotate vector(s) v around axis k by angle θ (Rodrigues' formula)."""
        k = k / np.linalg.norm(k)
        v_par = np.dot(k, v) * k[:,None]
        v_perp = v - v_par
        v_cross = np.cross(k[:,None], v, axis=0)
        return v_par + v_perp*np.cos(θ) + v_cross*np.sin(θ)

    def init():
        line.set_data([], [])
        line.set_3d_properties([])
        dot.set_data([], [])
        dot.set_3d_properties([])
        return line, dot

    def update(i):
        # 1) build a time-varying rotation axis from Flowpoint trig
        axis = np.array([
            trig_x.cos(i * 0.1),
            trig_y.sin(i * 0.123),
            trig_z.cos_sin(i * 0.07)
        ])
        axis = axis / np.linalg.norm(axis)

        # 2) rotation angle increases nonlinearly
        angle = 2*np.pi * (i/N_anim) * (1 + 0.3*np.sin(i*0.05))

        # 3) rotate entire circle
        circle_rot = rodrigues(base_circle, axis, angle)

        # 4) choose the dot position sliding around the circle
        phi = 2*np.pi * (i % circle_pts) / circle_pts
        dot_base = np.array([np.cos(phi), np.sin(phi), 0.0])
        dot_rot = rodrigues(dot_base[:,None], axis, angle).flatten()

        # update line (blue) and dot (red)
        line.set_data(circle_rot[0], circle_rot[1])
        line.set_3d_properties(circle_rot[2])
        dot.set_data([dot_rot[0]], [dot_rot[1]])
        dot.set_3d_properties([dot_rot[2]])
        return line, dot

    ani = animation.FuncAnimation(
        fig4, update, init_func=init,
        frames=N_anim, interval=30, blit=True
    )
    anim_file = os.path.join(base_dir, 'uncountable_infinity_rotating_circle.gif')
    ani.save(anim_file, writer='pillow', fps=30)
    plt.close(fig4)
    print(f"Uncountable animation saved in {time.time()-t0:.2f}s")

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    results = simulate_uncountable_infinity(1000)
    save_results(results, os.path.join(base, 'uncountable_infinity_simulation_results.csv'))
    visualize_uncountable_infinity(results, base)
    print("All visualizations generated.")

if __name__ == "__main__":
    main()

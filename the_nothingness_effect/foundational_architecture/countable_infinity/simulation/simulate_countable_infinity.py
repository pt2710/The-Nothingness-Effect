"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Countable Infinity Simulation Script

This script simulates the countable infinity property and generates visualizations of the results,
including:
  • Static and animated plots of countable_infinity outputs
  • Static 3D permutation cube of ±X,±Y,±Z with 3-bit labels (Appendix P)
  • Animated Gray‑code traversal of the cube via parity flips

All outputs are saved alongside the script.
"""

import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import csv
import time
import random
import traceback
from itertools import product

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d import Axes3D  
from tqdm import tqdm

from the_nothingness_effect.foundational_architecture.countable_infinity import countable_infinity

def simulate_countable_infinity(n_points=1000):
    """Run the countable_infinity generator on random (x,y,z) inputs."""
    results = []
    print(f"Starting countable infinity simulation with {n_points} points.")
    for _ in tqdm(range(n_points), desc="Simulating Countable Infinity", unit="pt"):
        x = random.uniform(-100, 100)
        y = random.uniform(-100, 100)
        z = random.uniform(-100, 100)
        try:
            result = next(countable_infinity(x, y, z))
        except Exception:
            result = np.nan
        results.append([x, y, z, result])
    print("Simulation complete.")
    return results

def save_results(results, filename):
    """Save simulation results to CSV."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x','y','z','result'])
        writer.writerows(results)
    print(f"Results saved to {filename}")

def visualize_countable_infinity(results, static_png, anim_gif):
    """Static scatter & animated 3D scatter of countable_infinity outputs."""
    xs = np.array([r[0] for r in results])
    ys = np.array([r[1] for r in results])
    zs = np.array([r[2] for r in results])
    vals = np.array([r[3] for r in results])

    # Static
    print(f"Creating static plot: {static_png}")
    t0 = time.time()
    fig, (ax1, ax2) = plt.subplots(2,1,figsize=(10,12))
    ax1.scatter(xs, vals, c='blue', alpha=0.5, label='X→result')
    ax1.scatter(ys, vals, c='red',  alpha=0.5, label='Y→result')
    ax1.scatter(zs, vals, c='green',alpha=0.5, label='Z→result')
    ax1.legend(); ax1.grid(True)
    ax1.set_title('Countable Infinity: Input vs Result')
    ax1.set_xlabel('Input'); ax1.set_ylabel('Result')

    ax2.hist(vals[~np.isnan(vals)], bins=30, color='purple', alpha=0.7)
    ax2.set_title('Result Distribution'); ax2.grid(True)
    ax2.set_xlabel('Result'); ax2.set_ylabel('Frequency')

    plt.tight_layout(); fig.savefig(static_png); plt.close(fig)
    print(f"Static saved in {time.time()-t0:.2f}s")

    # Animated
    print(f"Creating animated scatter GIF: {anim_gif}")
    t0 = time.time()
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111, projection='3d')
    cmap = plt.get_cmap('viridis')
    scat = ax.scatter([],[],[], c=[], cmap=cmap, s=10, alpha=0.6)

    def init():
        ax.set_xlim(xs.min(), xs.max())
        ax.set_ylim(ys.min(), ys.max())
        ax.set_zlim(zs.min(), zs.max())
        return scat,

    def update(frame):
        current = frame+1
        scat._offsets3d = (xs[:current], ys[:current], zs[:current])
        scat.set_array(vals[:current])
        ax.set_title(f'Frame {current}/{len(results)}')
        return scat,

    ani = animation.FuncAnimation(fig, update, init_func=init,
                                  frames=len(results), interval=30, blit=False)
    ani.save(anim_gif, writer='pillow', fps=20)
    plt.close(fig)
    print(f"Animated saved in {time.time()-t0:.2f}s")

def visualize_permutation_cube_static(filename):
    """
    Static 3D permutation cube of ±X,±Y,±Z vertices labeled with 3-bit codes:
    Appendix P mapping: (+X,+Y,+Z)=000 ... (-X,-Y,-Z)=111
    """
    print(f"Creating permutation cube: {filename}")
    # generate bit triplets and coords
    triplets = list(product([0,1], repeat=3))
    coords   = [((1-2*b1),(1-2*b2),(1-2*b3)) for b1,b2,b3 in triplets]

    fig = plt.figure(figsize=(6,6))
    ax  = fig.add_subplot(111, projection='3d')
    xs, ys, zs = zip(*coords)
    ax.scatter(xs, ys, zs, c='black', s=50)

    for (b1,b2,b3),(x,y,z) in zip(triplets, coords):
        ax.text(x, y, z, f'{b1}{b2}{b3}', color='blue', ha='center', va='center')

    # draw edges between vertices differing by one bit
    for i,(x1,y1,z1) in enumerate(coords):
        for j,(x2,y2,z2) in enumerate(coords):
            if sum(abs(a-b) for a,b in zip(coords[i],coords[j])) == 2:
                ax.plot([x1,x2],[y1,y2],[z1,z2], c='gray', lw=1)

    ax.set_title('Permutation Cube B³ → ±X,±Y,±Z')
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
    ax.set_xlim(-1.5,1.5); ax.set_ylim(-1.5,1.5); ax.set_zlim(-1.5,1.5)
    plt.tight_layout(); fig.savefig(filename); plt.close(fig)
    print(f"Cube saved to {filename}")

def visualize_permutation_cube_dynamic(filename, cycles=2):
    """
    Animated Gray‑code traversal of the permutation cube, flipping one parity bit per step.
    """
    print(f"Creating permutation cube traversal GIF: {filename}")
    # generate Gray code sequence for 3 bits
    seq = [i ^ (i>>1) for i in range(8)]
    # repeat for given cycles
    seq = seq * cycles
    # build coords for ±X,±Y,±Z from bits b2 b1 b0 => (X,Y,Z)
    coords = [
        ((1 - 2 * ((i >> 2) & 1)),
            (1 - 2 * ((i >> 1) & 1)),
            (1 - 2 * ((i >> 0) & 1)))
        for i in range(8)
    ]
    coords_map = {i: coords[i] for i in range(8)}

    fig = plt.figure(figsize=(6,6))
    ax  = fig.add_subplot(111, projection='3d')
    ax.set_xlim(-1.5,1.5); ax.set_ylim(-1.5,1.5); ax.set_zlim(-1.5,1.5)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    plt.tight_layout()

    # pre-draw cube edges
    def draw_edges():
        for i, (x1,y1,z1) in coords_map.items():
            for j, (x2,y2,z2) in coords_map.items():
                if sum(abs(a-b) for a,b in zip(coords_map[i], coords_map[j])) == 2:
                    ax.plot([x1,x2], [y1,y2], [z1,z2], c='lightgray', lw=1)

    def init():
        ax.cla()
        ax.set_xlim(-1.5,1.5); ax.set_ylim(-1.5,1.5); ax.set_zlim(-1.5,1.5)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
        draw_edges()
        return []

    def update(frame):
        init()
        idx = seq[frame]
        x,y,z = coords_map[idx]
        ax.scatter([x], [y], [z], c='red', s=200)
        ax.set_title(f'Gray code: {format(idx, "03b")}')
        return []

    ani = animation.FuncAnimation(fig, update, init_func=init,
                                    frames=len(seq), interval=500, blit=False)
    ani.save(filename, writer='pillow', fps=2)
    plt.close(fig)
    print(f"Traversal GIF saved to {filename}")

def main():
    if '__file__' in globals():
        base = os.path.dirname(os.path.abspath(__file__))
    else:
        base = os.getcwd()
    print(f"Script directory: {base}")

    # simulate
    results = simulate_countable_infinity(1000)
    # save CSV
    csv_f = os.path.join(base,'countable_infinity_results.csv')
    save_results(results, csv_f)

    # visualizations
    static_png = os.path.join(base,'countable_infinity_static.png')
    anim_gif   = os.path.join(base,'countable_infinity_animation.gif')
    visualize_countable_infinity(results, static_png, anim_gif)

    cube_png = os.path.join(base,'permutation_cube_static.png')
    cube_gif = os.path.join(base,'permutation_cube_traversal.gif')
    visualize_permutation_cube_static(cube_png)
    visualize_permutation_cube_dynamic(cube_gif, cycles=3)

if __name__=="__main__":
    main()

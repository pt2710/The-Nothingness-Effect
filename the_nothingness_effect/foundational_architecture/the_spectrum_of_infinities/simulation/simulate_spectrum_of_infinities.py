"""
Author: Budd McCrackn
Email: thenothingnesseffect@gmail.com
...

Spectrum of Infinities Simulation Script

This script simulates the spectrum of infinities concept and generates 
visualizations of the results, including:
  1) Static spectrum line plots
  2) 3D animated scatter for basic & symmetric spectra
  3) Appendix T: Entropy Density over a 10‑feature spectrum [0–100]
"""
import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)
import time
import csv
import random
from multiprocessing import Pool, cpu_count

from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import colorsys

from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.flowpoint import fp
from the_nothingness_effect.mathematical_architecture.flowpoint_trigonometry.fp_trigonometry import FlowpointTrigonometry
from the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities.spectrum_of_infinities import SpectrumOfInfinities

def _compute_spectrum_point(_):
    """Worker for parallel spectrum computation."""
    spec = SpectrumOfInfinities()
    basic = spec.soi()
    sym_p, sym_n = spec.soi(normalize_to=100, adv_mode=True, type='symmetric')
    return (
        float(np.real(basic)),
        float(np.real(sym_p)),
        float(np.real(sym_n))
    )

def simulate_spectrum_of_infinities(n_points=50):
    """
    Parallel simulation of spectrum points with real‑time progress.
    Returns ndarray of shape (n_points, 3).
    """
    print(f"[1/4] Starting spectrum simulation with {n_points} points using {cpu_count()} cores.")
    with Pool() as pool:
        results = list(tqdm(
            pool.imap(_compute_spectrum_point, range(n_points)),
            total=n_points,
            desc="Simulating Spectrum",
            unit="pt"
        ))
    print("[1/4] Spectrum simulation completed.")
    return np.array(results, dtype=float)

def save_results(results, filename):
    """
    Saves results to CSV with a tqdm progress bar and ETA.
    """
    print(f"[2/4] Saving results to {filename}")
    start = time.time()
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Basic Spectrum', 'Symmetric +', 'Symmetric -'])
        for row in tqdm(results, desc="Writing CSV rows", unit="row"):
            writer.writerow(row)
    print(f"[2/4] Saved CSV in {time.time() - start:.2f}s.")

def visualize_spectrum_of_infinities(results, base_dir):
    """
    1) Static line plots
    2) 3D animated scatter for Basic & Symmetric spectra
    3) Appendix T: Entropy Density over a 10‑feature spectrum [0–100]
    """
    basic, sym_p, sym_n = results.T
    N = len(basic)

    # 3) Static line plots
    print(f"[3/4] Generating static plots…")
    static_png = os.path.join(base_dir, 'spectrum_of_infinities_simulation_static.png')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax1.plot(basic, label='Basic'); 
    ax1.set_title('Basic Spectrum'); ax1.grid(True); ax1.legend()
    ax2.plot(sym_p, label='Symmetric +'); ax2.plot(sym_n, label='Symmetric -')
    ax2.set_title('Symmetric Spectrum'); ax2.set_xlabel('Test #'); ax2.grid(True); ax2.legend()
    plt.tight_layout()
    fig.savefig(static_png, dpi=300)
    plt.close(fig)
    print(f"[3/4] Static plots saved to {static_png}.")

    # Common setup for animations
    radius = 10.0
    theta = np.random.uniform(0, 2*np.pi, N)
    phi   = np.random.uniform(0, np.pi, N)
    r     = radius * (1 + 0.1 * np.random.uniform(-1,1,N))
    xs    = r * np.sin(phi) * np.cos(theta)
    ys    = r * np.sin(phi) * np.sin(theta)
    zs    = r * np.cos(phi)
    fp_gens = [fp(random.random()) for _ in range(N)]

    def make_progress_cb(label):
        def _cb(current, total):
            print(f"{label}: frame {current}/{total} ({current/total*100:.1f}%), {total-current} left")
        return _cb

    # 2a) Basic Spectrum 3D Animation
    print(f"[4/4] Creating Basic Spectrum 3D animation…")
    anim_basic = os.path.join(base_dir, 'basic_spectrum_simulation_animation.gif')
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111, projection='3d')

    def update_basic(frame):
        ax.clear()
        ang = frame * 0.02
        ca, sa = np.cos(ang), np.sin(ang)
        xr = xs*ca - ys*sa
        yr = xs*sa + ys*ca
        zr = zs
        count = frame + 1
        offs = np.array([next(g) for g in fp_gens[:count]])
        ax.scatter(
            xr[:count] + offs,
            yr[:count] + offs,
            zr[:count] + offs,
            c=[colorsys.hsv_to_rgb(next(g)%1,1,1) for g in fp_gens[:count]],
            s=5
        )
        ax.set_title('Basic Spectrum 3D Animation')
        ax.set_xlim(-radius, radius)
        ax.set_ylim(-radius, radius)
        ax.set_zlim(-radius, radius)

    writer_basic = PillowWriter(fps=25)
    writer_basic.progress_callback = make_progress_cb("Basic Anim")
    ani = FuncAnimation(fig, update_basic, frames=N, interval=50, blit=False)
    ani.save(anim_basic, writer=writer_basic)
    plt.close(fig)
    print(f"[4/4] Basic animation saved to {anim_basic}.")

    # 2b) Symmetric Spectrum 3D Animation
    print(f"[4/4] Creating Symmetric Spectrum 3D animation…")
    half = N // 2
    thp = np.random.uniform(0, 2*np.pi, half)
    php = np.random.uniform(0, np.pi/2, half)
    rp  = radius * (1 + 0.1 * np.random.uniform(-1,1,half))
    xp = rp*np.sin(php)*np.cos(thp)
    yp = rp*np.sin(php)*np.sin(thp)
    zp = rp*np.cos(php)

    thr = np.random.uniform(0, 2*np.pi, half)
    phr = np.random.uniform(np.pi/2, np.pi, half)
    rr  = radius * (1 + 0.1 * np.random.uniform(-1,1,half))
    xr_ = rr*np.sin(phr)*np.cos(thr)
    yr_ = rr*np.sin(phr)*np.sin(thr)
    zr_ = rr*np.cos(phr)

    fp_p = [fp(random.random()) for _ in range(half)]
    fp_n = [fp(random.random()) for _ in range(half)]

    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111, projection='3d')

    def update_sym(frame):
        ax.clear()
        ang = frame * 0.02
        ca, sa = np.cos(ang), np.sin(ang)
        xpr = xp[:frame+1]*ca - yp[:frame+1]*sa
        ypr = xp[:frame+1]*sa + yp[:frame+1]*ca
        zpr = zp[:frame+1]
        xmr = xr_[:frame+1]*ca + yr_[:frame+1]*sa
        ymr = -xr_[:frame+1]*sa + yr_[:frame+1]*ca
        zmr = zr_[:frame+1]

        xpo = xpr + np.array([next(g) for g in fp_p[:frame+1]])
        ypo = ypr + np.array([next(g) for g in fp_p[:frame+1]])
        zpo = zpr + np.array([next(g) for g in fp_p[:frame+1]])

        xno = xmr + np.array([next(g) for g in fp_n[:frame+1]])
        yno = ymr + np.array([next(g) for g in fp_n[:frame+1]])
        zno = zmr + np.array([next(g) for g in fp_n[:frame+1]])

        ax.scatter(xpo, ypo, zpo, c='green', s=5)
        ax.scatter(xno, yno, zno, c='red',   s=5)
        ax.set_title('Symmetric Spectrum 3D Animation')
        ax.set_xlim(-radius, radius)
        ax.set_ylim(-radius, radius)
        ax.set_zlim(-radius, radius)

    writer_sym = PillowWriter(fps=25)
    writer_sym.progress_callback = make_progress_cb("Symmetric Anim")
    ani2 = FuncAnimation(fig, update_sym, frames=half, interval=50, blit=False)
    ani2.save(os.path.join(base_dir, 'symmetric_spectrum_simulation_animation.gif'), writer=writer_sym)
    plt.close(fig)
    print(f"[4/4] Symmetric animation saved.")

    # 4) Appendix T: Per‐Feature Shannon Contributions
    print("[4/4] Computing per‐feature Shannon entropy (Appendix T)…")

    # use 5 features for clarity
    n_features = 3
    N_samples  = 50

    # x‐axis: normalized spectrum positions 0 → 100%
    spectrum_positions = np.linspace(0, 100, N_samples)

    # simulate 3 random feature streams at each position
    feats = np.random.rand(N_samples, n_features)

    # normalize to probabilities p_ij(x)
    row_sums = feats.sum(axis=1, keepdims=True) + 1e-12
    probs    = feats / row_sums

    # compute per‐feature Shannon contributions
    S_feats = -probs * np.log(probs + 1e-12)

    # plot each S_j(x) with distinct colour
    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = plt.get_cmap("tab10")
    for j in range(n_features):
        ax.plot(
            spectrum_positions,
            S_feats[:, j],
            color=cmap(j),
            lw=1.5,
            label=f"feature {j+1}"
        )

    ax.set_title("Features Shannon Entropy over Spectrum [0–100%]")
    ax.set_xlabel("Normalized Spectrum (%)")
    ax.set_ylabel(r"$S_j(x) = -p_j(x)\,\log p_j(x)$")
    ax.grid(True)
    ax.legend(loc="upper right", ncol=1, fontsize="small")

    out_png = os.path.join(base_dir, "entropy_density_map.png")
    fig.savefig(out_png, dpi=300)
    plt.close(fig)
    print(f"[4/4] Per‐feature entropy plot saved to {out_png}")

def main():
    if '__file__' in globals():
        script_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        script_dir = os.getcwd()
    print(f"Script directory: {script_dir}")

    n_points = 50
    csv_f     = os.path.join(script_dir, 'spectrum_of_infinities_simulation_results.csv')

    results   = simulate_spectrum_of_infinities(n_points)
    save_results(results, csv_f)
    visualize_spectrum_of_infinities(results, script_dir)

    print("All simulations and visualizations completed successfully.")

if __name__ == "__main__":
    main()

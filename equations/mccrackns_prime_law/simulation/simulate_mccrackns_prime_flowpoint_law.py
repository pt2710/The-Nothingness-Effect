"""
Author   : Budd McCrackn
Email    : thenothingnesseffect@gmail.com
Usage    : python -m equations.mccrackns_prime_law.simulate_mccrackns_prime_flowpoint_law --n 32

Simulates McCrackn’s Prime Flowpoint Law and generates visualizations of the motif
binary tree with regime boundaries. All output is saved to 'visualizations/' and
'data_results/' directories relative to this script.
"""

import sys
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

def find_project_root(marker_file_or_folder="equations"):
    d = os.path.abspath(__file__)
    while True:
        d = os.path.dirname(d)
        if marker_file_or_folder in os.listdir(d):
            return d
        if d == os.path.dirname(d):
            break
    raise RuntimeError(f"Could not find project root with marker '{marker_file_or_folder}'.")

project_root = find_project_root()
sys.path.insert(0, project_root)

from equations.mccrackns_prime_law.mccrackns_prime_flowpoint_law import McCracknsPrimeFlowpointLaw
from equations.numbers_domains.numbers_domains import NumbersDomains

def ensure_output_dirs(script_dir):
    vis_dir = os.path.join(script_dir, "visualizations")
    data_dir = os.path.join(script_dir, "data_results")
    os.makedirs(vis_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    return vis_dir, data_dir

def draw_motif_tree(law, vis_dir):
    """
    Tegner præcis de motif-alfabeter som loven har opbygget på hvert regime.
    Forudsætter at `law.alphabet_snapshots` er en liste af lister, hvor
    alphabet_snapshots[0] = ["U1"], alphabet_snapshots[1] = ["U1","E1.0"], osv.
    Og at `law.get_parent_motif(level, child)` returnerer korrekt parent-label.
    """
    # antal regimes = dybden k
    k = len(law.alphabet_snapshots) - 1
    motifs_per_level = law.alphabet_snapshots  # index 0..k

    coords = {}
    fig, ax = plt.subplots(figsize=(2.0 * (k+1), 2.0 * (k+1)))

    def node_pos(level, idx):
        span = 1.0 / max(1, len(motifs_per_level[level]))
        x = (idx + 0.5) * span
        y = -level
        return x, y

    # 1) plot nodes
    for lvl, motifs in enumerate(motifs_per_level):
        for idx, label in enumerate(motifs):
            x, y = node_pos(lvl, idx)
            coords[(lvl, label)] = (x, y)
            ax.scatter(x, y, color='black', s=60, zorder=4)
            ax.text(x, y - 0.1, label, ha='center', va='top', fontsize=9, zorder=5)

    # 2) plot edges
    for lvl in range(1, len(motifs_per_level)):
        for label in motifs_per_level[lvl]:
            parent = law.get_parent_motif(level=lvl, child=label)
            x0, y0 = coords[(lvl-1, parent)]
            x1, y1 = coords[(lvl, label)]
            ax.plot([x0, x1], [y0, y1], color='gray', lw=1, zorder=3)

    # 3) regime­-linjer og labels
    for regime in range(1, k + 2):
        y = -regime
        ax.axhline(y, color="red", ls="--", lw=1, alpha=0.7, zorder=2)
        ax.text(0.5, y - 0.02, f"Regime {regime}", color="red",
                fontsize=10, ha="center", va="top", zorder=6)

    ax.set_xlim(0,1)
    ax.set_ylim(- (k + 2), 0.5)
    ax.invert_yaxis()
    ax.axis('off')
    plt.title(f"Motif binary tree and regime boundaries ($k={k}$)", pad=20)
    outfile = os.path.join(vis_dir, f"prime_motif_tree_k{k}.png")
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    plt.close()
    print(f"✓ Saved motif tree to {outfile}")

def plot_flowpoint_oscillation(law, vis_dir):
    """
    Plots the flowpoint oscillation and prime sequence,
    marking regime and motif/domain structure and annotating each dot with its motif label.
    """
    n = len(law.primes)
    idx = np.arange(1, n + 1)
    primes = np.array(law.primes)
    motifs = ["U1"] + law.motifs  # Motif label for each prime
    parities = [1] + law.parities

    fig, ax = plt.subplots(figsize=(13, 5))
    sc = ax.scatter(idx, primes, c=parities, cmap="bwr", s=50, edgecolor="k", zorder=5)

    for regime_idx in law.regimes:
        ax.axvline(regime_idx, color="red", ls="--", lw=1, alpha=0.5, zorder=1)

    # Annotate each dot with its motif label
    for i in range(n):
        ax.text(idx[i], primes[i] + 0.45, motifs[i],
                fontsize=8, ha="center", va="bottom", color="black", zorder=6, alpha=0.95)

    ax.set_xlabel("Prime index n")
    ax.set_ylabel("Prime $p_n$")
    ax.set_title("Prime sequence with flowpoint parity, motif/domain, and regime boundaries")
    plt.tight_layout()
    plt.savefig(os.path.join(vis_dir, "flowpoint_prime_sequence.png"))
    plt.close()

def plot_flowpoint_oscillation_strip(law, vis_dir):
    idx = np.arange(1, len(law.primes) + 1)
    parities = [1] + law.parities

    fig, axs = plt.subplots(2, 1, figsize=(12, 7), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

    axs[0].scatter(idx, law.primes, c=parities, cmap="bwr", s=30, edgecolor="k")
    axs[0].set_ylabel("Prime $p_n$")
    axs[0].set_title("Prime sequence with flowpoint parity and motif domain")

    axs[1].step(idx, parities, where='mid', color='k')
    axs[1].set_ylabel("Flowpoint parity")
    axs[1].set_yticks([-1, 1])
    axs[1].set_yticklabels(["-1", "+1"])
    axs[1].set_xlabel("Prime index $n$")

    plt.tight_layout()
    plt.savefig(os.path.join(vis_dir, "flowpoint_oscillation_strip.png"))
    plt.close()

def plot_prime_vs_imaginary_spectrum(law, gammas, vis_dir):
    idx = np.arange(1, len(law.primes) + 1)
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    axs[0].plot(idx, law.primes, marker='o', ms=3, label="Primes (real axis)")
    axs[0].set_ylabel("Prime $p_n$")
    axs[0].set_title("Prime sequence (real) vs Imaginary spectrum")

    axs[1].plot(idx, gammas, marker='x', ms=3, color="purple", label="Spectral $\gamma_n$")
    axs[1].set_ylabel("Im($\gamma_n$)")
    axs[1].set_xlabel("Prime index $n$")

    plt.tight_layout()
    plt.savefig(os.path.join(vis_dir, "prime_vs_spectral.png"))
    plt.close()

def main():
    """
    CLI entry for simulation and visualization.
    """
    parser = argparse.ArgumentParser(
        description="Simulate and visualize McCrackn’s Prime Flowpoint Law, including motif tree and flowpoint oscillation."
    )
    parser.add_argument("--n", type=int, default=32,
                        help="Number of primes to generate (default: 32)")
    parser.add_argument("--regime_k", type=int, default=4,
                        help="Depth of motif tree/regimes to visualize (default: 4)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    vis_dir, data_dir = ensure_output_dirs(script_dir)

    law = McCracknsPrimeFlowpointLaw(n_primes=args.n)
    law.generate()
    gammas = None
    law.export_all(script_dir)
    try:
        law.export_all_feather(script_dir)
    except Exception:
        pass

    draw_motif_tree(law, vis_dir)
    plot_flowpoint_oscillation(law, vis_dir)
    plot_flowpoint_oscillation_strip(law, vis_dir)
    if gammas is not None and len(gammas) == len(law.primes):
        plot_prime_vs_imaginary_spectrum(law, gammas, vis_dir)

if __name__ == "__main__":
    main()

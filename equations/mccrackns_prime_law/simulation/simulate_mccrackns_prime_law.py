#!/usr/bin/env python3
"""
Author  : B. McCrackn
Email   : thenothingnesseffect@gmail.com
Usage   : python -m equations.mccrackns_prime_law.simulate_mccrackns_prime_law --n 1000

Purpose
-------
Simulates McCrackn’s Prime Law and motif structure.
All figures are always saved to a subfolder 'visualizations' relative to this script.
All data tables (CSV/feather) are saved to a subfolder 'data_results' relative to this script.
This output folder structure is required by project standard and must not be changed.
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def find_project_root(marker_file_or_folder="equations"):
    """
    Detects project root directory by searching upward for a marker.

    Args:
        marker_file_or_folder (str): Folder or file used as marker.

    Returns:
        str: Absolute path to the project root.
    """
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

from equations.mccrackns_prime_law.mccrackns_prime_law import McCracknsPrimeLaw as mpl
from equations.numbers_domains.numbers_domains import NumbersDomains

def simulate_primes(n_primes: int = 1000):
    """
    Generates primes, gaps, motifs, domains, and regime points.

    Args:
        n_primes (int): Number of primes to generate.

    Returns:
        dict: Visualization-ready data (primes, gaps, motifs, domains, regime_points).
    """
    pgen = mpl(n_primes=n_primes, verbose=True)
    pgen.generate()
    primes = pgen.get_primes()
    gaps = [primes[i + 1] - primes[i] for i in range(len(primes) - 1)]
    motifs = pgen.get_motifs()
    motif_labels = [m[0] for m in motifs]
    motif_runs = [m[1] for m in motifs]
    regime_points = set(pgen.regime_points)

    domains = []
    nd = NumbersDomains()
    for lbl in motif_labels:
        if lbl == "U1":
            domains.append("U1")
        else:
            domains.append(lbl.split(".")[0])

    return {
        "primes": primes,
        "gaps": gaps,
        "motif_labels": motif_labels,
        "motif_runs": motif_runs,
        "domains": domains,
        "regime_points": regime_points,
    }

def plot_all(data, script_dir):
    """
    Plots all core figures to 'visualizations/', saves DataFrame to 'data_results/'.

    Args:
        data (dict): Output from simulate_primes().
        script_dir (str): Directory where this script is located (used for all output).
    """
    visual_dir = os.path.join(script_dir, "visualizations")
    data_dir = os.path.join(script_dir, "data_results")
    os.makedirs(visual_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    n = len(data["primes"])
    idx = np.arange(1, n + 1)
    assert len(data["gaps"]) == n - 1
    assert len(data["motif_labels"]) == n - 1
    assert len(data["motif_runs"]) == n - 1
    assert len(data["domains"]) == n - 1

    df = pd.DataFrame({
        "index": idx,
        "prime": data["primes"],
        "gap": [np.nan] + data["gaps"],
        "motif": ["U1"] + data["motif_labels"],
        "run": [1] + data["motif_runs"],
        "domain": ["U1"] + data["domains"],
    })

    # Save DataFrame to data_results in both feather and csv (project requirement)
    df.to_feather(os.path.join(data_dir, "motif_table.feather"))
    df.to_csv(os.path.join(data_dir, "motif_table.csv"), index=False)

    # Prime gaps plot
    plt.figure(figsize=(12, 6))
    plt.plot(df["index"][1:], df["gap"][1:], marker="o", linestyle="-", ms=2)
    for rp in sorted(data["regime_points"]):
        plt.axvline(rp, color="grey", lw=1, ls="--", alpha=0.5)
    plt.title("Prime Gaps")
    plt.xlabel("Prime index n")
    plt.ylabel("Gap = pₙ₊₁ − pₙ")
    plt.tight_layout()
    plt.savefig(os.path.join(visual_dir, "prime_gaps.png"))
    plt.close()

    # Motif distribution
    plt.figure(figsize=(12, 6))
    sns.countplot(x="motif", data=df.iloc[1:], order=sorted(set(data["motif_labels"])))
    plt.title("Motif Distribution")
    plt.xlabel("Motif label")
    plt.ylabel("Count")
    plt.xticks(rotation=60)
    plt.tight_layout()
    plt.savefig(os.path.join(visual_dir, "motif_distribution.png"))
    plt.close()

    # Domain distribution
    plt.figure(figsize=(8, 5))
    sns.countplot(x="domain", data=df.iloc[1:], order=sorted(set(data["domains"])))
    plt.title("Domain Distribution")
    plt.xlabel("Domain")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(visual_dir, "domain_distribution.png"))
    plt.close()

    # Motif run vs gap
    plt.figure(figsize=(10, 6))
    plt.scatter(
        df["run"][1:], df["gap"][1:],
        c=df["domain"][1:].astype("category").cat.codes,
        cmap="tab10", s=10, alpha=0.7
    )
    plt.title("Gap size vs. motif run index")
    plt.xlabel("Motif run index")
    plt.ylabel("Gap size")
    plt.tight_layout()
    plt.savefig(os.path.join(visual_dir, "gap_vs_run.png"))
    plt.close()

    # Regime marker plot over primes
    plt.figure(figsize=(12, 4))
    plt.plot(df["index"], df["prime"], marker=".", ms=2, linestyle="None", label="Prime")
    for rp in sorted(data["regime_points"]):
        plt.axvline(rp, color="red", lw=1, ls="--", alpha=0.6)
    plt.title("Prime sequence with regime boundaries")
    plt.xlabel("Prime index n")
    plt.ylabel("Prime")
    plt.tight_layout()
    plt.savefig(os.path.join(visual_dir, "primes_with_regimes.png"))
    plt.close()

def main():
    """
    CLI entry: parses arguments, runs simulation and plotting.

    All figures are saved to 'visualizations/' (relative to this script).
    All data tables are saved to 'data_results/' (relative to this script).
    This structure is required by the project ruleset.
    """
    parser = argparse.ArgumentParser(description="Simulate McCrackn’s Prime Law and visualize motifs/gaps.")
    parser.add_argument("--n", type=int, default=1000, help="Number of primes to simulate (default: 1000)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"Simulating McCrackn’s Prime Law with n={args.n} …")
    data = simulate_primes(n_primes=args.n)
    print("Plotting and saving all output …")
    plot_all(data, script_dir=script_dir)
    print(f"Figures saved to:   {os.path.join(script_dir, 'visualizations')}")
    print(f"Data tables saved to: {os.path.join(script_dir, 'data_results')}")

if __name__ == "__main__":
    main()

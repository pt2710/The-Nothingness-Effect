#!/usr/bin/env python3
"""
Author  : B. McCrackn
Email   : thenothingnesseffect@gmail.com
Usage   : python simulate_dfi.py

Simulates global temperature diffusion over ISO countries,
computes Dynamic Fluctuation Index (DFI) time series,
and visualizes entropy evolution and a rotating 3D globe animation.

All data and visualizations are saved in the local visualizations/ directory.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import pycountry

# Attempt to import pycountry_convert for region grouping
try:
    import pycountry_convert
except ImportError:
    pycountry_convert = None

def find_project_root(marker_file_or_folder="equations"):
    """
    Search upwards for the project root containing the given marker folder.
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

from equations.dynamic_fluctuation_index.dfi import DynamicFluctuationIndex

def print_progress_bar(iteration, total, start_time, bar_length=40):
    """
    Dynamic terminal progress bar with elapsed and estimated remaining time.
    """
    percent = iteration / total
    elapsed = time.time() - start_time
    est_total = elapsed / percent if percent > 0 else 0
    time_left = est_total - elapsed if percent > 0 else 0
    bar_fill = int(bar_length * percent)
    bar = '#' * bar_fill + '-' * (bar_length - bar_fill)
    sys.stdout.write(
        f'\r[{"{:>6.1f}%".format(percent*100)}] |{bar}| '
        f'Elapsed: {elapsed:6.2f}s | Left: {time_left:6.2f}s'
    )
    sys.stdout.flush()
    if iteration == total:
        print()

def get_country_list():
    """
    Return a list of ISO country names.
    """
    return [c.name for c in pycountry.countries]

def simulate_global_temps(n_steps=365, noise_scale=16.0, show_progress=True):
    """
    Generate highly volatile synthetic global temperatures with extreme shocks.
    Returns a DataFrame of shape (n_steps, n_countries).
    """
    countries = get_country_list()
    n_countries = len(countries)
    df = pd.DataFrame(index=range(n_steps), columns=countries, dtype=float)
    days = np.arange(n_steps)
    global_trend = 30 + 45 * np.sin(2 * np.pi * days / n_steps)
    offsets = np.random.uniform(-40, 40, size=n_countries)
    df.iloc[0] = global_trend[0] + offsets + np.random.randn(n_countries) * noise_scale
    start_time = time.time()
    for t in range(1, n_steps):
        prev = df.iloc[t - 1].values
        next_vals = prev + 0.3 * (global_trend[t] - prev) + np.random.randn(n_countries) * noise_scale
        # 20% chance each day for a "heatwave" or "cold snap"
        if np.random.rand() < 0.2:
            affected = np.random.choice(n_countries, size=np.random.randint(1, max(2, n_countries//15)), replace=False)
            temp_shock = np.random.uniform(25, 60, size=affected.size) * np.random.choice([-1, 1], size=affected.size)
            next_vals[affected] += temp_shock
        df.iloc[t] = next_vals
        if show_progress:
            print_progress_bar(t, n_steps - 1, start_time)
    if show_progress:
        print_progress_bar(n_steps - 1, n_steps - 1, start_time)
    return df

def build_globe_coords(countries):
    """
    Assign random latitude and longitude to each country, return Nx3 array.
    """
    n = len(countries)
    lats = np.random.uniform(-90, 90, size=n) * np.pi/180
    lons = np.random.uniform(-180, 180, size=n) * np.pi/180
    x = np.cos(lats) * np.cos(lons)
    y = np.cos(lats) * np.sin(lons)
    z = np.sin(lats)
    return np.vstack((x, y, z)).T

def animate_globe(df_temps, coords, out_file):
    """
    Create and save a rotating globe animation, coloring each country point
    by its current relative entropy (temperature/volatility).
    """
    n_steps, n_countries = df_temps.shape
    engine = DynamicFluctuationIndex()
    ent = engine.dfi(df_temps)
    rel_ent = np.vstack([ent[c]["Relative_Entropy"] for c in df_temps.columns]).T

    p_low = float(np.percentile(rel_ent, 10))
    p_high = float(np.percentile(rel_ent, 90))
    p_mid = float(np.median(rel_ent))
    if not (p_low < p_mid < p_high):
        p_low, p_mid, p_high = float(np.min(rel_ent)), float(np.mean(rel_ent)), float(np.max(rel_ent))
        if not (p_low < p_mid < p_high):
            p_low, p_mid, p_high = 0.0, 0.5, 1.0
    norm = TwoSlopeNorm(vmin=p_low, vcenter=p_mid, vmax=p_high)

    fig = plt.figure(figsize=(9,9))
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(
        coords[:,0], coords[:,1], coords[:,2],
        c=rel_ent[0], cmap='seismic', norm=norm, s=28
    )
    mappable = plt.cm.ScalarMappable(cmap='seismic', norm=norm)
    mappable.set_array([])
    cbar = plt.colorbar(mappable, ax=ax, fraction=0.03, pad=0.07, shrink=0.8)
    cbar.set_label('Relative Entropy / Temperature', fontsize=12)

    ax.set_axis_off()
    ax.view_init(elev=30, azim=0)
    rotation_period = n_steps * 2

    def update(day):
        sc.set_array(rel_ent[day])
        azim = (day * 360 / rotation_period) % 360
        ax.view_init(elev=30, azim=azim)
        ax.set_title(f"Day {day}: Avg Entropy {rel_ent[day].mean():.2f}", fontsize=12)

    anim = animation.FuncAnimation(fig, update, frames=n_steps, interval=100)
    print(f"\n💾  Saving globe animation to {out_file} ...")
    start = time.time()
    anim.save(out_file, fps=10, dpi=150, codec='libx264')
    print_progress_bar(1, 1, start)
    plt.close(fig)

def save_entropy_frame(coords, rel_ent, day, out_file):
    """
    Save a 3D globe snapshot of relative entropy at a specific simulation frame.
    """
    p_low = float(np.percentile(rel_ent, 10))
    p_high = float(np.percentile(rel_ent, 90))
    p_mid = float(np.median(rel_ent))
    if not (p_low < p_mid < p_high):
        p_low, p_mid, p_high = np.min(rel_ent), np.mean(rel_ent), np.max(rel_ent)
        if not (p_low < p_mid < p_high):
            p_low, p_mid, p_high = 0.0, 0.5, 1.0
    norm = TwoSlopeNorm(vmin=p_low, vcenter=p_mid, vmax=p_high)
    fig = plt.figure(figsize=(9, 9))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(
        coords[:, 0], coords[:, 1], coords[:, 2],
        c=rel_ent[day], cmap='seismic', norm=norm, s=28
    )
    mappable = plt.cm.ScalarMappable(cmap='seismic', norm=norm)
    mappable.set_array([])
    cbar = plt.colorbar(mappable, ax=ax, fraction=0.03, pad=0.07, shrink=0.8)
    cbar.set_label('Relative Entropy / Temperature', fontsize=12)
    ax.set_axis_off()
    azim = (day * 360 / (rel_ent.shape[0] * 2)) % 360
    ax.view_init(elev=30, azim=azim)
    ax.set_title(f"Day {day}: Avg Entropy {rel_ent[day].mean():.2f}", fontsize=12)
    plt.tight_layout()
    plt.savefig(out_file, dpi=180)
    plt.close(fig)

def get_country_region_map(country_names):
    """
    Map each country to a region using pycountry_convert.
    Returns a dict: region -> list of (country, idx)
    Regions: Europe, Asia, Africa, Americas, Oceania, Other
    """
    region_map = {"Europe": [], "Asia": [], "Africa": [], "Americas": [], "Oceania": [], "Other": []}
    if pycountry_convert is None:
        for i, name in enumerate(country_names):
            region_map["Other"].append((name, i))
        return region_map

    for i, name in enumerate(country_names):
        try:
            c = pycountry.countries.get(name=name)
            if c is None:
                region_map["Other"].append((name, i))
                continue
            alpha2 = c.alpha_2
            cont = pycountry_convert.country_alpha2_to_continent_code(alpha2)
            if cont == "EU":
                region_map["Europe"].append((name, i))
            elif cont == "AS":
                region_map["Asia"].append((name, i))
            elif cont == "AF":
                region_map["Africa"].append((name, i))
            elif cont == "NA" or cont == "SA":
                region_map["Americas"].append((name, i))
            elif cont == "OC":
                region_map["Oceania"].append((name, i))
            else:
                region_map["Other"].append((name, i))
        except Exception:
            region_map["Other"].append((name, i))
    region_map = {k: v for k, v in region_map.items() if len(v) > 0}
    return region_map

def save_sigma_ft_frame_regions(df_temps, day, out_file):
    """
    Calculates and plots σ_x^{F_t} per region at the specified timestep, using DFI over regional means.
    Also saves a CSV with the full region-level sigma time series.
    Args:
        df_temps (DataFrame): Temperature data, columns = countries.
        day (int): Time index to plot.
        out_file (str): Output PNG filename.
    """
    country_names = list(df_temps.columns)
    region_map = get_country_region_map(country_names)
    region_names = [r for r in region_map if len(region_map[r]) > 0]
    region_names_sorted = sorted(region_names)
    region_series = {}
    for region in region_names_sorted:
        idxs = [i for _, i in region_map[region]]
        arr = df_temps.iloc[:, idxs].mean(axis=1)
        region_series[region] = arr
    df_regions = pd.DataFrame(region_series)
    engine = DynamicFluctuationIndex()
    ent_region = engine.dfi(df_regions)
    has_sigma = "Sigma" in ent_region[next(iter(ent_region))]
    T = df_regions.shape[0]
    n_vars = df_regions.shape[1]
    sigma_timeseries = np.full((T, n_vars), np.nan)
    if has_sigma:
        for k, r in enumerate(df_regions.columns):
            sigma_timeseries[:, k] = ent_region[r]["Sigma"]
        sigma_ft_region = sigma_timeseries[day, :]
    else:
        rel_entropies = np.vstack([ent_region[r]["Relative_Entropy"] for r in df_regions.columns]).T
        for t in range(T):
            for j in range(n_vars):
                numer = rel_entropies[t, j]
                denom = np.sum(np.delete(rel_entropies[t], j))
                if (
                    n_vars > 1 and
                    np.isfinite(numer) and
                    np.isfinite(denom) and
                    denom != 0
                ):
                    sigma_val = numer * (n_vars - 1) / denom
                else:
                    sigma_val = np.nan
                sigma_timeseries[t, j] = sigma_val
        sigma_ft_region = sigma_timeseries[day, :]
    # Save CSV
    csv_path = out_file.replace(".png", "_timeseries.csv")
    sigma_df = pd.DataFrame(sigma_timeseries, columns=region_names_sorted)
    sigma_df.index.name = "timestep"
    sigma_df.to_csv(csv_path)
    # Plot
    fig, ax = plt.subplots(figsize=(2.2 + 1.4 * len(region_names_sorted), 6))
    bar_colors = np.where(np.array(sigma_ft_region) >= 0, "firebrick", "royalblue")
    bars = ax.bar(np.arange(len(region_names_sorted)), sigma_ft_region, color=bar_colors, alpha=0.93, width=0.85)
    ax.axhline(0, color="k", lw=1)
    ax.set_ylabel(r"Region $\sigma_x^{F_t}$", fontsize=15)
    ax.set_xlabel("Region", fontsize=14)
    ax.set_xticks(np.arange(len(region_names_sorted)))
    ax.set_xticklabels(region_names_sorted, rotation=17, ha="center", fontsize=15)
    ax.set_title(rf"Regional entropic deviation index $\sigma_x^{{F_t}}$ at $t={day}$", fontsize=16, pad=12)
    vmax = np.nanmax(np.abs(sigma_ft_region)) if len(sigma_ft_region) > 0 else 1
    if np.isnan(vmax) or vmax == 0:
        vmax = 1
    ax.set_ylim(-1.1 * vmax, 1.1 * vmax)
    for i, bar in enumerate(bars):
        y = bar.get_height()
        if not np.isnan(y):
            ax.text(bar.get_x() + bar.get_width()/2, y + 0.045*vmax*np.sign(y),
                    f"{y:.2f}", ha="center", va="bottom" if y >= 0 else "top", fontsize=13)
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(out_file, dpi=180)
    plt.close(fig)

def save_sigma_ft_frame_grouped(sigma_ft, day, country_names, out_file, max_bars_per_region=16):
    """
    Save a bar plot of σ_x^{F_t} at the specified timestep, grouped by region.
    Each bar is a country; regions shown separately, sorted by mean |σ|, max bars/region enforced.
    """
    region_map = get_country_region_map(country_names)
    n_regions = len(region_map)
    fig_height = 2.5 + 2.2 * n_regions
    widest = max([min(len(v), max_bars_per_region) for v in region_map.values()])
    fig_width = max(13, 1.4 * widest)
    fig, axes = plt.subplots(n_regions, 1, figsize=(fig_width, fig_height), squeeze=False)
    if n_regions == 1:
        axes = np.array([[axes[0, 0]]])
    regions = list(region_map.keys())
    for idx, region in enumerate(regions):
        countries = region_map[region]
        vals = np.array([sigma_ft[day, i] for _, i in countries])
        labels = [name for name, _ in countries]
        sort_idx = np.argsort(-np.abs(vals))
        show_idx = sort_idx[:max_bars_per_region]
        plot_vals = vals[show_idx]
        plot_labels = [labels[i] for i in show_idx]
        bar_colors = np.where(plot_vals >= 0, "firebrick", "royalblue")
        ax = axes[idx, 0]
        bars = ax.bar(range(len(plot_vals)), plot_vals, color=bar_colors, alpha=0.95, width=0.86)
        ax.axhline(0, color="k", lw=1)
        n_labels = len(plot_labels)
        if n_labels <= 10:
            label_fontsize = 17
        elif n_labels <= 15:
            label_fontsize = 15
        else:
            label_fontsize = 13
        ax.set_xticks(range(n_labels))
        ax.set_xticklabels(plot_labels, rotation=28, ha="right", fontsize=label_fontsize)
        ax.set_ylabel(region, fontsize=12, rotation=0, labelpad=34, va="center")
        ax.set_xlim(-0.6, n_labels - 0.4)
        vmax = np.max(np.abs(plot_vals)) if plot_vals.size > 0 else 1
        ax.set_ylim(-1.07 * vmax, 1.07 * vmax)
        if idx < n_regions - 1:
            ax.xaxis.set_ticklabels([])
        ax.grid(axis="y", alpha=0.23)
        if n_labels > 12:
            plt.setp(ax.get_xticklabels(), ha="right", rotation=30)
            for label in ax.get_xticklabels():
                label.set_y(-0.04)
    fig.suptitle(rf"Entropic deviation index $\sigma_x^{{F_t}}$ at $t={day}$ (region-grouped, bars: country)", fontsize=15, y=0.995)
    plt.tight_layout(rect=[0, 0.04, 1, 0.97])
    plt.savefig(out_file, dpi=180)
    plt.close(fig)

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(current_dir, "visualizations")
    os.makedirs(out_dir, exist_ok=True)
    start_global = time.time()

    print("🛰️  Simulating global temperature scenario...")
    df_temps = simulate_global_temps(show_progress=True)
    print(f"\n▶️  Simulated {df_temps.shape[0]} days × {df_temps.shape[1]} countries")

    print("⚙️  Computing Dynamic Fluctuation Index...")
    engine = DynamicFluctuationIndex()
    start = time.time()
    ent = engine.dfi(df_temps)
    print_progress_bar(1, 1, start)

    rel_entropies = np.vstack([ent[c]["Relative_Entropy"] for c in df_temps.columns]).T
    avg_entropy = rel_entropies.mean(axis=1)
    sigma_ft = np.vstack([ent[c]["Sigma"] for c in df_temps.columns]).T \
        if "Sigma" in ent[next(iter(ent))] \
        else np.full_like(rel_entropies, np.nan)
    if np.isnan(sigma_ft).all():
        n_vars = rel_entropies.shape[1]
        for t in range(rel_entropies.shape[0]):
            total = np.sum(rel_entropies[t])
            sigma_ft[t] = total * (n_vars-1) / (np.sum(rel_entropies[t]) * n_vars) if n_vars > 1 else np.nan

    out_csv = os.path.join(out_dir, "global_avg_relative_entropy.csv")
    out_df = pd.DataFrame({"day": np.arange(len(avg_entropy)), "avg_relative_entropy": avg_entropy})
    out_df.to_csv(out_csv, index=False)
    print(f"💾  Wrote average entropy CSV → {out_csv}")

    plt.figure(figsize=(10, 4))
    plt.plot(out_df["day"], out_df["avg_relative_entropy"], lw=2)
    plt.title("Global Average Relative Entropy Over Time")
    plt.xlabel("Day")
    plt.ylabel("Avg Relative Entropy")
    plt.grid(True)
    plt.tight_layout()
    out_png = os.path.join(out_dir, "global_avg_relative_entropy.png")
    plt.savefig(out_png, dpi=150)
    print(f"💾  Wrote plot → {out_png}")
    plt.close()

    coords = build_globe_coords(df_temps.columns)
    out_mp4 = os.path.join(out_dir, "globe_entropy.mp4")
    animate_globe(df_temps, coords, out_mp4)

    frame_idx = 240
    frame_file = os.path.join(out_dir, f"sigma_frame_{frame_idx}.png")
    save_entropy_frame(coords, rel_entropies, frame_idx, frame_file)

    # --- Region-level DFI σ_x^{F_t} bar plot ---
    sigmaft_file = os.path.join(out_dir, f"sigma_ft_frame_{frame_idx}.png")
    save_sigma_ft_frame_regions(df_temps, frame_idx, sigmaft_file)
    print(f"💾  Saved region-level sigma_ft frame {frame_idx} → {sigmaft_file}")

    # --- Optional: country-level grouped sigma plot (old style) ---
    # country_sigmaft_file = os.path.join(out_dir, f"sigma_ft_country_frame_{frame_idx}.png")
    # save_sigma_ft_frame_grouped(sigma_ft, frame_idx, list(df_temps.columns), country_sigmaft_file)

    print(f"\nProcess done. Total elapsed: {time.time() - start_global:.2f}s\n")

if __name__ == "__main__":
    main()

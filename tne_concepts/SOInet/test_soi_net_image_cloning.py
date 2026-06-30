# test_soi_net_image_cloning.py

import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from skimage.data import camera, astronaut
from skimage.color import rgb2gray
from skimage.io import imread, imsave

from soi_net import SOInet
import soi_pgnn_analytics as spa

# --- Output directories ---
OUT_DIR   = 'test_image_cloning_data'
IMG_DIR   = os.path.join(OUT_DIR, 'images')
FIG_DIR   = os.path.join(OUT_DIR, 'figures')
pgqenn_FIG  = os.path.join(FIG_DIR, 'pgqenn_networks')
ROW_DIR   = os.path.join(OUT_DIR, 'row_profiles')
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(pgqenn_FIG, exist_ok=True)
os.makedirs(ROW_DIR, exist_ok=True)

def plot_images(orig, clone, spectrum, name, figdir):
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    plt.imshow(orig, cmap='gray')
    plt.title('Original')
    plt.axis('off')
    plt.subplot(1, 3, 2)
    plt.imshow(clone, cmap='gray')
    plt.title('Cloned/Mirrored')
    plt.axis('off')
    plt.subplot(1, 3, 3)
    plt.imshow(np.log1p(np.abs(spectrum)), cmap='magma')
    plt.title('Log Abs(Spectrum)')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, f"{name}_compare.png"))
    plt.close()

def plot_profiles(orig, clone, name, figdir):
    """Plot and save the center row of original and cloned image (analogy to sound waveform compare)."""
    row = orig.shape[0] // 2
    t = np.arange(orig.shape[1])
    plt.figure(figsize=(8, 3))
    plt.plot(t, orig[row, :], label='Original row', color='royalblue')
    plt.plot(t, clone[row, :], label='Cloned row', color='firebrick', alpha=0.7, linestyle='--')
    plt.title(f"{name}: Center Row Profile")
    plt.xlabel("Pixel index")
    plt.ylabel("Intensity")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, f"{name}_row_profile.png"))
    plt.close()

def mse_snr(orig, clone):
    mse = np.mean((orig - clone)**2)
    snr = 10 * np.log10(np.sum(orig**2) / (np.sum((orig - clone)**2) + 1e-12))
    return mse, snr

def main():
    start_time = time.time()
    print("🚀 [SOI Net] Initializing for IMAGE CLONING (bidirectional/generative mode)...", flush=True)

    soi_params = {'normalize_to': 1.0, 'adv_mode': True, 'type': 'symmetric'}
    net = SOInet(soi_params=soi_params)

    # --- IMAGE TESTSET: (use skimage, numpy, or your own images)
    test_imgs = [
        {'label': 'camera',    'data': camera().astype(float) / 255.0},
        {'label': 'astronaut', 'data': rgb2gray(astronaut()).astype(float)},
        # Optionally: add your own images here
        # {'label': 'custom',  'data': rgb2gray(imread('path_to_image.png'))},
    ]

    results = []
    for i, imgdict in enumerate(test_imgs):
        print(f"\n🖼️ [{i}] Cloning: {imgdict['label']}...")
        img = imgdict['data']
        img = (img - img.min()) / (img.max() - img.min())  # Normalize

        # --- Save input
        imsave(os.path.join(IMG_DIR, f"{imgdict['label']}_input.png"), (img*255).astype(np.uint8))

        # ==== ENCODE ====
        spectrum = np.fft.fft2(img)
        mirrored_spectrum = -spectrum  # Mirror as with audio

        # ==== DECODE ====
        cloned = np.fft.ifft2(mirrored_spectrum).real
        cloned = np.clip(cloned, 0, 1)
        imsave(os.path.join(IMG_DIR, f"{imgdict['label']}_cloned.png"), (cloned*255).astype(np.uint8))

        # --- Plots: image, spectrum, row profile
        plot_images(img, cloned, mirrored_spectrum, imgdict['label'], FIG_DIR)
        plot_profiles(img, cloned, imgdict['label'], ROW_DIR)

        # --- Metrics
        mse, snr = mse_snr(img, cloned)
        print(f"  [MSE: {mse:.6f} | SNR: {snr:.2f} dB]")
        results.append({'label': imgdict['label'], 'mse': mse, 'snr': snr})

    # ---- Save metrics table
    pd.DataFrame(results).to_csv(os.path.join(OUT_DIR, "cloning_metrics.csv"), index=False)
    print("\n✅ All image cloning complete! Metrics saved.")

    # ==== pgqenn/SOI/DFI ANALYTICS ==== (identical to your sound scripts)
    print("\n📊 Generating SOI/pgqenn analytics and visualizations...")
    net_results = net.run()
    histories    = net_results['histories']
    elastic_pi   = net_results['elastic_pi']
    dfi_results  = net_results['dfi']

    # --- Save Elastic Pi analytics
    np.savez(os.path.join(FIG_DIR, "elastic_pi_results.npz"),
             x=elastic_pi["x"], S=elastic_pi["S"], piE=elastic_pi["piE"], lap=elastic_pi["lap"])
    pd.DataFrame({"x": elastic_pi["x"], "S": elastic_pi["S"], "piE": elastic_pi["piE"], "lap": elastic_pi["lap"]}) \
        .to_csv(os.path.join(FIG_DIR, "elastic_pi_results.csv"), index=False)

    # --- Save DFI analytics
    for feat, featdict in dfi_results.items():
        df = pd.DataFrame(featdict)
        df.to_csv(os.path.join(FIG_DIR, f"dfi_{feat}.csv"), index=False)

    # ---- DFI/Flowpoint weight evolution ----
    T = 15
    hist_records     = []
    weight_snapshots = []
    for net_idx, (_, edges, _, _, _, weight_map, _) in enumerate(histories):
        snapshots = []
        for epoch in range(T):
            flat = []
            for u in weight_map:
                for v, w in weight_map[u].items():
                    if u < v:
                        hist_records.append({
                            'network': net_idx,
                            'epoch':   epoch,
                            'u':       u,
                            'v':       v,
                            'weight':  w
                        })
                        flat.append(w)
            snapshots.append(flat)
            for u in list(weight_map):
                weight_map[u] = spa.dfi_update(weight_map[u], step=epoch, alpha=0.25)
        weight_snapshots.append(snapshots)

    hist_df = pd.DataFrame(hist_records)
    hist_df.to_csv(os.path.join(FIG_DIR, 'weight_evolution.csv'), index=False)
    for net_idx in hist_df['network'].unique():
        hist_df[hist_df.network==net_idx].to_csv(
            os.path.join(FIG_DIR, f'weight_evolution_net{net_idx}.csv'), index=False)

    stats = hist_df.groupby(['network','epoch'])['weight'].agg(['mean','std']).reset_index()
    stats.to_csv(os.path.join(FIG_DIR, 'weight_stats.csv'), index=False)
    for net_idx in stats['network'].unique():
        stats[stats.network==net_idx].to_csv(
            os.path.join(FIG_DIR, f'weight_stats_net{net_idx}.csv'), index=False)

    # ---- Full analytics suite per net ----
    total = len(histories)
    print(f"📊 Generating visuals for {total} networks…", flush=True)

    for i, (
        primes, edges,
        all_coords, all_edges, all_primes,
        weight_map, shell_nodes
    ) in enumerate(histories):
        net_start = time.time()
        degrees      = {p: len(edges[p]) for p in primes}
        motif_counts = spa.motif_histogram(primes)

        # ---- Use pgqenn analytics plotting suite ----
        spa.plot_spherical_3d(primes, all_coords[-1], degrees, None, weight_map, i, None, fig_dir=pgqenn_FIG)
        spa.plot_weight_histograms(hist_df[hist_df.network==i], i, fig_dir=pgqenn_FIG)
        spa.plot_entropy_per_epoch(weight_snapshots[i], i, fig_dir=pgqenn_FIG)
        spa.plot_network_growth_animation(all_coords, all_edges, all_primes, i, fig_dir=pgqenn_FIG)
        spa.plot_degree_hist(degrees, i, fig_dir=pgqenn_FIG)
        spa.plot_shell_population(shell_nodes, i, fig_dir=pgqenn_FIG)
        spa.plot_motif_histogram(motif_counts, i, fig_dir=pgqenn_FIG)
        spa.plot_adjacency_heatmap(edges, primes, i, fig_dir=pgqenn_FIG)
        spa.plot_spectral_embedding(edges, all_coords[-1], primes, i, fig_dir=pgqenn_FIG)
        spa.plot_betweenness(edges, primes, all_coords[-1], i, fig_dir=pgqenn_FIG)
        spa.plot_flow_path(edges, all_coords[-1], primes, i, fig_dir=pgqenn_FIG)
        spa.save_pairwise_distances(coords=all_coords[-1], primes=primes, net_idx=i, fig_dir=pgqenn_FIG)
        spa.plot_connected_components(edges, primes, i, fig_dir=pgqenn_FIG) 
        spa.plot_clustering_coefficients(edges, primes, i, fig_dir=pgqenn_FIG)
        this_dur = time.time() - net_start
        print(f"[Net {i+1}/{total}] analytics in {this_dur:.1f}s", flush=True)

    total_time = time.time() - start_time
    print(f"\n🏁 All image cloning, analytics & figures complete in {total_time:.1f}s", flush=True)
    print(f"Results and figures in: {OUT_DIR}/")

if __name__ == "__main__":
    main()

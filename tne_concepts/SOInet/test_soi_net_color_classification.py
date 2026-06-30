# test_soi_net_color_classification.py

import os
import time
import numpy as np
import pandas as pd

from soi_net import SOInet
import soi_pgnn_analytics as spa

from sklearn.metrics import (
    precision_score, recall_score, f1_score, classification_report, confusion_matrix
)
import matplotlib.pyplot as plt

# --- Ensure output directories exist ---
os.makedirs('test_color_classification_data/soi_net_test_figures', exist_ok=True)
os.makedirs('test_color_classification_data/soi_net_test_data',   exist_ok=True)

def plot_confusion_matrix_heatmap(cm, class_labels, fig_path):
    """Plot and save confusion matrix heatmap."""
    plt.figure(figsize=(4,4))
    plt.imshow(cm, cmap='Blues', interpolation='nearest')
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.xticks(np.arange(len(class_labels)), class_labels)
    plt.yticks(np.arange(len(class_labels)), class_labels)
    for i in range(len(class_labels)):
        for j in range(len(class_labels)):
            plt.text(j, i, cm[i, j], ha='center', va='center', color='black')
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(fig_path)
    plt.close()

def main():
    start_time = time.time()
    print("🚀 Initializing SOInet & building PGNN histories...", flush=True)

    # Instantiate and run SOInet to get all core results
    net = SOInet()
    results = net.run()
    histories    = results['histories']
    elastic_pi   = results['elastic_pi']
    dfi_results  = results['dfi']

    print("✅ SOInet core computation complete.", flush=True)

    # ----- Save Elastic Pi analytics -----
    np.savez("test_color_classification_data/soi_net_test_data/elastic_pi_results.npz",
             x=elastic_pi["x"], S=elastic_pi["S"], piE=elastic_pi["piE"], lap=elastic_pi["lap"])
    pd.DataFrame({"x": elastic_pi["x"], "S": elastic_pi["S"],
                  "piE": elastic_pi["piE"], "lap": elastic_pi["lap"]}) \
        .to_csv("test_color_classification_data/soi_net_test_data/elastic_pi_results.csv", index=False)
    print("✅ Elastic Pi analytics saved.", flush=True)

    # ----- Save DFI analytics -----
    for feat, featdict in dfi_results.items():
        df = pd.DataFrame(featdict)
        df.to_csv(f"test_color_classification_data/soi_net_test_data/dfi_{feat}.csv", index=False)
    print("✅ DFI entropical data saved.", flush=True)

    # ----- DFI/Flowpoint weight evolution -----
    T = 15
    hist_records     = []
    weight_snapshots = []
    for net_idx, (_, edges, _, _, _, weight_map, _) in enumerate(histories):
        snapshots = []
        for epoch in range(T):
            flat = []
            for u in weight_map:
                for v,w in weight_map[u].items():
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
    hist_df.to_csv('test_color_classification_data/soi_net_test_data/weight_evolution.csv', index=False)
    for net_idx in hist_df['network'].unique():
        hist_df[hist_df.network==net_idx].to_csv(
            f"test_color_classification_data/soi_net_test_data/weight_evolution_net{net_idx}.csv", index=False)
    print("✅ Weight evolution data saved.", flush=True)

    # ----- Weight stats -----
    stats = hist_df.groupby(['network','epoch'])['weight'].agg(['mean','std']).reset_index()
    stats.to_csv('test_color_classification_data/soi_net_test_data/weight_stats.csv', index=False)
    for net_idx in stats['network'].unique():
        stats[stats.network==net_idx].to_csv(
            f"test_color_classification_data/soi_net_test_data/weight_stats_net{net_idx}.csv", index=False)
    print("✅ Weight stats saved.", flush=True)

    # ----- Spectrum color classification -----
    prototypes = np.array([650,550,475])
    class_labels = ["Red", "Green", "Blue"]  # match order to prototypes!
    np.random.seed(42)
    wavelengths = np.clip(
        np.linspace(450,650,300) + np.random.normal(0,5,300),
        450,650
    )
    true = np.zeros_like(wavelengths, dtype=int)
    true[wavelengths<525] = 2   # Blue
    mask = (wavelengths>=525)&(wavelengths<600)
    true[mask] = 1              # Green
    true[wavelengths>=600] = 0  # Red
    pred = np.argmin(np.abs(wavelengths[:,None]-prototypes[None,:]), axis=1)

    # --- METRIC CALCULATION ---
    acc  = float((pred==true).mean())
    precision = precision_score(true, pred, average=None, zero_division=0)
    recall    = recall_score(true, pred, average=None, zero_division=0)
    f1        = f1_score(true, pred, average=None, zero_division=0)
    macro_f1  = f1_score(true, pred, average='macro')
    micro_f1  = f1_score(true, pred, average='micro')
    conf_mat  = confusion_matrix(true, pred)
    class_report = classification_report(true, pred, target_names=class_labels, output_dict=True)
    # Terminal report (readable)
    print("=== Color Classification Report ===")
    print(classification_report(true, pred, target_names=class_labels, digits=4))
    print(f"Accuracy: {acc:.4f} | Macro-F1: {macro_f1:.4f} | Micro-F1: {micro_f1:.4f}")

    # Save metrics CSV
    metrics_df = pd.DataFrame({
        'class': class_labels,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    })
    metrics_df.loc['macro'] = ['macro', '', '', macro_f1]
    metrics_df.loc['micro'] = ['micro', '', '', micro_f1]
    metrics_df['accuracy'] = acc
    metrics_df.to_csv('test_color_classification_data/soi_net_test_data/metrics.csv', index=False)
    # Save sklearn's classification report as well
    pd.DataFrame(class_report).T.to_csv('test_color_classification_data/soi_net_test_data/classification_report.csv')

    # Confusion matrix CSV
    pd.DataFrame(conf_mat, index=[f"true_{l}" for l in class_labels], columns=[f"pred_{l}" for l in class_labels]) \
        .to_csv('test_color_classification_data/soi_net_test_data/confusion_matrix.csv')
    # Confusion matrix heatmap
    plot_confusion_matrix_heatmap(conf_mat, class_labels,
        'test_color_classification_data/soi_net_test_figures/confusion_matrix_heatmap.png')
    print("✅ Spectrum classification benchmark & metrics saved.", flush=True)

    # ----- Degree distribution -----
    deg_records = []
    for net_idx, (primes, edges, *_ ) in enumerate(histories):
        for p in primes:
            deg_records.append({'network': net_idx, 'node': p, 'degree': len(edges[p])})
    deg_df = pd.DataFrame(deg_records)
    deg_df.to_csv('test_color_classification_data/soi_net_test_data/degree_distribution.csv', index=False)
    for net_idx in deg_df['network'].unique():
        deg_df[deg_df.network==net_idx].to_csv(
            f"test_color_classification_data/soi_net_test_data/degree_distribution_net{net_idx}.csv", index=False)
    print("✅ Degree distributions saved.", flush=True)

    # ==== VISUALIZE WITH PROGRESS & ETA ====
    total = len(histories)
    print(f"📊 Generating visuals for {total} networks…", flush=True)

    for i, (
        primes, edges,
        all_coords, all_edges, all_primes,
        weight_map, shell_nodes
    ) in enumerate(histories):
        net_start = time.time()

        # ---- PREP ----
        degrees      = {p: len(edges[p]) for p in primes}
        motif_counts = spa.motif_histogram(primes)

        # ---- Call analytics/plotting utils from soi_pgnn_analytics.py ----
        spa.plot_spherical_3d(
            primes,
            coords=all_coords[-1],
            degrees=degrees,
            motifs=None,
            edge_weights=weight_map,
            net_idx=i,
            epoch=None,
            fig_dir='test_color_classification_data/soi_net_test_figures'
        )
        spa.plot_weight_histograms(hist_df[hist_df.network==i], i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_entropy_per_epoch(weight_snapshots[i], i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_network_growth_animation(all_coords, all_edges, all_primes, i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_degree_hist(degrees, i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_shell_population(shell_nodes, i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_motif_histogram(motif_counts, i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_adjacency_heatmap(edges, primes, i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_spectral_embedding(edges, all_coords[-1], primes, i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_betweenness(edges, primes, all_coords[-1], i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_flow_path(edges, all_coords[-1], primes, i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_spectrum_classification(wavelengths, prototypes, i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_confusion_matrix(conf_mat, acc, i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.save_pairwise_distances(coords=all_coords[-1], primes=primes, net_idx=i, fig_dir='test_color_classification_data/soi_net_test_figures')
        spa.plot_connected_components(edges, primes, i, fig_dir='test_color_classification_data/soi_net_test_figures') 
        spa.plot_clustering_coefficients(edges, primes, i, fig_dir='test_color_classification_data/soi_net_test_figures')
        this_dur = time.time() - net_start
        elapsed  = time.time() - start_time
        avg      = elapsed / (i+1)
        remain   = avg * (total - i - 1)
        print(f"[Network {i+1}/{total}] done in {this_dur:.1f}s — ETA {remain:.1f}s", flush=True)

    # Meta‐network of SOI-neurons
    meta_nodes = [
        {'x': prototypes[j], 'y': 0, 'color': c}
        for j,c in enumerate(['red','green','blue'])
    ]
    meta_edges = {(0,1):1, (0,2):1, (1,2):1}
    spa.plot_meta_network(meta_nodes, meta_edges, fig_dir='test_color_classification_data/soi_net_test_figures')

    total_time = time.time() - start_time
    print(f"\n🏁 All analytics & figures generated in {total_time:.1f}s", flush=True)

if __name__ == "__main__":
    main()

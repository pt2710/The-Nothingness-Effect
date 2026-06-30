# test_soi_net_sound_classification.py

import os
import time
import numpy as np
import pandas as pd

from soi_net import SOInet
import soi_pgnn_analytics as spa
import analytic_sound_utils as asu

from sklearn.metrics import (
    confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, balanced_accuracy_score
)

# --- Ensure output directories exist ---
os.makedirs('test_sound_classification_data/soi_net_test_figures', exist_ok=True)
os.makedirs('test_sound_classification_data/soi_net_test_data', exist_ok=True)
os.makedirs('test_sound_classification_data/audio_comparisons', exist_ok=True)
os.makedirs('test_sound_classification_data/sound_wave_comparisons', exist_ok=True)

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
    np.savez("test_sound_classification_data/soi_net_test_data/elastic_pi_results.npz",
             x=elastic_pi["x"], S=elastic_pi["S"], piE=elastic_pi["piE"], lap=elastic_pi["lap"])
    pd.DataFrame({"x": elastic_pi["x"], "S": elastic_pi["S"],
                  "piE": elastic_pi["piE"], "lap": elastic_pi["lap"]}) \
        .to_csv("test_sound_classification_data/soi_net_test_data/elastic_pi_results.csv", index=False)
    print("✅ Elastic Pi analytics saved.", flush=True)

    # ----- Save DFI analytics -----
    for feat, featdict in dfi_results.items():
        df = pd.DataFrame(featdict)
        df.to_csv(f"test_sound_classification_data/soi_net_test_data/dfi_{feat}.csv", index=False)
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
    hist_df.to_csv('test_sound_classification_data/soi_net_test_data/weight_evolution.csv', index=False)
    for net_idx in hist_df['network'].unique():
        hist_df[hist_df.network==net_idx].to_csv(
            f"test_sound_classification_data/soi_net_test_data/weight_evolution_net{net_idx}.csv", index=False)
    print("✅ Weight evolution data saved.", flush=True)

    # ----- Weight stats -----
    stats = hist_df.groupby(['network','epoch'])['weight'].agg(['mean','std']).reset_index()
    stats.to_csv('test_sound_classification_data/soi_net_test_data/weight_stats.csv', index=False)
    for net_idx in stats['network'].unique():
        stats[stats.network==net_idx].to_csv(
            f"test_sound_classification_data/soi_net_test_data/weight_stats_net{net_idx}.csv", index=False)
    print("✅ Weight stats saved.", flush=True)

    # ----- Sound frequency classification -----
    prototypes = np.array([250, 1000, 4000])  # Low, Mid, High Hz
    np.random.seed(42)
    freqs = np.clip(
        np.linspace(100, 6000, 300) + np.random.normal(0, 50, 300),
        100, 6000
    )
    true = np.zeros_like(freqs, dtype=int)
    true[freqs < 500] = 0    # Low
    mask = (freqs >= 500) & (freqs < 2000)
    true[mask] = 1           # Mid
    true[freqs >= 2000] = 2  # High
    pred = np.argmin(np.abs(freqs[:,None]-prototypes[None,:]), axis=1)

    # ----- Metric Calculation -----
    acc = accuracy_score(true, pred)
    conf_mat = confusion_matrix(true, pred)
    precision = precision_score(true, pred, average=None)
    recall    = recall_score(true, pred, average=None)
    f1        = f1_score(true, pred, average=None)
    balanced_acc = balanced_accuracy_score(true, pred)
    macro_precision = precision_score(true, pred, average='macro')
    macro_recall    = recall_score(true, pred, average='macro')
    macro_f1        = f1_score(true, pred, average='macro')

    # Save individual class metrics
    metrics_df = pd.DataFrame({
        'class': ['Low', 'Mid', 'High'],
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    })
    macro_df = pd.DataFrame({
        'metric': ['accuracy', 'balanced_accuracy', 'macro_precision', 'macro_recall', 'macro_f1'],
        'value':  [acc, balanced_acc, macro_precision, macro_recall, macro_f1]
    })
    metrics_df.to_csv('test_sound_classification_data/soi_net_test_data/class_metrics.csv', index=False)
    macro_df.to_csv('test_sound_classification_data/soi_net_test_data/macro_metrics.csv', index=False)
    pd.DataFrame({'accuracy':[acc]}).to_csv('test_sound_classification_data/soi_net_test_data/accuracy.csv', index=False)
    pd.DataFrame(conf_mat, index=['true0','true1','true2'], columns=['pred0','pred1','pred2']) \
        .to_csv('test_sound_classification_data/soi_net_test_data/confusion_matrix.csv')

    print(f"✅ Sound classification benchmark saved (accuracy: {acc:.3f}).", flush=True)
    print(f"✅ Metrics saved.\n  Balanced acc: {balanced_acc:.3f}\n  Macro-F1: {macro_f1:.3f}", flush=True)

    # ----- SAVE AUDIO COMPARISONS -----
    for i, (input_freq, predicted_class) in enumerate(zip(freqs, pred)):
        out_path = f"test_sound_classification_data/audio_comparisons/test_{i:03d}_input_{int(input_freq)}Hz_class_{predicted_class}_{prototypes[predicted_class]}Hz.wav"
        asu.save_comparison_wav(input_freq, prototypes[predicted_class], out_path)
    print("✅ Audio comparison files saved.", flush=True)

    # ----- SAVE WAVEFORM VISUALIZATIONS -----
    asu.plot_sound_wave_comparisons(
        freqs, prototypes, true, pred,
        out_dir="test_sound_classification_data/sound_wave_comparisons"
    )
    print("✅ Sound waveform comparison plots saved.", flush=True)

    # ----- Degree distribution -----
    deg_records = []
    for net_idx, (primes, edges, *_ ) in enumerate(histories):
        for p in primes:
            deg_records.append({'network': net_idx, 'node': p, 'degree': len(edges[p])})
    deg_df = pd.DataFrame(deg_records)
    deg_df.to_csv('test_sound_classification_data/soi_net_test_data/degree_distribution.csv', index=False)
    for net_idx in deg_df['network'].unique():
        deg_df[deg_df.network==net_idx].to_csv(
            f"test_sound_classification_data/soi_net_test_data/degree_distribution_net{net_idx}.csv", index=False)
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
            fig_dir='test_sound_classification_data/soi_net_test_figures'
        )
        spa.plot_weight_histograms(hist_df[hist_df.network==i], i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_entropy_per_epoch(weight_snapshots[i], i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_network_growth_animation(all_coords, all_edges, all_primes, i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_degree_hist(degrees, i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_shell_population(shell_nodes, i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_motif_histogram(motif_counts, i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_adjacency_heatmap(edges, primes, i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_spectral_embedding(edges, all_coords[-1], primes, i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_betweenness(edges, primes, all_coords[-1], i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_flow_path(edges, all_coords[-1], primes, i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_spectrum_classification(freqs, prototypes, i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_confusion_matrix(conf_mat, acc, i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.save_pairwise_distances(coords=all_coords[-1], primes=primes, net_idx=i, fig_dir='test_sound_classification_data/soi_net_test_figures')
        spa.plot_connected_components(edges, primes, i, fig_dir='test_sound_classification_data/soi_net_test_figures') 
        spa.plot_clustering_coefficients(edges, primes, i, fig_dir='test_sound_classification_data/soi_net_test_figures')

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
    spa.plot_meta_network(meta_nodes, meta_edges, fig_dir='test_sound_classification_data/soi_net_test_figures')

    total_time = time.time() - start_time
    print(f"\n🏁 All analytics & figures generated in {total_time:.1f}s", flush=True)

if __name__ == "__main__":
    main()

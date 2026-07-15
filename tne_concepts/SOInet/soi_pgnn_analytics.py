import os
import math
import random
from collections import defaultdict, deque, Counter
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances
from scipy.linalg import eigh

try:
    import networkx as nx
    from networkx import Graph, connected_components, betweenness_centrality, clustering
except ImportError:
    Graph = None
    connected_components = None
    betweenness_centrality = None
    clustering = None

# Legacy analytics defaults now point at the canonical producer-local layout.
# Importing this compatibility module must not create repository-root folders.
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIG_DIR = str(_REPOSITORY_ROOT / "equations" / "artificial_intelligence" / "color_classification" / "simulation")
DEFAULT_DATA_DIR = str(_REPOSITORY_ROOT / "equations" / "artificial_intelligence" / "color_classification" / "test")

# --- Alignment helper for all plotting routines ---
def _align_coords_primes(coords, primes):
    """Ensure all primes are in coords. Warn and drop if needed."""
    missing = [p for p in primes if p not in coords]
    if missing:
        print(f"[WARN] {len(missing)} primes missing from coords (e.g., {missing[:5]} ...)")
    return [p for p in primes if p in coords]

def flowpoint(f, steps=1):
    return f if (steps % 2 == 0) else -f

def dfi_update(weights, step=1, alpha=0.25):
    updated = {}
    for k, v in weights.items():
        sign_flip = flowpoint(np.sign(v), steps=step)
        mutated = (1-alpha)*v + alpha*sign_flip
        updated[k] = mutated
    return updated

def motif_histogram(primes):
    def canonical_motif(g):
        if g == 1: return (0, 0)
        k = 0
        while g % 2 == 0: g //= 2; k += 1
        ell = (g - 1) // 2
        return k, ell
    motifs = [canonical_motif(primes[i] - primes[i-1]) for i in range(1, len(primes))]
    return Counter(motifs)

def plot_spherical_3d(primes, coords, degrees=None, motifs=None, edge_weights=None, net_idx=0, epoch=None, fig_dir=DEFAULT_FIG_DIR):
    primes = _align_coords_primes(coords, primes)
    if not primes: return
    fig = plt.figure(figsize=(6, 5))
    ax = fig.add_subplot(111, projection='3d')
    xs, ys, zs = zip(*[coords[p] for p in primes])
    if degrees is not None:
        node_sizes = [20 + 3 * degrees[p] for p in primes]
    else:
        node_sizes = 15
    colorval = None
    if motifs is not None:
        colorval = [motifs.get(p, 0) for p in primes]
    else:
        colorval = [coords[p][0]**2 + coords[p][1]**2 + coords[p][2]**2 for p in primes]
    sc = ax.scatter(xs, ys, zs, c=colorval, cmap='viridis', s=node_sizes)
    plt.colorbar(sc, ax=ax, label='Motif/Shell/Depth')
    tit = f"PGNN Net {net_idx} 3D"
    if epoch is not None: tit += f" (Epoch {epoch})"
    ax.set_title(tit)
    ax.set_axis_off()
    plt.savefig(f"{fig_dir}/pgnn3d_net{net_idx}_epoch{epoch or 0}.png")
    plt.close(fig)

def plot_network_growth_animation(all_coords, all_edges, all_primes, net_idx, fig_dir=DEFAULT_FIG_DIR):
    frames = len(all_primes)
    fig = plt.figure(figsize=(6,5))
    ax = fig.add_subplot(111, projection='3d')
    def animate(i):
        these_primes = _align_coords_primes(all_coords[i], all_primes[i])
        if not these_primes: return
        ax.cla()
        xs, ys, zs = zip(*[all_coords[i][p] for p in these_primes])
        ax.scatter(xs, ys, zs, c='c', s=15)
        for u in all_edges[i]:
            for v in all_edges[i][u]:
                if u < v and u in all_coords[i] and v in all_coords[i]:
                    x_vals = [all_coords[i][u][0], all_coords[i][v][0]]
                    y_vals = [all_coords[i][u][1], all_coords[i][v][1]]
                    z_vals = [all_coords[i][u][2], all_coords[i][v][2]]
                    ax.plot(x_vals, y_vals, z_vals, color='k', alpha=0.15)
        ax.set_axis_off()
        ax.set_title(f"Growth Epoch {i+1}")

    anim = animation.FuncAnimation(fig, animate, frames=frames, interval=80)
    anim.save(f"{fig_dir}/pgnn_growth_net{net_idx}.gif", writer='pillow')
    plt.close(fig)

def plot_weight_histograms(hist_df, net_idx, fig_dir=DEFAULT_FIG_DIR):
    fig, ax = plt.subplots(figsize=(8,4))
    epochs = sorted(hist_df['epoch'].unique())
    bins = np.linspace(hist_df['weight'].min(), hist_df['weight'].max(), 32)
    def animate(i):
        ax.cla()
        ws = hist_df[hist_df['epoch'] == epochs[i]]['weight']
        ax.hist(ws, bins=bins, color='b', alpha=0.6)
        ax.set_title(f"Edge Weight Distribution - Network {net_idx} - Epoch {epochs[i]}")
        ax.set_xlabel('Weight')
        ax.set_ylabel('Count')
    anim = animation.FuncAnimation(fig, animate, frames=len(epochs), interval=200)
    anim.save(f'{fig_dir}/weight_hist_ani_net{net_idx}.gif', writer='pillow')
    plt.close(fig)

def plot_entropy_per_epoch(weight_snapshots, net_idx, fig_dir=DEFAULT_FIG_DIR):
    H = []
    for ws in weight_snapshots:
        p, _ = np.histogram(ws, bins=32, density=True)
        p = p[p>0]
        H.append(-np.sum(p * np.log2(p)))
    plt.figure(figsize=(7,4))
    plt.plot(H, '-o', label='H(weights)')
    plt.plot(np.diff(H,prepend=H[0]), '--', label='ΔS')
    plt.xlabel('Epoch'); plt.ylabel('Entropy')
    plt.legend(); plt.title(f'Entropy evolution, Net {net_idx}')
    plt.savefig(f'{fig_dir}/entropy_epoch_net{net_idx}.png')
    plt.close()

def plot_degree_hist(degrees, net_idx, fig_dir=DEFAULT_FIG_DIR):
    plt.figure(figsize=(5,4))
    plt.hist(list(degrees.values()), bins=range(min(degrees.values()),max(degrees.values())+2), edgecolor='black')
    plt.title(f"Degree Dist Net {net_idx}")
    plt.xlabel("Degree"); plt.ylabel("Count")
    plt.savefig(f"{fig_dir}/degree_dist_net{net_idx}.png")
    plt.close()

def plot_shell_population(shell_nodes, net_idx, fig_dir=DEFAULT_FIG_DIR):
    pop = [len(shell_nodes[k]) for k in sorted(shell_nodes)]
    plt.figure(figsize=(5,3))
    plt.bar(list(sorted(shell_nodes)), pop)
    plt.title(f"Shell/Layer Population Net {net_idx}")
    plt.xlabel("Shell (k)"); plt.ylabel("Nodes")
    plt.savefig(f"{fig_dir}/shell_population_net{net_idx}.png")
    plt.close()

def plot_motif_histogram(motif_counts, net_idx, fig_dir=DEFAULT_FIG_DIR):
    items = sorted(motif_counts.items(), key=lambda x: x[1], reverse=True)
    labels = [str(x[0]) for x in items]
    values = [x[1] for x in items]
    plt.figure(figsize=(10,3))
    plt.bar(labels, values)
    plt.title(f"Motif Histogram Net {net_idx}")
    plt.xlabel("(k, l) Motif"); plt.ylabel("Count")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(f"{fig_dir}/motif_hist_net{net_idx}.png")
    plt.close()

def plot_adjacency_heatmap(edges, primes, net_idx, fig_dir=DEFAULT_FIG_DIR):
    primes = list(primes)
    N = len(primes)
    idx = {p: i for i, p in enumerate(primes)}
    A = np.zeros((N, N))
    for u in edges:
        for v in edges[u]:
            if u in idx and v in idx:
                i, j = idx[u], idx[v]
                A[i, j] = 1
    plt.figure(figsize=(7,7))
    plt.imshow(A, cmap='hot', interpolation='nearest')
    plt.title(f"Adjacency Heatmap Net {net_idx}")
    plt.savefig(f"{fig_dir}/adj_heatmap_net{net_idx}.png")
    plt.close()

def plot_spectral_embedding(edges, coords, primes, net_idx, fig_dir=DEFAULT_FIG_DIR):
    primes = _align_coords_primes(coords, primes)
    N = len(primes)
    idx = {p: i for i, p in enumerate(primes)}
    A = np.zeros((N, N))
    for u in edges:
        for v in edges[u]:
            if u in idx and v in idx:
                i, j = idx[u], idx[v]
                A[i, j] = 1
    D = np.diag(A.sum(axis=1))
    L = D - A
    eigvals, eigvecs = eigh(L)
    X = eigvecs[:, 1:3]  # Use 2nd/3rd smallest eigenvectors
    plt.figure(figsize=(7,6))
    plt.scatter(X[:,0], X[:,1], c='b', s=10)
    plt.title(f"Spectral Embedding Net {net_idx}")
    plt.savefig(f"{fig_dir}/spectral_embed_net{net_idx}.png")
    plt.close()

def plot_betweenness(edges, primes, coords, net_idx, fig_dir=DEFAULT_FIG_DIR):
    if Graph is None or betweenness_centrality is None:
        print("[WARN] networkx not installed for betweenness.")
        return
    primes = _align_coords_primes(coords, primes)
    G = Graph()
    for u in edges:
        for v in edges[u]:
            if u < v: G.add_edge(u, v)
    b = betweenness_centrality(G)
    plt.figure(figsize=(6,5))
    vals = [b.get(p, 0) for p in primes]
    xs, ys, zs = zip(*[coords[p] for p in primes])
    plt.scatter(xs, ys, c=vals, s=40, cmap='plasma')
    plt.title(f"Betweenness Net {net_idx}")
    plt.savefig(f"{fig_dir}/betweenness_net{net_idx}.png")
    plt.close()

def plot_confusion_matrix(conf_mat, acc, net_idx, fig_dir=DEFAULT_FIG_DIR):
    plt.figure(figsize=(4,4))
    plt.imshow(conf_mat, cmap='Blues')
    plt.title(f"Confusion Matrix Net {net_idx}, acc={acc:.2%}")
    plt.xlabel('Predicted'); plt.ylabel('True')
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(f"{fig_dir}/confusion_matrix_net{net_idx}.png")
    plt.close()

def plot_accuracy_vs_epoch(accs, net_idx, fig_dir=DEFAULT_FIG_DIR):
    plt.figure(figsize=(6,3))
    plt.plot(accs, '-o')
    plt.title(f"Accuracy vs Epoch Net {net_idx}")
    plt.xlabel("Epoch"); plt.ylabel("Accuracy")
    plt.savefig(f"{fig_dir}/accuracy_epoch_net{net_idx}.png")
    plt.close()

def plot_meta_network(meta_nodes, meta_edges, meta_weights=None, fig_dir=DEFAULT_FIG_DIR):
    plt.figure(figsize=(7,3))
    xs = [n['x'] for n in meta_nodes]
    ys = [n['y'] for n in meta_nodes]
    plt.scatter(xs, ys, c=[n['color'] for n in meta_nodes], s=250)
    for (i,j), w in meta_edges.items():
        plt.plot([xs[i], xs[j]], [ys[i], ys[j]], color='k', alpha=0.6, lw=(1 if meta_weights is None else meta_weights[(i,j)]*3))
    plt.title("Meta-Network of SOI Neurons")
    plt.axis('off')
    plt.savefig(f"{fig_dir}/meta_network.png")
    plt.close()

def plot_flow_path(edges, coords, primes, net_idx, fig_dir=DEFAULT_FIG_DIR):
    import random
    from collections import deque
    import matplotlib.pyplot as plt
    primes = _align_coords_primes(coords, primes)
    if not primes: return
    src = random.choice(primes)
    dst = random.choice(primes)
    visited = {src}
    queue = deque([[src]])
    path = []
    while queue:
        pth = queue.popleft()
        node = pth[-1]
        if node == dst:
            path = pth
            break
        for nbr in edges[node]:
            if nbr not in visited:
                visited.add(nbr)
                queue.append(pth + [nbr])

    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111, projection='3d')
    for u in edges:
        for v in edges[u]:
            if u < v and u in coords and v in coords:
                xs, ys, zs = zip(coords[u], coords[v])
                ax.plot(xs, ys, zs, color='gray', alpha=0.1, linewidth=0.5)
    for i in range(len(path)-1):
        u, v = path[i], path[i+1]
        if u in coords and v in coords:
            xs, ys, zs = zip(coords[u], coords[v])
            ax.plot(xs, ys, zs, color='yellow', alpha=0.9, linewidth=2)
    if src in coords: ax.scatter(*coords[src], color='lime',  s=50, label='Input')
    if dst in coords: ax.scatter(*coords[dst], color='magenta', s=50, label='Output')
    ax.set_title(f'PGNN {net_idx} Path {src}→{dst}')
    ax.legend(loc='upper left')
    ax.set_axis_off()
    fig.savefig(f"{fig_dir}/flow_path_net{net_idx}.png")
    plt.close(fig)

def plot_spectrum_classification(wavelengths, prototypes, net_idx, fig_dir=DEFAULT_FIG_DIR):
    def wavelength_to_rgb(wl):
        gamma = 0.8
        if wl < 380 or wl > 780: return (0,0,0)
        if wl < 440:
            R,G,B = -(wl-440)/(440-380), 0, 1
        elif wl < 490:
            R,G,B = 0, (wl-440)/(490-440), 1
        elif wl < 510:
            R,G,B = 0, 1, -(wl-510)/(510-490)
        elif wl < 580:
            R,G,B = (wl-510)/(580-510), 1, 0
        elif wl < 645:
            R,G,B = 1, -(wl-645)/(645-580), 0
        else:
            R,G,B = 1, 0, 0
        factor = 1.0
        if wl < 420:
            factor = 0.3 + 0.7*(wl-380)/(420-380)
        elif wl > 700:
            factor = 0.3 + 0.7*(780-wl)/(780-700)
        return (R*factor)**gamma, (G*factor)**gamma, (B*factor)**gamma

    pred = np.argmin(np.abs(wavelengths[:,None] - prototypes[None,:]), axis=1)
    fig, ax = plt.subplots(figsize=(8,3))
    y_jitter = np.random.uniform(-0.1, 0.1, len(wavelengths))
    colors   = [wavelength_to_rgb(wl) for wl in wavelengths]
    ax.scatter(wavelengths, y_jitter, c=colors, s=30, edgecolor='k', lw=0.2)
    for i, wl in enumerate(prototypes):
        ax.axvline(wl, color='k', ls='--')
        ax.text(wl, 0.15, f'Neuron {i}', ha='center')
    ax.set_title(f"Spectrum Classification (Net {net_idx})")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_yticks([])
    plt.tight_layout()
    plt.savefig(f"{fig_dir}/spectrum_classification_net{net_idx}.png")
    plt.close(fig)

def plot_sound_wave_comparisons(
    freqs, prototypes, true, pred, sample_rate=16000, duration=0.3, out_dir=None
):
    if out_dir is None:
        out_dir = _REPOSITORY_ROOT / "equations" / "artificial_intelligence" / "sound_classification" / "simulation"
    os.makedirs(out_dir, exist_ok=True)
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    for i, (f_true, f_pred, lab_true, lab_pred) in enumerate(zip(freqs, prototypes[pred], true, pred)):
        y_true = np.sin(2 * np.pi * f_true * t)
        y_pred = np.sin(2 * np.pi * f_pred * t)
        plt.figure(figsize=(7,3))
        plt.plot(t, y_true, label=f"True freq: {int(f_true)} Hz", color='royalblue', alpha=0.7)
        plt.plot(t, y_pred, label=f"Pred freq: {int(f_pred)} Hz", color='firebrick', alpha=0.6, linestyle='--')
        plt.title(f"Sample {i}: True Label {lab_true}, Pred Label {lab_pred}")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.tight_layout()
        fname = f"sample_{i}_true{lab_true}_pred{lab_pred}.png"
        plt.savefig(os.path.join(out_dir, fname))
        plt.close()

def save_pairwise_distances(coords, primes, net_idx, fig_dir=DEFAULT_FIG_DIR):
    """
    Save the pairwise Euclidean distance matrix for node coordinates.
    """
    primes = _align_coords_primes(coords, primes)
    if not primes: return
    X = np.array([coords[p] for p in primes])
    distmat = pairwise_distances(X)
    pd.DataFrame(distmat, index=primes, columns=primes).to_csv(
        os.path.join(fig_dir, f"pairwise_distances_net{net_idx}.csv")
    )
    # Optionally, plot as a heatmap
    plt.figure(figsize=(6,5))
    plt.imshow(distmat, cmap='viridis')
    plt.colorbar(label="Euclidean distance")
    plt.title(f"Pairwise Distances Net {net_idx}")
    plt.savefig(os.path.join(fig_dir, f"pairwise_distances_net{net_idx}.png"))
    plt.close()

def plot_connected_components(edges, primes, net_idx, fig_dir=DEFAULT_FIG_DIR):
    """
    Use networkx.connected_components to label and visualize connected components.
    """
    if Graph is None or connected_components is None:
        print("[WARN] networkx not installed for connected components.")
        return
    G = Graph()
    for u in edges:
        for v in edges[u]:
            G.add_edge(u, v)
    comps = list(connected_components(G))
    labelmap = {}
    for idx, comp in enumerate(comps):
        for p in comp:
            labelmap[p] = idx
    primes = [p for p in primes if p in labelmap]
    labels = [labelmap[p] for p in primes]
    plt.figure(figsize=(6,4))
    plt.scatter(primes, labels, c=labels, cmap='tab10', s=25)
    plt.title(f"Connected Components Net {net_idx}")
    plt.xlabel("Prime Index")
    plt.ylabel("Component Label")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, f"connected_components_net{net_idx}.png"))
    plt.close()

def plot_clustering_coefficients(edges, primes, net_idx, fig_dir=DEFAULT_FIG_DIR):
    """
    Use networkx.clustering to compute and plot clustering coefficient for each node.
    """
    if Graph is None or clustering is None:
        print("[WARN] networkx not installed for clustering coefficient.")
        return
    G = Graph()
    for u in edges:
        for v in edges[u]:
            G.add_edge(u, v)
    cdict = clustering(G)
    primes = [p for p in primes if p in cdict]
    coeffs = [cdict[p] for p in primes]
    plt.figure(figsize=(7,3))
    plt.plot(primes, coeffs, '.-')
    plt.title(f"Clustering Coefficient Net {net_idx}")
    plt.xlabel("Prime")
    plt.ylabel("Clustering Coefficient")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, f"clustering_coeff_net{net_idx}.png"))
    plt.close()

# test_soi_net_sound_cloning.py

import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import soundfile as sf

from soi_net import SOInet
import soi_pgnn_analytics as spa
import analytic_sound_utils as asu

# --- Output directories ---
OUT_DIR   = 'test_sound_cloning_data'
WAV_DIR   = os.path.join(OUT_DIR, 'wav')
FIG_DIR   = os.path.join(OUT_DIR, 'figures')
PGNN_FIG  = os.path.join(FIG_DIR, 'pgnn_networks')
WAVE_CMP  = os.path.join(FIG_DIR, 'wave_comparisons')
os.makedirs(WAV_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(PGNN_FIG, exist_ok=True)
os.makedirs(WAVE_CMP, exist_ok=True)

def save_wav(arr, path, samplerate=16000):
    arr = np.asarray(arr)
    sf.write(path, arr, samplerate)

def plot_waveforms(original, cloned, path, samplerate=16000, title=None):
    t = np.arange(len(original)) / samplerate
    plt.figure(figsize=(10, 3))
    plt.plot(t, original, label='Original')
    plt.plot(t, cloned, label='Cloned/Mirrored', alpha=0.7)
    plt.legend()
    plt.title(title or 'Original vs. Cloned Audio Waveform')
    plt.xlabel('Time [s]')
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def plot_spectra(original, cloned, path, samplerate=16000, title=None):
    f = np.fft.rfftfreq(len(original), 1/samplerate)
    plt.figure(figsize=(8, 4))
    plt.plot(f, np.abs(np.fft.rfft(original)), label="Original Spectrum")
    plt.plot(f, np.abs(np.fft.rfft(cloned)), label="Cloned Spectrum", alpha=0.7)
    plt.title(title or "Spectrum: Original vs. Cloned Audio")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Magnitude")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def main():
    start_time = time.time()
    print("🚀 [SOI Net] Initializing for SOUND CLONING (bidirectional/generative mode)...", flush=True)

    soi_params = {'normalize_to': 1.0, 'adv_mode': True, 'type': 'symmetric'}
    net = SOInet(soi_params=soi_params)

    # --- MULTI-SOUND CLONING TEST SET ---
    samplerate = 16000
    duration   = 1.2
    test_sounds = [
        {'label': 'A4_sine_440Hz', 'data': 0.6 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(samplerate * duration), endpoint=False))},
        {'label': 'C5_sine_523Hz', 'data': 0.6 * np.sin(2 * np.pi * 523.25 * np.linspace(0, duration, int(samplerate * duration), endpoint=False))},
        {'label': 'sawtooth_220Hz', 'data': 0.4 * (2 * (np.linspace(0, 1, int(samplerate * duration), endpoint=False) * 220 % 1) - 1)},
        {'label': 'triangle_330Hz', 'data': 0.4 * (2 * np.abs(2 * ((np.linspace(0, 1, int(samplerate * duration), endpoint=False) * 330) % 1) - 1) - 1)},
        # Optionally add real audio:
        # {'label': 'voice_sample', 'data': sf.read('your_voice.wav')[0][:int(samplerate*duration)]}
    ]

    results = []
    for i, s in enumerate(test_sounds):
        print(f"\n🔊 [{i}] Cloning: {s['label']}...")
        audio = s['data']
        n_samples = len(audio)

        # --- Save input .wav
        inpath = os.path.join(WAV_DIR, f"{s['label']}_input.wav")
        save_wav(audio, inpath, samplerate=samplerate)

        # ==== ENCODE ====
        latent = net.encode_audio(audio)
        mirrored_latent = -latent  # Simple spectral mirroring (DFI/PGNN mirror optional)

        # ==== DECODE ====
        cloned_audio = net.decode_audio(mirrored_latent, n_samples=n_samples)
        outpath = os.path.join(WAV_DIR, f"{s['label']}_cloned.wav")
        save_wav(cloned_audio, outpath, samplerate=samplerate)

        # --- Waveform/Spectrum plots
        plot_waveforms(audio, cloned_audio, os.path.join(FIG_DIR, f"{s['label']}_waveform.png"), samplerate, title=f"{s['label']}: Waveform")
        plot_spectra(audio, cloned_audio, os.path.join(FIG_DIR, f"{s['label']}_spectrum.png"), samplerate, title=f"{s['label']}: Spectrum")

        # --- "side-by-side" input/cloned waveform using analytic_sound_utils (OPTIONAL)
        # For this context, we show just the original and cloned (if you want freq predictions, plug in below)
        asu.plot_sound_wave_comparisons(
            [440], [440], [0], [0],  # dummy for sine, adapt for real test sets with classification
            sample_rate=samplerate, duration=duration, out_dir=WAVE_CMP
        )

        # --- Metrics
        mse = np.mean((audio - cloned_audio[:n_samples])**2)
        snr = 10 * np.log10(np.sum(audio**2) / (np.sum((audio - cloned_audio[:n_samples])**2) + 1e-12))
        print(f"  [MSE: {mse:.6f} | SNR: {snr:.2f} dB]")

        results.append({'label': s['label'], 'mse': mse, 'snr': snr})

    # ---- Save metrics table
    pd.DataFrame(results).to_csv(os.path.join(OUT_DIR, "cloning_metrics.csv"), index=False)
    print("\n✅ All cloning complete! Metrics saved.")

    # ==== PGNN/SOI/DFI ANALYTICS ====
    print("\n📊 Generating SOI/PGNN analytics and visualizations...")
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

    # ---- Visualization Suite ----
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

        # ---- Use PGNN analytics plotting suite ----
        spa.plot_spherical_3d(primes, all_coords[-1], degrees, None, weight_map, i, None, fig_dir=PGNN_FIG)
        spa.plot_weight_histograms(hist_df[hist_df.network==i], i, fig_dir=PGNN_FIG)
        spa.plot_entropy_per_epoch(weight_snapshots[i], i, fig_dir=PGNN_FIG)
        spa.plot_network_growth_animation(all_coords, all_edges, all_primes, i, fig_dir=PGNN_FIG)
        spa.plot_degree_hist(degrees, i, fig_dir=PGNN_FIG)
        spa.plot_shell_population(shell_nodes, i, fig_dir=PGNN_FIG)
        spa.plot_motif_histogram(motif_counts, i, fig_dir=PGNN_FIG)
        spa.plot_adjacency_heatmap(edges, primes, i, fig_dir=PGNN_FIG)
        spa.plot_spectral_embedding(edges, all_coords[-1], primes, i, fig_dir=PGNN_FIG)
        spa.plot_betweenness(edges, primes, all_coords[-1], i, fig_dir=PGNN_FIG)
        spa.plot_flow_path(edges, all_coords[-1], primes, i, fig_dir=PGNN_FIG)

        this_dur = time.time() - net_start
        print(f"[Net {i+1}/{total}] analytics in {this_dur:.1f}s", flush=True)

    total_time = time.time() - start_time
    print(f"\n🏁 All sound cloning, analytics & figures complete in {total_time:.1f}s", flush=True)
    print(f"Results and figures in: {OUT_DIR}/")

if __name__ == "__main__":
    main()

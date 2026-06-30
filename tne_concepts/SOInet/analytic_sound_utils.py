# analytic_sound_utils.py

import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
import os

def generate_tone(freq, duration=0.7, sr=22050, amplitude=0.3):
    """Generate a pure sine tone of given frequency (Hz) and duration (s)."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * freq * t)
    return wave, sr

def save_comparison_wav(freq_actual, freq_classified, out_path, duration=0.7, pause=0.15):
    """Save .wav with: [actual sound][pause][classified sound]"""
    sr = 22050
    tone1, _ = generate_tone(freq_actual, duration, sr)
    tone2, _ = generate_tone(freq_classified, duration, sr)
    silence = np.zeros(int(sr * pause))
    combined = np.concatenate([tone1, silence, tone2])
    # Scale to int16 for wav
    combined = (combined * 32767).astype(np.int16)
    wav.write(out_path, sr, combined)

def plot_sound_wave_comparisons(freqs, prototypes, true, pred, out_dir):
    """
    Plots comparison of actual (input) vs classified (output) sound waves.
    Each file: test_{idx}_input_{freq}Hz_class_{class}_{class_freq}Hz.png
    """
    sr = 22050
    dur = 0.7
    n = len(freqs)
    os.makedirs(out_dir, exist_ok=True)

    for i in range(n):
        f_input = freqs[i]
        f_class = prototypes[pred[i]]
        wave_input, _ = generate_tone(f_input, dur, sr)
        wave_class, _ = generate_tone(f_class, dur, sr)
        t = np.linspace(0, dur, len(wave_input))
        plt.figure(figsize=(8, 3))
        plt.plot(t, wave_input, label=f'Actual {int(f_input)}Hz', color='C0')
        plt.plot(t, wave_class, label=f'Classified {int(f_class)}Hz', color='C1', alpha=0.7)
        plt.title(f"Input vs Classified Sound Wave (#{i})\nTrue class: {true[i]}, Pred: {pred[i]}")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.tight_layout()
        fname = f"test_{i:03d}_input_{int(f_input)}Hz_class_{pred[i]}_{int(f_class)}Hz.png"
        plt.savefig(os.path.join(out_dir, fname))
        plt.close()



# Optionally: a batch function to save all
def batch_save_comparisons(test_freqs, pred_freqs, outdir):
    os.makedirs(outdir, exist_ok=True)
    for i, (f_test, f_pred) in enumerate(zip(test_freqs, pred_freqs)):
        fname = f"{outdir}/comparison_{i:03d}_test{int(f_test)}_pred{int(f_pred)}.wav"
        save_comparison_wav(f_test, f_pred, fname)

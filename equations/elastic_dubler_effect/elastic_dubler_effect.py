import sys, os
import numpy as np
import matplotlib.pyplot as plt

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from equations.dynamic_fluctuation_index.dfi import DynamicFluctuationIndex
from equations.elastic_pi.elastic_pi import ElasticPi

PLANCK_H = 6.62607015e-34
BOLTZMANN_K = 1.380649e-23
SOUND_KD = 0.1

regimes = [
    r"Light: Planck ($\mathcal{K}_D=h$)",
    r"Thermodynamics: Boltzmann ($\mathcal{K}_D=k_B$)",
    r"Sound: Acoustic Doppler ($\mathcal{K}_D=0.1$)"
]
K_D_values = [PLANCK_H, BOLTZMANN_K, SOUND_KD]
colors = ['#B22222', '#228B22', '#E66100']

# --------------------------------------
# 1) GENERATE NONLINEAR DATA FOR DFI
# --------------------------------------
np.random.seed(42)
n_samples = 240
t = np.linspace(-2, 2, n_samples)

# Feature A: sigmoid S-curve
featA = 1 / (1 + np.exp(-3 * t))
# Feature B: Gaussian bump
featB = np.exp(- (t**2) / 1.5)

all_X = np.column_stack([featA, featB])

# tiny noise to avoid exact ties
all_X += np.random.normal(scale=1e-3, size=all_X.shape)

# normalize each column into [0,1]
def normalize_zero_one(x):
    lo, hi = x.min(), x.max()
    return (x - lo) / (hi - lo) if hi > lo else np.zeros_like(x)

all_X[:,0] = normalize_zero_one(all_X[:,0])
all_X[:,1] = normalize_zero_one(all_X[:,1])

# ---------------------------
# 2) COMPUTE DFI
# ---------------------------
dfi_engine = DynamicFluctuationIndex()
soi = 100
entropies = dfi_engine.dfi(all_X, soi=soi)

S_A_raw = entropies[0]['Relative_Entropy']
S_B_raw = entropies[1]['Relative_Entropy']

elastic_pi = ElasticPi()

def scale_entropy(S):
    S = S - np.mean(S)
    return S / (np.max(np.abs(S)) + 1e-12) * 5

# ---------------------------
# 3) PLOTTING (unchanged)
# ---------------------------
fig, axes = plt.subplots(2, 3, figsize=(16, 8), gridspec_kw={'height_ratios': [1.1, 1]})
plt.subplots_adjust(hspace=0.28, wspace=0.23)

for i, (K_D, color, label) in enumerate(zip(K_D_values, colors, regimes)):
    S_A = scale_entropy(S_A_raw)
    S_B = scale_entropy(S_B_raw)
    entropy_gradient = S_A - S_B
    idx_sort = np.argsort(entropy_gradient)
    _, pi_A, _ = elastic_pi.compute_piE_and_laplacian(S_A, K_D=K_D)
    _, pi_B, _ = elastic_pi.compute_piE_and_laplacian(S_B, K_D=K_D)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        pi_B_safe = np.where(pi_B == 0, 1e-300, pi_B)
        dubler_shift = pi_A / pi_B_safe
        dubler_shift[~np.isfinite(dubler_shift)] = np.nan

    # Top row: Dubler line plot
    ax1 = axes[0, i]
    ax1.plot(entropy_gradient[idx_sort], dubler_shift[idx_sort], '-', color=color, lw=2)
    ax1.axhline(1.0, color='gray', lw=1, ls='--')
    ax1.set_xlabel(r'Entropy Gradient $S_A - S_B$ (DFI)')
    ax1.set_title(label, fontsize=13)
    ax1.grid(True, alpha=0.25)
    if i == 0:
        ax1.set_ylabel(r'Dubler Shift $\frac{\pi_{\mathcal{E}}(A)}{\pi_{\mathcal{E}}(B)}$')
    ax1.set_xlim(-10, 10)
    finite_yvals = dubler_shift[np.isfinite(dubler_shift)]
    if finite_yvals.size == 0:
        ax1.set_ylim(0, 1)
    else:
        y0, y1 = np.nanmin(finite_yvals), np.nanmax(finite_yvals)
        if y0 == y1: y0, y1 = 0, y1 + 1
        ax1.set_ylim(y0 * 0.95, y1 * 1.05)

    # Bottom row: regime-specific interpretables
    ax2 = axes[1, i]
    if np.all(np.isnan(dubler_shift)):
        ax2.text(0.5, 0.5, "No data", ha='center', va='center')
        continue

    if label.startswith("Light"):
        normed = (dubler_shift - np.nanmin(dubler_shift)) / (np.nanmax(dubler_shift) - np.nanmin(dubler_shift) + 1e-12)
        wavelengths = 400 + normed * (700-400)
        rgb = plt.cm.jet((wavelengths-400)/300)
        for j in range(len(entropy_gradient)-1):
            ax2.axvspan(entropy_gradient[idx_sort][j], entropy_gradient[idx_sort][j+1],
                        color=rgb[idx_sort][j], ec=None)
        ax2.set_xlim(ax1.get_xlim()); ax2.set_ylim(0,1)
        ax2.set_yticks([]); ax2.set_ylabel("Color Map")
        ax2.set_xlabel(r'Entropy Gradient $S_A - S_B$ (DFI)')
        ax2.set_title("Visible Color Shift", fontsize=10)

    elif label.startswith("Sound"):
        n_wave = len(dubler_shift)
        t_wave = np.linspace(0, 2*np.pi, n_wave)
        freq = 200 + 1800 * (1 - np.abs(entropy_gradient) /
                             (np.max(np.abs(entropy_gradient)) + 1e-8))
        wave = np.sin(2 * np.pi * freq * (t_wave / (2*np.pi)))
        amp_env = 0.5 + 0.5 * (dubler_shift - np.nanmin(dubler_shift)) / \
                  (np.nanmax(dubler_shift) - np.nanmin(dubler_shift) + 1e-12)
        ax2.plot(t_wave, wave * amp_env, color=color, lw=1.5)
        ax2.set_xlabel("Time (arbitrary)"); ax2.set_ylabel("Sound Waveform")
        ax2.set_title("Doppler-like Frequency Shift", fontsize=10)
        ax2.set_yticks([]); ax2.set_xticks([])

    elif label.startswith("Thermo"):
        normed = (dubler_shift - np.nanmin(dubler_shift)) / \
                 (np.nanmax(dubler_shift) - np.nanmin(dubler_shift) + 1e-12)
        heat_colors = plt.cm.hot(normed)
        for j in range(len(entropy_gradient)-1):
            ax2.axvspan(entropy_gradient[idx_sort][j], entropy_gradient[idx_sort][j+1],
                        color=heat_colors[idx_sort][j], ec=None)
        ax2.set_xlim(ax1.get_xlim()); ax2.set_ylim(0,1)
        ax2.set_yticks([]); ax2.set_ylabel("Heat Map")
        ax2.set_xlabel(r'Entropy Gradient $S_A - S_B$ (DFI)')
        ax2.set_title("Thermal Shift (Heat Color)", fontsize=10)

fig.suptitle(r"Dubler Shift: DFI + Elastic $\pi$ (Light, Sound, Thermo; unique regime plots below lines)",
             fontsize=14)
fig.tight_layout(rect=[0, 0, 1, 0.95])

os.makedirs("figures", exist_ok=True)
fig.savefig("figures/dubler_shift_three_scenarios_interpretables.pdf")
fig.savefig("figures/dubler_shift_three_scenarios_interpretables.png", dpi=300)
plt.show()

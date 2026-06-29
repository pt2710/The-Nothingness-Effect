"""
Elastic‑π Quasicrystal demo — HD edition (2025‑04 update)
• Higher‑resolution spheres (512² samples)
• Slower, longer animations (24 fps, 2 complete oscillations ≈ 8 s)
• 5‑D cloud now oscillates intrinsically, not just via camera
"""

import os, gc, math
from   time import perf_counter
import numpy as np
import pandas as pd
import pywt
import matplotlib.pyplot    as plt
import matplotlib.animation as anim
from   scipy.fft            import fft2, fftshift
from   scipy.ndimage        import map_coordinates

# ──────────────────── output directory ────────────────────
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ───────────── high‑def & timing configuration ─────────────
DPI          = 240
AXES         = 60
SPHERE_RES   = 512   
SCATTER_PTS  = 32_000
FPS          = 24         
OSC_CYCLES   = 2      
FLOW_PERIOD  = 80
OSC_PERIOD   = int(FPS * 4)  
SCAT_FRAMES  = OSC_PERIOD * OSC_CYCLES 

np.random.seed(1)
plt.rcParams.update({"figure.dpi": DPI,
                     "animation.embed_limit": 200})

# ───────────────────── utilities ─────────────────────
def log_step(step, idx, total, start):
    """Print progress for discrete steps (static plots)."""
    elapsed = perf_counter() - start
    eta     = elapsed/(idx+1)*(total-idx-1)
    print(f"[{step}] {idx+1}/{total}  elapsed: {elapsed:5.1f}s  ETA: {eta:5.1f}s")


def save_animation(anim_obj, fname, label):
    """Animation saver with live progress."""
    start  = perf_counter()
    fig    = anim_obj._fig
    writer = anim.FFMpegWriter(fps=FPS, bitrate=4000)

    total = anim_obj._save_count or anim_obj._iter_gen().__length_hint__()
    print(f"[{label}] frames: {total}")

    with writer.saving(fig, fname, DPI):
        for fno, frame in enumerate(anim_obj.new_frame_seq()):
            anim_obj._draw_next_frame(frame, blit=True)
            writer.grab_frame()
            if fno % max(1, total//20) == 0 or fno + 1 == total:
                elapsed = perf_counter() - start
                eta = elapsed/(fno+1)*(total-fno-1)
                print(f"\r[{label}] {fno+1:4}/{total}  "
                      f"elapsed {elapsed:6.1f}s  ETA {eta:6.1f}s",
                      end="")
    print(f"\n[{label}] DONE in {perf_counter()-start:5.1f}s")


# ───────────────────── flow‑point generator ─────────────────────
try:
    from equations.flowpoint.flowpoint import fp 
except ImportError:
    def fp(period_frames: int = FLOW_PERIOD):
        s = 1.0
        while True:
            for _ in range(period_frames):
                yield s
            s = -s

# Ornstein‑Uhlenbeck camera & helpers ───────────────────────────
class OUcamera:
    def __init__(self, θ=0.03, σ=0.05):
        v = np.random.randn(3)
        self.v = v/np.linalg.norm(v); self.θ, self.σ = θ, σ
    def step(self):
        self.v += -self.θ*self.v + self.σ*np.random.randn(3)
        self.v /= np.linalg.norm(self.v); return self.v

def rot(axis, θ):
    axis = axis/np.linalg.norm(axis); ux,uy,uz = axis
    c,s = math.cos(θ), math.sin(θ)
    return np.array([
        [c+ux*ux*(1-c),   ux*uy*(1-c)-uz*s, ux*uz*(1-c)+uy*s],
        [uy*ux*(1-c)+uz*s,c+uy*uy*(1-c),    uy*uz*(1-c)-ux*s],
        [uz*ux*(1-c)-uy*s,uz*uy*(1-c)+ux*s, c+uz*uz*(1-c)]
    ])

# ───────────────── DFI & elastic‑π helpers ─────────────────
def dfi(df: pd.DataFrame, soi=100.0):
    xn, V0 = df.shape[1], soi/df.shape[1]
    Σ = df.sum(axis=1).values
    out = {}
    for c in df.columns:
        xi = df[c].values
        σ  = (Σ*(xn-1))/((Σ-xi)*xn + 1e-14)
        out[c] = {"V": V0*σ, "S": V0*σ - V0}
    return out

def flowpoint_pi(k=10_000_000):
    pi_approx = 0.0
    for k in range(k):
        numerator   = next(fp((-1) ** k))
        denominator = 2 * k + 1
        pi_approx  += numerator/denominator
        if k > 1_000_000 and abs((4*pi_approx) - math.pi) < 1e-5:
            break
    return 4 * pi_approx

def entropic_ratio(S_dict, K_D, clamp=100.0):
    return {k: np.clip(np.exp(v["S"]/K_D), -clamp, clamp)
            for k,v in S_dict.items()}

# ────────────── base decagonal QC field ──────────────
N, EXT = 800, 5.0
gx = np.linspace(-EXT, EXT, N)
X, Y = np.meshgrid(gx, gx)
k10  = np.arange(10)
base = np.sum(
    np.cos(2*np.pi*(np.cos(2*np.pi*k10/10)[:,None,None]*X +
                    np.sin(2*np.pi*k10/10)[:,None,None]*Y)),
    axis=0
)
base /= np.ptp(base)

# ─── diffraction → DFI → elastic‑π pre‑compute ───
mag   = np.log1p(np.abs(fftshift(fft2(base))))
ctr   = np.array([N//2, N//2])
r     = np.linspace(-N/2, N/2, N)
angs  = np.linspace(0, 2*np.pi, AXES, endpoint=False)
profiles = {
    f"I{k:02d}": map_coordinates(
        mag,
        np.vstack([ctr[0]+r*np.cos(a), ctr[1]+r*np.sin(a)]),
        order=1, mode="reflect"
    ) for k,a in enumerate(angs)
}
dfi_data   = dfi(pd.DataFrame(profiles))
K_D        = flowpoint_pi()
ratio_avg  = np.vstack(list(entropic_ratio(dfi_data, K_D).values())).mean(0)
elastic_pi = np.tile(np.pi*ratio_avg, (N,1))
fp_main    = fp(1.0)
pattern    = lambda: base * elastic_pi * next(fp_main)

def purge(ax):
    for art in (*ax.collections, *ax.lines): art.remove()

# ────────────────── sphere sampling ──────────────────
θ_vals, φ_vals = np.linspace(0,np.pi,SPHERE_RES), np.linspace(0,2*np.pi,SPHERE_RES)
Θ, Φ = np.meshgrid(θ_vals, φ_vals)
vi, ui = (Θ/np.pi)*(N-1), (Φ/(2*np.pi))*(N-1)
coords = np.vstack([vi.ravel(), ui.ravel()])
back_mask = Φ >= np.pi
to_sphere = lambda vals2d: map_coordinates(vals2d, coords, order=1, mode="wrap").reshape(SPHERE_RES, SPHERE_RES)
def sphere_coords(vals2d):
    r = 1 + 0.25*vals2d/np.ptp(vals2d)
    return r*np.sin(Θ)*np.cos(Φ), r*np.sin(Θ)*np.sin(Φ), r*np.cos(Θ)

# ───────────────── static plot builders ──────────────────
def plot_qc_contour():
    fig = plt.figure(figsize=(5,5))
    plt.contour(X, Y, pattern(), 60, cmap="plasma")
    plt.axis("off"); return fig

def plot_elastic_surface():
    fig = plt.figure(figsize=(6,5))
    ax  = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, Y, pattern(), cmap="viridis",
                    rcount=300, ccount=300, linewidth=0, antialiased=True)
    ax.set_axis_off(); return fig

def plot_diffraction():
    fig = plt.figure(figsize=(5,5))
    plt.imshow(np.log1p(np.abs(fftshift(fft2(pattern())))), cmap="inferno")
    plt.axis("off"); return fig

def plot_wavelet():
    fig = plt.figure(figsize=(6,3))
    fft_img = np.log1p(np.abs(fftshift(fft2(pattern()))))
    cwt,_ = pywt.cwt(fft_img[N//2], np.arange(1,192), "morl")
    plt.imshow(np.abs(cwt), extent=[0,N,192,1],
               cmap="RdBu", aspect="auto")
    plt.xlabel("pixel"); plt.ylabel("scale"); return fig

def plot_dfi_surface():
    fig = plt.figure(figsize=(6,3))
    ax  = fig.add_subplot(111, projection="3d")
    V0, S0 = next(iter(dfi_data.values())).values()
    grid   = np.outer(V0, S0)
    Xg,Yg  = np.meshgrid(np.arange(N), np.arange(N))
    ax.plot_surface(Xg, Yg, grid, cmap="coolwarm",
                    linewidth=0, antialiased=True)
    ax.set_axis_off(); return fig

static_steps = [
    ("qc_contour.png",        plot_qc_contour),
    ("elastic_pi_surface.png",plot_elastic_surface),
    ("diffraction_fft.png",   plot_diffraction),
    ("wavelet_central_row.png",plot_wavelet),
    ("dfi_surface.png",       plot_dfi_surface),
]

static_start = perf_counter()
for idx, (fname, builder) in enumerate(static_steps):
    fig = builder()
    fig.savefig(os.path.join(OUTPUT_DIR, fname), dpi=DPI)
    plt.close(fig); log_step("Static", idx, len(static_steps), static_start)
gc.collect()

# ────────────────── 2‑D flicker animation ──────────────────
k10 = np.arange(10)
cosk, sink = np.cos(2*np.pi*k10/10), np.sin(2*np.pi*k10/10)
figF, axF  = plt.subplots(figsize=(5,5)); axF.axis("off")
levels, fp2 = np.linspace(-1,1,65)*np.ptp(base), fp(1)
def frame_flick(i):
    purge(axF); shift = i/90
    cos_part = (cosk+shift)[:,None,None]*X
    sin_part = (sink+shift)[:,None,None]*Y
    pat = np.sum(np.cos(2*np.pi*(cos_part+sin_part)), axis=0)/10
    axF.contour(X, Y, pat*next(fp2), levels, cmap="plasma")
    return axF.collections
ani_flick = anim.FuncAnimation(figF, frame_flick,
                               frames=SCAT_FRAMES, interval=1000/FPS, blit=True)
save_animation(ani_flick, f"{OUTPUT_DIR}/elastic_pi_flicker.mp4", "Flicker")
plt.close(figF); del ani_flick; gc.collect()

# ─────────── 5‑D→3‑D OU‑camera *oscillating* scatter ────────────
pts5   = np.random.randint(-4, 5, (SCATTER_PTS, 5))
proj45 = np.random.randn(4, 5)
pts4_0 = pts5 @ proj45.T             # frozen reference frame

figS, axS = plt.subplots(
    figsize=(8, 8), subplot_kw={"projection": "3d"}
)
axS.axis("off")
lim = 38
sc  = axS.scatter([], [], [], s=2, c=[], cmap="Spectral",
                  depthshade=True, alpha=0.85)

cam, Rm = OUcamera(), np.eye(3)

def osc4(t):
    """Sinusoidally deform the 4‑D cloud with phase offsets."""
    phase = 2 * np.pi * t / OSC_PERIOD
    scale = 1.0 + 0.35 * np.sin(phase + np.arange(4) * np.pi / 2)
    return pts4_0 * scale 

def frame_scatter(i):
    global Rm
    Rm = rot(cam.step(), 0.015) @ Rm 
    P3 = osc4(i)[:, :3] @ Rm.T
    sc._offsets3d = (P3[:, 0], P3[:, 1], P3[:, 2])
    sc.set_array(osc4(i)[:, 3]) 
    axS.set(xlim=(-lim, lim), ylim=(-lim, lim), zlim=(-lim, lim))
    return sc,

ani_scatter = anim.FuncAnimation(
    figS, frame_scatter,
    frames=SCAT_FRAMES, interval=1000 / FPS, blit=True
)
save_animation(ani_scatter,
               f"{OUTPUT_DIR}/elastic_pi_scatter.mp4",
               "Scatter (osc)")
plt.close(figS); del ani_scatter; gc.collect()

# ────────────────── breathing sphere ──────────────────
figB, axB = plt.subplots(figsize=(7,7), subplot_kw={"projection":"3d"})
axB.axis("off")
def frame_sphere(i):
    purge(axB)
    vals2d = to_sphere(pattern())
    Xs,Ys,Zs = sphere_coords(vals2d)
    norm_vals = (vals2d - vals2d.min())/np.ptp(vals2d)
    surf = axB.plot_surface(
        Xs, Ys, Zs,
        facecolors=plt.cm.plasma(norm_vals),
        rcount=SPHERE_RES, ccount=SPHERE_RES,
        linewidth=0, shade=False, antialiased=False)
    axB.view_init(25, i*2)
    return surf,
ani_sphere = anim.FuncAnimation(figB, frame_sphere,
                                frames=SCAT_FRAMES, interval=1000/FPS, blit=True)
save_animation(ani_sphere, f"{OUTPUT_DIR}/elastic_pi_sphere.mp4", "Sphere")
plt.close(figB); del ani_sphere; gc.collect()

# ───────────── cut‑away half‑sphere ─────────────
figH, axH = plt.subplots(figsize=(7,7), subplot_kw={"projection":"3d"})
axH.axis("off")
def frame_half(i):
    purge(axH)
    vals2d = to_sphere(pattern())
    Xs,Ys,Zs = sphere_coords(vals2d)
    FC = plt.cm.plasma((vals2d-vals2d.min())/np.ptp(vals2d))
    surf = axH.plot_surface(np.where(back_mask,Xs,np.nan),
                            np.where(back_mask,Ys,np.nan),
                            np.where(back_mask,Zs,np.nan),
                            facecolors=np.where(back_mask[...,None],FC,np.nan),
                            linewidth=0, antialiased=False, shade=False)
    axH.plot_wireframe(np.where(~back_mask,Xs,np.nan),
                       np.where(~back_mask,Ys,np.nan),
                       np.where(~back_mask,Zs,np.nan),
                       rcount=SPHERE_RES//8, ccount=SPHERE_RES//8,
                       linewidth=0.3, alpha=0.7)
    axH.view_init(20, i*2)
    return surf,
ani_half = anim.FuncAnimation(figH, frame_half,
                              frames=SCAT_FRAMES, interval=1000/FPS, blit=True)
save_animation(ani_half, f"{OUTPUT_DIR}/elastic_pi_half_sphere.mp4", "Half‑Sphere")
plt.close(figH); del ani_half; gc.collect()

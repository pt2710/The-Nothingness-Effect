#!/usr/bin/env python3
"""
Author : B. McCrackn
Email  : thenothingnesseffect@gmail.com
Usage  : python simulate_elastic_pi.py

High-contrast black hole demo:
  • πₑ plotted with log norm (vmin=1e-6–vmax=1)
  • K_D override to 0.5 for steeper core drop
  • Spike starts at 50% and intensifies over 50%
  • Clear cyan horizon and red/orange shell
Outputs: visualizations/piE_blackhole_dfi_event.mp4,
         visualizations/initial_frame.png,
         visualizations/final_frame.png,
         CSV slices.
"""

import os, sys, time, shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import LogNorm
from numba import njit


from the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index.dfi import DynamicFluctuationIndex
from the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi.elastic_pi import ElasticPi

HERE      = os.path.dirname(__file__)
VIS_DIR   = os.path.join(HERE, "visualizations")
DATA_DIR  = os.path.join(HERE, "data_results")
os.makedirs(VIS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

@njit(fastmath=True, cache=True)
def lap2_numba(Z, dx, out):
    N = Z.shape[0]
    for i in range(1, N-1):
        for j in range(1, N-1):
            out[i,j] = (
                Z[i+1,j] + Z[i-1,j] + Z[i,j+1] + Z[i,j-1] - 4*Z[i,j]
            ) / (dx*dx)
    return out

def _bar(i, n, t0, label="Progress"):
    term_width = shutil.get_terminal_size((80,20)).columns
    p = (i+1)/n if n else 1.0
    elapsed = time.time() - t0
    rem = (elapsed/p - elapsed) if p>0 else 0
    pct = f"{p*100:6.2f}%"
    info = f"{label} {pct} {elapsed:5.1f}s ↔ {rem:5.1f}s"
    bw = max(10, term_width - len(info) - 4)
    filled = int(bw*p)
    bar = "#"*filled + "-"*(bw-filled)
    out = f"\r[{bar}] {info}"
    pad = " "*(term_width - len(out))
    sys.stdout.write(out+pad)
    sys.stdout.flush()
    if i==n-1:
        sys.stdout.write("\n")

def simulate(N=140, T=220, dt=0.08, L=6.0, eps_h=5e-3):
    x = np.linspace(-L,L,N)
    dx = x[1]-x[0]
    X,Y = np.meshgrid(x,x,indexing="ij")
    dfi = DynamicFluctuationIndex()
    ent = dfi.dfi(np.random.rand(10,3))
    seed_S = np.mean([ent[c]["Relative_Entropy"][0] for c in ent])

    delta = np.zeros_like(X)
    epi = ElasticPi(K_D=0.5)
    frames=[]
    t0=time.time()
    lap_buf=np.zeros_like(delta)

    delay = T//2
    n_spike = T-delay
    spike_amp = seed_S*12
    sigma=L/10

    for k in range(T):
        lap2_numba(delta,dx,lap_buf)
        delta += lap_buf * 0.02 * dt
        delta *= (1-0.012*dt)
        delta = np.maximum(delta,0)

        if k>=delay:
            r2 = X**2+Y**2
            delta += np.exp(-r2/(2*sigma**2))*spike_amp/n_spike

        _, piE, _ = epi.compute_piE_and_laplacian(S=delta)
        lnpi = np.log(np.clip(piE,1e-9,None))
        lap2_numba(lnpi,dx,lap_buf)
        gx,gy = np.gradient(piE,dx,edge_order=2)
        np.hypot(gx,gy,out=lap_buf)
        horizon = lap_buf<eps_h

        frames.append(dict(t=k*dt, piE=piE.copy(), horizon=horizon.copy()))
        _bar(k,T-1,t0,label="Simulation")
    _bar(T-1,T-1,t0,label="Simulation")
    return x,frames

def export(frames,x):
    mid=len(x)//2
    for key in ("piE","horizon"):
        arr=np.stack([f[key][mid,:] for f in frames])
        pd.DataFrame(arr,columns=[f"y={v:.2f}" for v in x])\
          .to_csv(os.path.join(DATA_DIR,f"{key}_central_slice.csv"),index_label="t_idx")

def animate(x, frames, eps_h=5e-3, fname="piE_blackhole_dfi_event.mp4"):
    """High‑contrast animation that keeps the same log‑scale for every frame
    so the emerging black‑hole core never washes out.  The instantaneous
    horizon that was already computed inside *simulate()* (and stored in
    the ``horizon`` field) is used directly for the cyan contour, so the
    user‑supplied ``eps_h`` is no longer left dangling.
    """
    X, Y = np.meshgrid(x, x, indexing="ij")

    # ------------------------------------------------------------------
    # 1.  Figure and the *constant* colormap normal (fixed vmin / vmax)
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 6))
    norm = LogNorm(vmin=1e-6, vmax=1)           # <- fixed for ALL frames

    img = ax.imshow(
        frames[0]["piE"].T,
        extent=[x[0], x[-1], x[0], x[-1]],
        origin="lower",
        norm=norm,
        cmap="magma",
        animated=True,
    )
    plt.colorbar(img, ax=ax, label="πₑ")
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # caches for over‑lays so we can update them in‑place ───────────────
    contour_set = [None]
    shell_im    = [None]

    # ------------------------------------------------------------------
    # 2.  Per‑frame drawer
    # ------------------------------------------------------------------
    def draw(i: int):
        f = frames[i]
        pi = f["piE"]

        # Update main image but *do not* rescale colour‑limits
        img.set_data(pi.T)

        # Cyan horizon: use the boolean mask that simulate() already built
        mask = f["horizon"].astype(float)
        if contour_set[0] is not None:
            contour_set[0].remove()
        contour_set[0] = ax.contour(
            X,
            Y,
            mask,
            levels=[0.5],   # 0‑1 mask ⇒ 0.5 separates inside / outside
            colors="cyan",
            linewidths=2.0,
        )


        # Hawking‑shell: where πₑ just crossed the horizon and is growing
        if i > 0:
            dpi   = pi - frames[i - 1]["piE"]
            shell = (frames[i - 1]["horizon"] == 0) & (f["horizon"] == 1) & (dpi > 0)
            if shell_im[0] is not None:
                shell_im[0].set_data(shell.T)
            else:
                shell_im[0] = ax.imshow(
                    shell.T,
                    extent=[x[0], x[-1], x[0], x[-1]],
                    origin="lower",
                    cmap="YlOrRd",
                    alpha=0.8,
                    vmin=0,
                    vmax=1,
                    animated=True,
                )

        ax.set_title(f"t = {f['t']:.2f}")
        return img,

    # ------------------------------------------------------------------
    # 3.  Render and save
    # ------------------------------------------------------------------
    def anim_progress(i, nframes):
        _bar(i, nframes, anim_progress.start_time, label="Animation")

    anim_progress.start_time = time.time()
    ani = animation.FuncAnimation(
        fig,
        draw,
        frames=len(frames),
        interval=35,
        blit=False,
    )
    ani.save(
        os.path.join(VIS_DIR, fname),
        writer="ffmpeg",
        dpi=160,
        progress_callback=anim_progress,
    )
    plt.close(fig)

    # ------------------------------------------------------------------
    # 4.  Snapshots (initial / final) in the *same* colour‑scale
    # ------------------------------------------------------------------
    for tag, f in zip(["initial", "final"], [frames[0], frames[-1]]):
        fig_s, ax_s = plt.subplots(figsize=(7, 6))
        ax_s.imshow(
            f["piE"].T,
            extent=[x[0], x[-1], x[0], x[-1]],
            origin="lower",
            norm=norm,
            cmap="magma",
        )
        ax_s.contour(
            X,
            Y,
            f["horizon"].astype(float),
            levels=[0.5],
            colors="cyan",
            linewidths=2.0,
        )
        ax_s.axis("off")
        plt.savefig(
            os.path.join(VIS_DIR, f"{tag}_frame.png"),
            bbox_inches="tight",
            pad_inches=0,
        )
        plt.close(fig_s)

def generate_appendix_figures(x, frames, vis_dir):
    """
    Generates and saves the required simulation figures for the elastic Pi manuscript appendix.

    Args:
        x (np.ndarray): Spatial grid.
        frames (list): List of frame dicts from the simulation.
        vis_dir (str): Output directory for visualizations.

    Outputs:
        elastic_pi_surface.png
        pi_laplacian_curvature.png
        pi_dfi_overlay.png
    """
    # Use final frame for static analysis
    piE = frames[-1]['piE']
    X, Y = np.meshgrid(x, x, indexing="ij")
    # Surface plot of pi_E(x, t)
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, piE, cmap='magma', linewidth=0, antialiased=False)
    ax.set_title(r"$\pi_{\mathcal{E}}(x,t)$ surface")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel(r"$\pi_{\mathcal{E}}$")
    fig.colorbar(surf, shrink=0.5, aspect=10)
    plt.tight_layout()
    plt.savefig(os.path.join(vis_dir, "elastic_pi_surface.png"), dpi=160)
    plt.close(fig)

    # Laplacian of log(pi_E) as curvature heatmap
    lnpi = np.log(np.clip(piE, 1e-12, None))
    dx = x[1] - x[0]
    lap = np.zeros_like(lnpi)
    lap2_numba(lnpi, dx, lap)
    fig2, ax2 = plt.subplots(figsize=(7, 6))
    im = ax2.imshow(lap.T, extent=[x[0], x[-1], x[0], x[-1]], origin="lower", cmap='inferno')
    fig2.colorbar(im, ax=ax2, label=r"$\nabla^2 \ln \pi_{\mathcal{E}}$")
    ax2.set_title(r"Laplacian of $\ln\pi_{\mathcal{E}}(x, t)$: Approximate curvature")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    plt.tight_layout()
    plt.savefig(os.path.join(vis_dir, "pi_laplacian_curvature.png"), dpi=160)
    plt.close(fig2)

    # DFI/Exponential vs. Conformal field overlay (compare two definitions)
    # DFI exponential: piE_exp = pi * exp(-S/K_D)
    epi = ElasticPi(K_D=0.5)
    S = -np.log(np.clip(piE/np.pi, 1e-12, 1)) * epi.K_D
    piE_dfi = np.pi * np.exp(-S / epi.K_D)
    delta = (1 - piE / np.pi) / (1 + piE / np.pi)
    piE_conf = np.pi * (1 - delta) / (1 + delta)
    diff = np.abs(piE_dfi - piE_conf)
    fig3, ax3 = plt.subplots(figsize=(7, 6))
    im3 = ax3.imshow(diff.T, extent=[x[0], x[-1], x[0], x[-1]], origin="lower", cmap='viridis')
    fig3.colorbar(im3, ax=ax3, label=r"DFI/Conformal $|\Delta \pi_{\mathcal{E}}|$")
    ax3.set_title(r"Overlay: DFI vs. Conformal $\pi_{\mathcal{E}}(x,t)$")
    ax3.set_xlabel("x")
    ax3.set_ylabel("y")
    plt.tight_layout()
    plt.savefig(os.path.join(vis_dir, "pi_dfi_overlay.png"), dpi=160)
    plt.close(fig3)

# --- Main() insertion: call after animate(x, f) ---
def main():
    x, f = simulate()
    export(f, x)
    animate(x, f)
    generate_appendix_figures(x, f, VIS_DIR)
    print("Done")

if __name__=="__main__":
    main()

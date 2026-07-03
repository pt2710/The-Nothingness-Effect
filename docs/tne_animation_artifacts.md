# TNE Animation Artifacts

These animations are finite deterministic TNE-proxy visualizations. They
illustrate entropic horizon crossing, Hawking-like flux proxies,
observer-horizon emergence, and locality-driven spiral formation. They are not
full GR/QFT or astrophysical simulations and are not formal proof substitutes.

## Purpose

The animation scripts extend the manuscript-linked repository artifacts with
deterministic 2D visualizations for Section 16.4, Section 18.6, and Section
18.13. They are repository-linked computational artifacts that visualize the
same toy proxy models used by the still-image simulations.

## Claim Boundary

Treat these outputs as finite illustrative simulations and TNE proxy
animations. They do not prove TNE, do not prove Hawking radiation, do not
replace formal proof, and do not constitute full GR/QFT or astrophysical
simulation.

## Commands

Run the 2D animation scripts in quick mode:

```bash
python -m equations.black_hole_dynamics.animation.animate_entropic_horizon_2d --quick
python -m equations.black_hole_dynamics.animation.animate_hawking_like_flux_2d --quick
python -m equations.black_hole_dynamics.animation.animate_observer_horizon_memory_2d --quick
python -m equations.locality_driven_gravity.animation.animate_spiral_galaxy_2d --quick --arm-mode 2
python -m equations.locality_driven_gravity.animation.animate_spiral_galaxy_2d --quick --arm-mode 3
python -m equations.locality_driven_gravity.animation.animate_spiral_galaxy_2d --quick --arm-mode 4
python -m equations.locality_driven_gravity.animation.animate_spiral_galaxy_2d --quick --arm-mode mixed
```

Run the 3D animation scripts in quick mode:

```bash
python -m equations.black_hole_dynamics.animation.animate_entropic_tension_3d --quick
python -m equations.black_hole_dynamics.animation.animate_hawking_flux_3d --quick
python -m equations.black_hole_dynamics.animation.animate_observer_horizon_3d --quick
python -m equations.locality_driven_gravity.animation.animate_spiral_galaxy_3d --quick --arm-mode 2
python -m equations.locality_driven_gravity.animation.animate_spiral_galaxy_3d --quick --arm-mode 3
python -m equations.locality_driven_gravity.animation.animate_spiral_galaxy_3d --quick --arm-mode 4
python -m equations.locality_driven_gravity.animation.animate_spiral_galaxy_3d --quick --arm-mode mixed
python -m equations.run_animation_artifacts --quick
```

For the spiral-galaxy proxy specifically, the animation now renders:

- explicit mass-bearing bodies
- controlled arm-mode initialization (`2`, `3`, `4`, `mixed`)
- a density heatmap and ridge contours in 2D
- fading trajectory trails
- a central mass marker
- tension-surface structure in 3D
- spiral metrics in metadata and on-frame overlays
- stability/evolution diagnostics in metadata for later report linkage

This remains a finite spiral-formation proxy, not a full astrophysical simulation and not an empirical validation claim.

Run the focused animation tests:

```bash
python -m pytest equations/black_hole_dynamics/test/test_black_hole_animations.py
python -m pytest equations/locality_driven_gravity/test/test_spiral_animations.py
```

## Output Paths

- `equations/black_hole_dynamics/animation/entropic_horizon_crossing_2d.mp4`
- `equations/black_hole_dynamics/animation/entropic_horizon_crossing_2d.gif`
- `equations/black_hole_dynamics/animation/entropic_horizon_crossing_2d_frame_strip.png`
- `equations/black_hole_dynamics/animation/entropic_horizon_crossing_2d_data.npz`
- `equations/black_hole_dynamics/animation/entropic_horizon_crossing_2d_metadata.json`
- `equations/black_hole_dynamics/animation/hawking_like_flux_2d.mp4`
- `equations/black_hole_dynamics/animation/hawking_like_flux_2d.gif`
- `equations/black_hole_dynamics/animation/hawking_like_flux_2d_frame_strip.png`
- `equations/black_hole_dynamics/animation/hawking_like_flux_2d_data.npz`
- `equations/black_hole_dynamics/animation/hawking_like_flux_2d_metadata.json`
- `equations/black_hole_dynamics/animation/observer_horizon_memory_2d.mp4`
- `equations/black_hole_dynamics/animation/observer_horizon_memory_2d.gif`
- `equations/black_hole_dynamics/animation/observer_horizon_memory_2d_frame_strip.png`
- `equations/black_hole_dynamics/animation/observer_horizon_memory_2d_data.npz`
- `equations/black_hole_dynamics/animation/observer_horizon_memory_2d_metadata.json`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_2d.mp4`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_2d.gif`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_2d_frame_strip.png`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_2d_data.npz`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_2d_metadata.json`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_2d_arm_mode_3.mp4`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_2d_arm_mode_mixed_frame_strip.png`
- `equations/black_hole_dynamics/animation/entropic_tension_3d.mp4`
- `equations/black_hole_dynamics/animation/entropic_tension_3d.gif`
- `equations/black_hole_dynamics/animation/entropic_tension_3d_frame_strip.png`
- `equations/black_hole_dynamics/animation/entropic_tension_3d_data.npz`
- `equations/black_hole_dynamics/animation/entropic_tension_3d_metadata.json`
- `equations/black_hole_dynamics/animation/hawking_flux_from_entropic_tension_3d.mp4`
- `equations/black_hole_dynamics/animation/hawking_flux_from_entropic_tension_3d.gif`
- `equations/black_hole_dynamics/animation/hawking_flux_from_entropic_tension_3d_frame_strip.png`
- `equations/black_hole_dynamics/animation/hawking_flux_from_entropic_tension_3d_data.npz`
- `equations/black_hole_dynamics/animation/hawking_flux_from_entropic_tension_3d_metadata.json`
- `equations/black_hole_dynamics/animation/observer_horizon_appear_disappear_3d.mp4`
- `equations/black_hole_dynamics/animation/observer_horizon_appear_disappear_3d.gif`
- `equations/black_hole_dynamics/animation/observer_horizon_appear_disappear_3d_frame_strip.png`
- `equations/black_hole_dynamics/animation/observer_horizon_appear_disappear_3d_data.npz`
- `equations/black_hole_dynamics/animation/observer_horizon_appear_disappear_3d_metadata.json`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_3d.mp4`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_3d.gif`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_3d_frame_strip.png`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_3d_data.npz`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_3d_metadata.json`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_3d_arm_mode_4.mp4`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_3d_arm_mode_mixed_frame_strip.png`
- `equations/animation_artifacts_summary.csv`
- `equations/animation_artifacts_metadata.json`

Not every run will produce both `.mp4` and `.gif`. The scripts prefer MP4,
fall back to GIF, and if no writer is available they still produce a
deterministic frame-strip PNG together with raw data and metadata.

## Quick Mode

`--quick` reduces frame count and grid/particle resolution so tests and local
validation remain fast and deterministic. Quick mode is intended for CI-style
artifact validation, not for the highest-quality repository export.

The animation scripts and aggregate runner also support explicit output-format
selection through `--format mp4|gif|frames`. If MP4/GIF writers are
unavailable, the code still writes deterministic frame-strip PNGs, raw `.npz`
data, and `.json` metadata. 3D renders are intentionally moderate in
resolution, because quick-mode runtime and deterministic reproducibility matter
more here than cinematic rendering.

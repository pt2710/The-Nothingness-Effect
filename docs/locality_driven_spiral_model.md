# Locality-Driven Spiral Model

## Purpose

The locality-driven spiral model is a finite TNE proxy model in which mass-bearing bodies deform an entropic-elastic locality field, and the resulting gravity-plus-elastic tension field feeds back into body motion. It is not a full astrophysical galaxy simulation and is not an empirical validation claim.

## Scope Boundary

- finite spiral-formation proxy
- TNE locality-driven galaxy proxy
- entropic-elastic spacetime-continuum toy model
- not a full astrophysical simulation
- not an empirical validation claim
- not a formal proof substitute

This model does not replace N-body or hydrodynamical galaxy simulations, does not prove TNE, and does not establish that dark matter is unnecessary.

## Body Classes

The simulation initializes explicit mass-bearing bodies:

- `central_mass`
- `star_system`
- `gas_cloud`
- `cluster`
- `optional_small_body`

Each body carries:

- mass
- softening radius
- position
- velocity
- spin proxy
- luminosity proxy
- entropic coupling
- elastic coupling

The central mass is a fixed bulge-like anchor. The disk contains star systems, gas clouds, and clusters with deterministic seeded perturbations.

## Gravity Force

The model uses softened pairwise gravity:

```text
a_grav_i = sum_j G_eff * m_j * (r_j - r_i) / (|r_j-r_i|^2 + eps_ij^2)^(3/2)
```

where `eps_ij` includes the global softening term and body-specific softening scales. A lighter locality-weighted shear term is also included as a secondary rotational proxy.

## Entropic-Elastic Locality Field

At each step the model builds a smooth density field `rho(x, y, t)` from body masses using a Gaussian kernel on a deterministic grid.

From that density field it derives:

- entropy/locality density proxy
- tension/stretch proxy
- shear proxy from local angular-velocity gradients
- simple strain proxies `strain_xx`, `strain_xy`, `strain_yy`

The tension field is updated through a relaxed feedback rule:

```text
tension_new
  = relax * tension_old
  + alpha * normalized_density
  + beta * |grad density|
  + gamma * local_shear
  + wave_seed
```

## Mass Density to Local Bending / Stretch

Higher local mass density increases the locality-field response through two separate channels:

1. direct density contribution
2. density-gradient contribution near ridges and arm boundaries

This means concentrated mass not only strengthens the local field value, but also sharpens the local tension response around emerging arm-like structures.

## Feedback into Body Motion

The total acceleration combines:

- pairwise gravity
- locality-weighted rotational shear
- elastic response from the negative tension gradient

Conceptually:

```text
a_total = a_grav + a_locality + a_elastic
a_elastic = -kappa * coupling * grad(tension)
```

Bodies with higher entropic or elastic coupling respond more strongly to the locality-field gradient.

## Differential Rotation

The disk is initialized with a radius-dependent circular-speed proxy and a deterministic differential-rotation factor. Outer radii rotate differently from inner radii, so seeded perturbations wind into arm-like structures rather than remaining rigid.

## Asymmetry Seed

The initial disk includes:

- a bar-like `m=2` perturbation
- deterministic radial wave interference
- small seeded local offsets
- arm selection phase splitting

The arms are therefore not drawn as static overlays. They emerge from the body distribution and its subsequent gravity-plus-tension evolution.

## Metrics

The model reports:

- `spiral_order_parameter`
- `mode_2_amplitude`
- `mode_3_amplitude`
- `pitch_angle_proxy`
- `radial_concentration`
- `density_arm_contrast`
- `angular_momentum_initial`
- `angular_momentum_final`
- `angular_momentum_drift`
- `total_mass`
- `energy_proxy`
- `elastic_tension_mean`
- `elastic_tension_max`
- `arm_asymmetry_index`

These are descriptive diagnostics for the toy model only.

## Artifact Paths

Simulation outputs:

- `equations/locality_driven_gravity/simulation/figure6_locality_driven_spiral.png`
- `equations/locality_driven_gravity/simulation/figure6_spiral_particles.npz`
- `equations/locality_driven_gravity/simulation/figure6_spiral_metrics.csv`
- `equations/locality_driven_gravity/simulation/locality_spiral_metrics.csv`
- `equations/locality_driven_gravity/simulation/figure6_metadata.json`
- `equations/locality_driven_gravity/simulation/locality_spiral_metadata.json`

Animation outputs:

- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_2d.mp4`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_2d_frame_strip.png`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_3d.mp4`
- `equations/locality_driven_gravity/animation/spiral_galaxy_formation_3d_frame_strip.png`

## Limitations

- not a full astrophysical simulation
- not a GR simulation
- not a hydrodynamical gas model
- not an empirical validation claim
- not a dark-matter-replacement claim
- not a formal proof substitute

The model is useful as a repository-linked supplementary visualization and computational support artifact for manuscript discussion of locality-driven spiral morphology.

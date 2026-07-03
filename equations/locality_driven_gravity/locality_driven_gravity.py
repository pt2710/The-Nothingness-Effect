"""Public facade for the finite locality-driven spiral proxy model.

The underlying implementation is an entropic-elastic spacetime-continuum toy
model in which mass-bearing bodies deform a locality field and the resulting
gravity-plus-elastic tension field feeds back into body motion. It is not a
full astrophysical simulation, not an empirical validation claim, and not a
formal proof substitute.
"""

from __future__ import annotations

from equations.locality_driven_gravity.entropic_elastic_spiral import (
    ArmMode,
    BodyType,
    LocalityGravityParams,
    SpiralBody,
    arm_phase_offsets,
    compare_spiral_arm_modes,
    compute_spiral_metrics,
    density_field,
    entropic_elastic_field,
    gravity_acceleration,
    initialize_spiral_bodies,
    locality_force,
    locality_kernel,
    radial_velocity_profile,
    simulate_spiral_arm_mode,
    simulate_locality_spiral,
    spiral_pitch_proxy,
    step_locality_gravity,
)

__all__ = [
    "ArmMode",
    "BodyType",
    "LocalityGravityParams",
    "SpiralBody",
    "arm_phase_offsets",
    "compare_spiral_arm_modes",
    "compute_spiral_metrics",
    "density_field",
    "entropic_elastic_field",
    "gravity_acceleration",
    "initialize_spiral_bodies",
    "locality_force",
    "locality_kernel",
    "radial_velocity_profile",
    "simulate_spiral_arm_mode",
    "simulate_locality_spiral",
    "spiral_pitch_proxy",
    "step_locality_gravity",
]

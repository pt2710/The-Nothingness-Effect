'Authoritative theorem title: Local Horizon Boundary.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='local_horizon_boundary_and_non_locality_divergence',
    role=TheoremRole.LEFT,
    authoritative_title='Local Horizon Boundary',
    authoritative_title_tex='Local Horizon Boundary',
    equation_labels=('eq:obs12_tail_profile_1c', 'eq:obs12_individual_horizon_radius_1c', 'eq:obs12_uniform_tightness_1c', 'eq:obs12_family_horizon_radius_1c', 'eq:obs12_common_horizon_bound_1c', 'eq:obs12_exact_common_support_1c', 'eq:obs12_individual_tail_decay_1c', 'eq:obs12_tail_orbit_invariance_1c', 'eq:obs12_horizon_perturbation_bound_1c', 'eq:obs12_synthesis_1c', 'eq:std_obs12_principle_1c'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Self-Negating Oscillation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='self_negating_oscillation_and_eigenstructure',
    role=TheoremRole.LEFT,
    authoritative_title='Self-Negating Oscillation',
    authoritative_title_tex='Self-Negating Oscillation',
    equation_labels=('eq:self_negating_flowpoint_sector_1a', 'eq:self_negating_flowpoint_orbit_definition_1a', 'eq:self_negating_flowpoint_orbit_recursion_definition_1a', 'eq:self_negating_flowpoint_oscillation_closed_form_1a', 'eq:self_negating_flowpoint_oscillation_periodicity_1a', 'eq:self_negating_flowpoint_two_state_orbit_1a', 'eq:fp_recursion_step_algebraic_1a', 'eq:fp_recursion_even_odd_1a', 'eq:flowpoint_harmonic_interpolation_1a', 'eq:flowpoint_harmonic_sampling_1a', 'eq:flowpoint_harmonic_ode_corrected_1a', 'eq:anti_invariant_flowpoint_equivalence_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

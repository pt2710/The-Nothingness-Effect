'Authoritative theorem title: Null Recurrence of the Cubical Cover Walk.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='recurrent_cubical_cover_dynamics',
    role=TheoremRole.RIGHT,
    authoritative_title='Null Recurrence of the Cubical Cover Walk',
    authoritative_title_tex='Null Recurrence of the Cubical Cover Walk',
    equation_labels=('eq:ci_b02_boundary_hold_2b', 'eq:ci_b02_boundary_move_2b', 'eq:ci_b02_interior_hold_2b', 'eq:ci_b02_interior_move_2b', 'eq:ci_b02_reversible_measure_2b', 'eq:ci_b02_universal_return_2b', 'eq:ci_b02_zero_frequency_2b', 'eq:ci_b02_detailed_balance_2b', 'eq:ci_b02_resistance_divergence_2b', 'eq:ci_b02_stationary_marginal_2b', 'eq:ci_b02_synthesis_2b', 'eq:ci_b02_finite_fibre_recurrence_principle_2b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

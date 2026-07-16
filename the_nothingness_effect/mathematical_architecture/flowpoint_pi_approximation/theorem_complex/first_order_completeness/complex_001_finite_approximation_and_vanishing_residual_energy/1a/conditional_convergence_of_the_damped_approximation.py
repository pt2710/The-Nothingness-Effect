'Authoritative theorem title: Conditional Convergence of the Damped Approximation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='finite_approximation_and_vanishing_residual_energy',
    role=TheoremRole.LEFT,
    authoritative_title='Conditional Convergence of the Damped Approximation',
    authoritative_title_tex='Conditional Convergence of the Damped Approximation',
    equation_labels=('eq:fp_pi_definition_partial_sum_1a', 'eq:fm_pi_error_bound_1a', 'eq:fm_pi_tail_decomposition_1a', 'eq:fm_pi_stopping_index_1a', 'eq:fm_pi_approximation_synthesis_1a', 'eq:fm_pi_approximation_principle_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Existence and Conditional Uniqueness of Spectral Minimizers.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='operation_covariance_and_spectral_minimization',
    role=TheoremRole.RIGHT,
    authoritative_title='Existence and Conditional Uniqueness of Spectral Minimizers',
    authoritative_title_tex='Existence and Conditional Uniqueness of Spectral Minimizers',
    equation_labels=('eq:fm_alg_minimizer_set_2a', 'eq:fm_alg_unique_minimizer_2a', 'eq:fm_alg_minimizer_transport_2a', 'eq:fm_alg_phase_fixed_optimizer_2a', 'eq:fm_alg_minimizer_synthesis_2a', 'eq:fm_alg_minimizer_principle_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

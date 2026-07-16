'Authoritative theorem title: Operation-Specific Phase Covariance.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='operation_covariance_and_spectral_minimization',
    role=TheoremRole.LEFT,
    authoritative_title='Operation-Specific Phase Covariance',
    authoritative_title_tex='Operation-Specific Phase Covariance',
    equation_labels=('eq:fm_alg_covariance_residual_1a', 'eq:fm_alg_covariance_criterion_1a', 'eq:fm_alg_parity_composition_1a', 'eq:fm_alg_trig_parity_1a', 'eq:fm_alg_covariance_synthesis_1a', 'eq:fm_alg_covariance_principle_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

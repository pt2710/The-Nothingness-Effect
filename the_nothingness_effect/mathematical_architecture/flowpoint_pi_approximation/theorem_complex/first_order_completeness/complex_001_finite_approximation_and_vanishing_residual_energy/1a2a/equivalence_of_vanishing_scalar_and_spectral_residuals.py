'Authoritative theorem title: Equivalence of Vanishing Scalar and Spectral Residuals.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='finite_approximation_and_vanishing_residual_energy',
    role=TheoremRole.CROSS,
    authoritative_title='Equivalence of Vanishing Scalar and Spectral Residuals',
    authoritative_title_tex='Equivalence of Vanishing Scalar and Spectral Residuals',
    equation_labels=('eq:fm_pi_joint_certificate_1a2a', 'eq:fm_pi_joint_equivalence_1a2a', 'eq:fm_pi_joint_domination_1a2a', 'eq:fm_pi_two_channel_stopping_1a2a', 'eq:fm_pi_joint_synthesis_1a2a', 'eq:fm_pi_joint_principle_1a2a', 'eq:fp_pi_pi_frequency_consistency_check_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

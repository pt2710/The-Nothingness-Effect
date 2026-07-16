'Authoritative theorem title: Parity-Bias Symmetry Breaking.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='z_2_2_sign_symmetry_parity_bias_symmetry_breaking',
    role=TheoremRole.RIGHT,
    authoritative_title='Parity-Bias Symmetry Breaking',
    authoritative_title_tex='Parity-Bias Symmetry Breaking',
    equation_labels=('eq:z2_parity_breaking_bound_2a', 'eq:z2_parity_eps_lower_2a', 'eq:z2_corr_bias_fourier_2a', 'eq:z2_eps_expectation_bound_2a', 'eq:z2_parity_breaking_algebra_ineq_2a', 'eq:z2_projection_residual_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Non-Invertible Reconstruction (2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='algebraic_analytic_reconstruction_equivalence_non_invertible_reconstruction',
    role=TheoremRole.RIGHT,
    authoritative_title='Non-Invertible Reconstruction',
    authoritative_title_tex='Non-Invertible Reconstruction (2A)',
    equation_labels=('eq:residual_off_support_2a', 'eq:residual_energy_2a', 'eq:single_line_mismatch_2a', 'eq:residual_characterization_2a', 'eq:detect_violation_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

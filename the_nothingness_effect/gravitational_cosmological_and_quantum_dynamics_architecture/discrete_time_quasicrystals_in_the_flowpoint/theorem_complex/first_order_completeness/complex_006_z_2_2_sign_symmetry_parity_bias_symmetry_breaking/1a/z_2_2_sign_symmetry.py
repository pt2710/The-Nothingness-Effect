'Authoritative theorem title: $\\mathbb{Z}_2^{\\,2}$ Sign Symmetry.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='z_2_2_sign_symmetry_parity_bias_symmetry_breaking',
    role=TheoremRole.LEFT,
    authoritative_title='Z_2^ 2 Sign Symmetry',
    authoritative_title_tex='$\\mathbb{Z}_2^{\\,2}$ Sign Symmetry',
    equation_labels=('eq:z2_symmetry_inner_1a', 'eq:z2_symmetry_fourier_1a', 'eq:z2_parity_lock_zero_gap_1a', 'eq:z2_parity_symmetry_core_1a', 'eq:z2_parity_zero_reg_penalty_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

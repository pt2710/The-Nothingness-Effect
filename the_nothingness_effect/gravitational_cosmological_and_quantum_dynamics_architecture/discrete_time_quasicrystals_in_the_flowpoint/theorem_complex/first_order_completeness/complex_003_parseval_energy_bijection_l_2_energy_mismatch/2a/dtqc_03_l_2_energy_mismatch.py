'Authoritative theorem title: DTQC 03 -- $L^2$ Energy Mismatch.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='parseval_energy_bijection_l_2_energy_mismatch',
    role=TheoremRole.RIGHT,
    authoritative_title='DTQC 03 – L^2 Energy Mismatch',
    authoritative_title_tex='DTQC 03 -- $L^2$ Energy Mismatch',
    equation_labels=('eq:psv_positive_gap_2a', 'eq:psv_gap_as_minresid_2a', 'eq:l2_gap_equals_resid_2a', 'eq:Jmin_equals_resnorm_2a', 'eq:l2_gap_positive_algebraic_2a', 'eq:gap_positive_iff_residual_2a', 'eq:coeff_energy_leq_signal_energy_2a', 'eq:lower_bound_fit_error_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

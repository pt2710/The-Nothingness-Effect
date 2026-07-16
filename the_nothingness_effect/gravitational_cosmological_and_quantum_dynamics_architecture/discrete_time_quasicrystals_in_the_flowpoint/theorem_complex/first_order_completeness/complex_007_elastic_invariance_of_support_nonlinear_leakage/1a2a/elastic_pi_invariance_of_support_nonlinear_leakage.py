'Authoritative theorem title: Elastic-$\\pi$ Invariance of Support $\\leftrightarrow$ Nonlinear Leakage.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_invariance_of_support_nonlinear_leakage',
    role=TheoremRole.CROSS,
    authoritative_title='Elastic-pi Invariance of Support <-> Nonlinear Leakage',
    authoritative_title_tex='Elastic-$\\pi$ Invariance of Support $\\leftrightarrow$ Nonlinear Leakage',
    equation_labels=('eq:dtqc07_constant_gain_active_support', 'eq:dtqc07_timevarying_gain_support', 'eq:dtqc07_polynomial_active_support', 'eq:dtqc07_joint_status_1a2a', 'eq:epsi_support_set_def_1a2a', 'eq:epsi_dtqc_series_def_1a2a', 'eq:epsi_linear_stationary_1a2a', 'eq:epsi_linear_timevarying_1a2a', 'eq:epsi_product_rule_fourier_1a2a', 'eq:epsi_cubic_nonlinear_1a2a', 'eq:epsi_dichotomy_statement_1a2a', 'eq:epsi_time_avg_equivalence_1a2a', 'eq:epsi_case_split_1a2a', 'eq:epsi_near_lattice_threshold_1a2a', 'eq:epsi_continuity_threshold_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

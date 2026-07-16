'Authoritative theorem title: Prime–Quasicrystal Support Equivalence $\\leftrightarrow$ Support Mismatch/Leakage.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='prime_quasicrystal_support_equivalence_support_mismatch_leakage',
    role=TheoremRole.CROSS,
    authoritative_title='Prime–Quasicrystal Support Equivalence <-> Support Mismatch/Leakage',
    authoritative_title_tex='Prime–Quasicrystal Support Equivalence $\\leftrightarrow$ Support Mismatch/Leakage',
    equation_labels=('eq:prime_qc_update_align_1a2a', 'eq:prime_qc_parseval_equiv_1a2a', 'eq:prime_qc_energy_flux_align_1a2a', 'eq:prime_qc_energy_rate_equiv_1a2a', 'eq:prime_qc_slope_criterion_align_1a2a', 'eq:prime_qc_slope_criterion_equation_1a2a', 'eq:prime_qc_slope_integral_align_1a2a', 'eq:prime_qc_slope_integral_equation_1a2a', 'eq:prime_qc_indicator_align_1a2a', 'eq:prime_qc_indicator_equation_1a2a', 'eq:prime_qc_cesaro_align_1a2a', 'eq:prime_qc_cesaro_equation_1a2a', 'eq:prime_qc_ops_scores_align_1a2a', 'eq:prime_qc_ops_scores_equation_1a2a', 'eq:prime_qc_ops_smooth_align_1a2a', 'eq:prime_qc_ops_smooth_equation_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

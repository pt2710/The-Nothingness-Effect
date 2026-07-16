'Authoritative theorem title: PV Inflation (Pure-Point Diffraction) $\\leftrightarrow$ Non-PV/Salem Leakage (1A $\\leftrightarrow$ 2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='pv_inflation_pure_point_diffraction_non_pv_salem_leakage',
    role=TheoremRole.CROSS,
    authoritative_title='PV Inflation (Pure-Point Diffraction) <-> Non-PV/Salem Leakage',
    authoritative_title_tex='PV Inflation (Pure-Point Diffraction) $\\leftrightarrow$ Non-PV/Salem Leakage (1A $\\leftrightarrow$ 2A)',
    equation_labels=('eq:pv_inflation_vs_salem_leakage_algebraic_align_1a2a', 'eq:pv_inflation_vs_salem_leakage_algebraic_equation_1a2a', 'eq:pv_inflation_vs_salem_leakage_calculus_align_1a2a', 'eq:pv_inflation_vs_salem_leakage_calculus_equation_1a2a', 'eq:pv_criterion_leakage_certificate_algebraic_align_1a2a', 'eq:pv_criterion_leakage_certificate_algebraic_equation_1a2a', 'eq:pv_criterion_leakage_certificate_calculus_align_1a2a', 'eq:pv_criterion_leakage_certificate_calculus_equation_1a2a', 'eq:pv_nonpv_dichotomy_algebraic_align_1a2a', 'eq:pv_nonpv_dichotomy_algebraic_equation_1a2a', 'eq:pv_nonpv_dichotomy_calculus_align_1a2a', 'eq:pv_nonpv_dichotomy_calculus_equation_1a2a', 'eq:spectral_decision_test_algebraic_align_1a2a', 'eq:spectral_decision_test_algebraic_equation_1a2a', 'eq:spectral_decision_test_calculus_align_1a2a', 'eq:spectral_decision_test_calculus_equation_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

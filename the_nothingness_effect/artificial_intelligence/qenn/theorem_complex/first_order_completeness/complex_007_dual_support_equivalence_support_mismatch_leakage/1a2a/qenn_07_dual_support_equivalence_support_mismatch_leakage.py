'Authoritative theorem title: QENN 07 -- Dual Support Equivalence $\\leftrightarrow$ Support Mismatch/Leakage.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='qenn::dual_support_equivalence_support_mismatch_leakage',
    role=TheoremRole.CROSS,
    authoritative_title='QENN 07 – Dual Support Equivalence <-> Support Mismatch/Leakage',
    authoritative_title_tex='QENN 07 -- Dual Support Equivalence $\\leftrightarrow$ Support Mismatch/Leakage',
    equation_labels=('eq:dual_support_equivalence_algebraic_align_1a2a', 'eq:dual_support_equivalence_algebraic_equation_1a2a', 'eq:dual_support_equivalence_calculus_align_1a2a', 'eq:dual_support_equivalence_calculus_equation_1a2a', 'eq:window_deconvolution_equivalence_algebraic_align_1a2a', 'eq:window_deconvolution_equivalence_algebraic_equation_1a2a', 'eq:window_deconvolution_equivalence_calculus_align_1a2a', 'eq:window_deconvolution_equivalence_calculus_equation_1a2a', 'eq:dual_equivalence_via_limits_algebraic_align_1a2a', 'eq:dual_equivalence_via_limits_algebraic_equation_1a2a', 'eq:dual_equivalence_via_limits_calculus_align_1a2a', 'eq:dual_equivalence_via_limits_calculus_equation_1a2a', 'eq:golden_test_dual_closure_algebraic_align_1a2a', 'eq:golden_test_dual_closure_algebraic_equation_1a2a', 'eq:golden_test_dual_closure_calculus_align_1a2a', 'eq:golden_test_dual_closure_calculus_equation_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

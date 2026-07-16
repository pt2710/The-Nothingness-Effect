'Authoritative theorem title: Dual Support Equality (1A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='qenn::dual_support_equivalence_support_mismatch_leakage',
    role=TheoremRole.LEFT,
    authoritative_title='Dual Support Equality',
    authoritative_title_tex='Dual Support Equality (1A)',
    equation_labels=('eq:dual_support_equality_algebraic_align_1a', 'eq:dual_support_equality_algebraic_equation_1a', 'eq:dual_support_equality_calculus_align_1a', 'eq:dual_support_equality_calculus_equation_1a', 'eq:window_convolution_concentration_algebraic_align_1a', 'eq:window_convolution_concentration_algebraic_equation_1a', 'eq:window_convolution_concentration_calculus_align_1a', 'eq:window_convolution_concentration_calculus_equation_1a', 'eq:support_convergence_algebraic_align_1a', 'eq:support_convergence_algebraic_equation_1a', 'eq:support_convergence_calculus_align_1a', 'eq:support_convergence_calculus_equation_1a', 'eq:pv_stationarity_algebraic_align_1a', 'eq:pv_stationarity_algebraic_equation_1a', 'eq:pv_stationarity_calculus_align_1a', 'eq:pv_stationarity_calculus_equation_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

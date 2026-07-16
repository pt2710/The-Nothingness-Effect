'Authoritative theorem title: Entropic Screening Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='entropic_screening_nonlocal_curvature_mixing',
    role=TheoremRole.LEFT,
    authoritative_title='Entropic Screening Theorem',
    authoritative_title_tex='Entropic Screening Theorem',
    equation_labels=('eq:ldg07_screening_order_parameter_1a', 'eq:ldg07_screening_branch_condition_1a', 'eq:entropic_screening_operator_1a', 'eq:entropic_screening_yukawa_solution_1a', 'eq:entropic_screening_greens_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

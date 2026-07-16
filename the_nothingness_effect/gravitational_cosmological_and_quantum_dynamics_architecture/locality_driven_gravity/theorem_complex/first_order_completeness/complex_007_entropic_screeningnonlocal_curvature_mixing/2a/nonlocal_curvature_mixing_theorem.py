'Authoritative theorem title: Nonlocal Curvature Mixing Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='entropic_screening_nonlocal_curvature_mixing',
    role=TheoremRole.RIGHT,
    authoritative_title='Nonlocal Curvature Mixing Theorem',
    authoritative_title_tex='Nonlocal Curvature Mixing Theorem',
    equation_labels=('eq:ldg07_screening_order_parameter_2a', 'eq:ldg07_screening_branch_condition_2a', 'eq:nonlocal_mixing_poisson_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

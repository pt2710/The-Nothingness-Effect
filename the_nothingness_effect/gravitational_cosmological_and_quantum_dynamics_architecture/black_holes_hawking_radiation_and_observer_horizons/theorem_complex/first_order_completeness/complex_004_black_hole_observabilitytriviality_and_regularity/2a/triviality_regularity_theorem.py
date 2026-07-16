'Authoritative theorem title: Triviality/Regularity Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='black_hole_observability_triviality_and_regularity',
    role=TheoremRole.RIGHT,
    authoritative_title='Triviality/Regularity Theorem',
    authoritative_title_tex='Triviality/Regularity Theorem',
    equation_labels=('eq:bhhr04_black_hole_observability_order_parameter_2a', 'eq:bhhr04_black_hole_observability_branch_condition_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

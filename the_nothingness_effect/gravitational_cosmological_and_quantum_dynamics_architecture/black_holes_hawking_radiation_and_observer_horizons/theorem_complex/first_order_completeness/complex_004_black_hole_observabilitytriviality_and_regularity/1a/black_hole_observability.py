'Authoritative theorem title: Black Hole Observability.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='black_hole_observability_triviality_and_regularity',
    role=TheoremRole.LEFT,
    authoritative_title='Black Hole Observability',
    authoritative_title_tex='Black Hole Observability',
    equation_labels=('eq:bhhr04_black_hole_observability_order_parameter_1a', 'eq:bhhr04_black_hole_observability_branch_condition_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: No-Horizon / Infinite Visibility Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='observer_horizon_threshold_infinite_visibility',
    role=TheoremRole.RIGHT,
    authoritative_title='No-Horizon / Infinite Visibility Theorem',
    authoritative_title_tex='No-Horizon / Infinite Visibility Theorem',
    equation_labels=('eq:bhhr07_observer_horizon_order_parameter_2a', 'eq:bhhr07_observer_horizon_branch_condition_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

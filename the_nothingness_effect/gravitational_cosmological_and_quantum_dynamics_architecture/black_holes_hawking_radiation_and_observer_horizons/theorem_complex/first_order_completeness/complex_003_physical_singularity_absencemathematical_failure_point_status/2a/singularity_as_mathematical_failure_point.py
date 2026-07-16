'Authoritative theorem title: Singularity as Mathematical Failure Point.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='physical_singularity_absence_mathematical_failure_point_status',
    role=TheoremRole.RIGHT,
    authoritative_title='Singularity as Mathematical Failure Point',
    authoritative_title_tex='Singularity as Mathematical Failure Point',
    equation_labels=('eq:bhhr03_singularity_status_order_parameter_2a', 'eq:bhhr03_singularity_status_branch_condition_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

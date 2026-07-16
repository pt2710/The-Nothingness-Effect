'Authoritative theorem title: No-Memory / Instant Relaxation Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='residual_deformation_memory_perfect_relaxation',
    role=TheoremRole.RIGHT,
    authoritative_title='No-Memory / Instant Relaxation Theorem',
    authoritative_title_tex='No-Memory / Instant Relaxation Theorem',
    equation_labels=('eq:bhhr09_residual_memory_order_parameter_2a', 'eq:bhhr09_residual_memory_branch_condition_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

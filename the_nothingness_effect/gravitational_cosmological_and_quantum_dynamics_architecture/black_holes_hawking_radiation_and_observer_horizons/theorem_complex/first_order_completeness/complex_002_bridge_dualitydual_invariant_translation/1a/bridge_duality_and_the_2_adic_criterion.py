'Authoritative theorem title: Bridge Duality and the 2-adic Criterion.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='bridge_duality_dual_invariant_translation',
    role=TheoremRole.LEFT,
    authoritative_title='Bridge Duality and the 2-adic Criterion',
    authoritative_title_tex='Bridge Duality and the 2-adic Criterion',
    equation_labels=('eq:bhhr02_bridge_duality_order_parameter_1a', 'eq:bhhr02_bridge_duality_branch_condition_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Dual-Invariant Translation Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='bridge_duality_dual_invariant_translation',
    role=TheoremRole.RIGHT,
    authoritative_title='Dual-Invariant Translation Theorem',
    authoritative_title_tex='Dual-Invariant Translation Theorem',
    equation_labels=('eq:bhhr02_bridge_duality_order_parameter_2a', 'eq:bhhr02_bridge_duality_branch_condition_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

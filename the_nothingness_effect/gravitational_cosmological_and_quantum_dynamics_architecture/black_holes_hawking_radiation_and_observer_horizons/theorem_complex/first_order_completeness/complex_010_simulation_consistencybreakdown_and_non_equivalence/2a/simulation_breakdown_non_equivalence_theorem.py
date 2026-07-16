'Authoritative theorem title: Simulation Breakdown/Non-Equivalence Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='simulation_consistency_breakdown_and_non_equivalence',
    role=TheoremRole.RIGHT,
    authoritative_title='Simulation Breakdown/Non-Equivalence Theorem',
    authoritative_title_tex='Simulation Breakdown/Non-Equivalence Theorem',
    equation_labels=('eq:bhhr10_simulation_consistency_order_parameter_2a', 'eq:bhhr10_simulation_consistency_branch_condition_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

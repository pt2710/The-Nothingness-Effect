'Authoritative theorem title: Simulation Breakdown/Non-Equivalence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_simulation_consistency_and_simulation_breakdown_non_equivalence',
    role=TheoremRole.RIGHT,
    authoritative_title='Simulation Breakdown/Non-Equivalence',
    authoritative_title_tex='Simulation Breakdown/Non-Equivalence',
    equation_labels=('eq:elastic_pi04_breakdown_statuses_2a', 'eq:elastic_pi04_range_threshold_2a', 'eq:elastic_pi04_synthesis_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

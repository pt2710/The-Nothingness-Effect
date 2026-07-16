'Authoritative theorem title: Collapse Inaccessibility.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='observable_locality_and_collapse_inaccessibility',
    role=TheoremRole.RIGHT,
    authoritative_title='Collapse Inaccessibility',
    authoritative_title_tex='Collapse Inaccessibility',
    equation_labels=('eq:obs10_locality_defect_vector_2c', 'eq:obs10_region_reach_defect_2c', 'eq:obs10_inaccessible_region_condition_2c', 'eq:obs10_synthesis_2c', 'eq:std_obs10_principle_2c'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

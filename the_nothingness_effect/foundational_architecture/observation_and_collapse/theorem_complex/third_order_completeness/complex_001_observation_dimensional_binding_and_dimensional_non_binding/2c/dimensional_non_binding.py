'Authoritative theorem title: Dimensional Non-Binding.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='observation_dimensional_binding_and_dimensional_non_binding',
    role=TheoremRole.RIGHT,
    authoritative_title='Dimensional Non-Binding',
    authoritative_title_tex='Dimensional Non-Binding',
    equation_labels=('eq:obs06_nonbinding_vector_2c', 'eq:obs06_source_defect_2c', 'eq:obs06_commutator_defect_2c', 'eq:obs06_projection_defect_2c', 'eq:obs06_fixed_core_defect_2c', 'eq:obs06_composition_failure_2c', 'eq:obs06_noncommuting_example_2c', 'eq:obs06_nonprojection_product_2c', 'eq:obs06_synthesis_2c', 'eq:std_obs06_principle_2c'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Flat Schedule-Controlled Reciprocal Transport.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='schedule_controlled_orbit_transport',
    role=TheoremRole.LEFT,
    authoritative_title='Flat Schedule-Controlled Reciprocal Transport',
    authoritative_title_tex='Flat Schedule-Controlled Reciprocal Transport',
    equation_labels=('eq:symmetry_transport_definition_1b', 'eq:symmetry_transport_path_1b', 'eq:symmetry_transport_cocycle_law_1b', 'eq:symmetry_transport_functor_law_1b', 'eq:symmetry_transport_local_update_1b', 'eq:symmetry_transport_prefix_locality_1b', 'eq:symmetry_transport_eventual_stabilization_1b', 'eq:symmetry_transport_principle_1b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

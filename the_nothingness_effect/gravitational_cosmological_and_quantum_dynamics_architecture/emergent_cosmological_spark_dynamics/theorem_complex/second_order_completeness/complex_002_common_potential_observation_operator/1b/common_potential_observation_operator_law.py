'Authoritative theorem title: Common-Potential Observation Operator Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='common_potential_observation_operator',
    role=TheoremRole.LEFT,
    authoritative_title='Common-Potential Observation Operator Law',
    authoritative_title_tex='Common-Potential Observation Operator Law',
    equation_labels=('eq:sc06_geometry_wave_state_1b', 'eq:sc06_geometry_wave_chain_1b', 'eq:sc06_geometry_wave_bound_1b', 'eq:sc06_geometry_wave_residual_1b', 'eq:sc06_geometry_wave_synthesis_1b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Complete Common-Potential Observation Operator Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='common_potential_observation_operator',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Common-Potential Observation Operator Classification',
    authoritative_title_tex='Complete Common-Potential Observation Operator Classification',
    equation_labels=('eq:sc06_source_complexes_1b2b', 'eq:sc06_joint_system_1b2b', 'eq:sc06_explicit_b_composition_1b2b', 'eq:sc06_branch_exchange_1b2b', 'eq:sc06_combined_residual_1b2b', 'eq:sc06_joint_synthesis_1b2b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

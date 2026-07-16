'Authoritative theorem title: Exact Perturbation Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='collapse_attractor_stability_and_attractor_instability',
    role=TheoremRole.CROSS,
    authoritative_title='Exact Perturbation Classification',
    authoritative_title_tex='Exact Perturbation Classification',
    equation_labels=('eq:obs02_canonical_observation_collapse_1a2a', 'eq:obs02_canonical_attractor_assignment_1a2a', 'eq:obs02_average_definition_1a2a', 'eq:obs02_average_linearity_1a2a', 'eq:obs02_response_map_1a2a', 'eq:obs02_cluster_translation_1a2a', 'eq:obs02_joint_response_map_1a2a', 'eq:std_obs02_principle_joint'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

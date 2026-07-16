'Authoritative theorem title: Complete Uniqueness Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='uniqueness_and_non_uniqueness_of_collapse',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Uniqueness Classification',
    authoritative_title_tex='Complete Uniqueness Classification',
    equation_labels=('eq:obs03_canonical_observation_collapse_1a2a', 'eq:obs03_family_averages_1a2a', 'eq:obs03_cluster_set_1a2a', 'eq:obs03_profile_1a2a', 'eq:obs03_singleton_criterion_1a2a', 'eq:obs03_cluster_classification_corollary_1a2a', 'eq:obs03_joint_uniqueness_status_1a2a', 'eq:std_obs03_principle_joint'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

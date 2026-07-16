'Authoritative theorem title: SOI Entropy Integrability Classification Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='entropy_density_mapping_and_entropy_divergence',
    role=TheoremRole.CROSS,
    authoritative_title='SOI Entropy Integrability Classification Theorem',
    authoritative_title_tex='SOI Entropy Integrability Classification Theorem',
    equation_labels=('eq:soi_entropy_original_soi_1a2a', 'eq:soi_entropy_measure_scaling_1a2a', 'eq:soi_entropy_pushforward_pair_1a2a', 'eq:std_soi_entropy_joint', 'eq:soi_entropy_absolute_scale_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

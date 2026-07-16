'Authoritative theorem title: Non-Locality Divergence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='local_horizon_boundary_and_non_locality_divergence',
    role=TheoremRole.RIGHT,
    authoritative_title='Non-Locality Divergence',
    authoritative_title_tex='Non-Locality Divergence',
    equation_labels=('eq:obs12_nonuniform_tightness_2c', 'eq:obs12_infinite_family_horizon_2c', 'eq:obs12_translating_bump_sequence_2c', 'eq:obs12_translating_horizon_divergence_2c', 'eq:obs12_synthesis_2c', 'eq:std_obs12_principle_2c'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

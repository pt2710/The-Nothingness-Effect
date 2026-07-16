'Authoritative theorem title: Entropy Divergence Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='entropy_density_mapping_and_entropy_divergence',
    role=TheoremRole.RIGHT,
    authoritative_title='Entropy Divergence Theorem',
    authoritative_title_tex='Entropy Divergence Theorem',
    equation_labels=('eq:std_soi_entropy_boundary_2a',),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

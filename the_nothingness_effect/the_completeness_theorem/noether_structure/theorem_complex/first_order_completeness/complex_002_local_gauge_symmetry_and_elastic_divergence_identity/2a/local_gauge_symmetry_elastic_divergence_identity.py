'Authoritative theorem title: Local Gauge Symmetry \\(\\Longrightarrow\\) Elastic Divergence Identity.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='local_gauge_symmetry_and_elastic_divergence_identity',
    role=TheoremRole.RIGHT,
    authoritative_title='Local Gauge Symmetry Elastic Divergence Identity',
    authoritative_title_tex='Local Gauge Symmetry \\(\\Longrightarrow\\) Elastic Divergence Identity',
    equation_labels=('eq:noether_local_predicate_2a', 'eq:noether_local_identity_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

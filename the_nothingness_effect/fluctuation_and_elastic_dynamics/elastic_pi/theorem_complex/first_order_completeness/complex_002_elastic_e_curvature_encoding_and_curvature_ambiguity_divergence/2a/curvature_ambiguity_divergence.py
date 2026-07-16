'Authoritative theorem title: Curvature Ambiguity/Divergence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_e_curvature_encoding_and_curvature_ambiguity_divergence',
    role=TheoremRole.RIGHT,
    authoritative_title='Curvature Ambiguity/Divergence',
    authoritative_title_tex='Curvature Ambiguity/Divergence',
    equation_labels=('eq:elastic_pi02_divergence_witness_2a', 'eq:curvature_divergence_2a', 'eq:pi_collapse_2a', 'eq:elastic_pi02_log_laplacian_map_2a', 'eq:elastic_pi02_synthesis_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

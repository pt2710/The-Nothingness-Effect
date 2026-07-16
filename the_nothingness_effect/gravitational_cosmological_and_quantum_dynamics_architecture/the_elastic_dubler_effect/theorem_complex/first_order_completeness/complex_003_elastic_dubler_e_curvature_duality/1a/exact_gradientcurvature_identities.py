'Authoritative theorem title: Exact Gradient--Curvature Identities.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_dubler_e_curvature_duality',
    role=TheoremRole.LEFT,
    authoritative_title='Exact Gradient–Curvature Identities',
    authoritative_title_tex='Exact Gradient--Curvature Identities',
    equation_labels=('eq:ed03_log_field_1a', 'eq:ed03_log_curvature_1a', 'eq:ed03_gradient_identity_1a', 'eq:ed03_laplacian_identity_1a', 'eq:ed03_proxy_lemma_1a', 'eq:ed03_one_dimensional_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

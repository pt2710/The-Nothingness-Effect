'Authoritative theorem title: Elastic-$\\pi$ Invariance of Support.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_invariance_of_support_nonlinear_leakage',
    role=TheoremRole.LEFT,
    authoritative_title='Elastic-pi Invariance of Support',
    authoritative_title_tex='Elastic-$\\pi$ Invariance of Support',
    equation_labels=('eq:epsi_support_preservation_1a', 'eq:epsi_support_preservation_calculus_1a', 'eq:epsi_indicator_projection_1a', 'eq:epsi_projection_test_function_1a', 'eq:epsi_projection_argument_1a', 'eq:epsi_energy_scale_1a', 'eq:epsi_parseval_scale_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

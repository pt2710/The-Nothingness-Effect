'Authoritative theorem title: SOI Cross-Domain Generalization (1A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='soi_cross_domain_generalization_and_collapse',
    role=TheoremRole.LEFT,
    authoritative_title='SOI Cross-Domain Generalization',
    authoritative_title_tex='SOI Cross-Domain Generalization (1A)',
    equation_labels=('eq:soi_generalization_algebraic_1a', 'eq:soi_generalization_calculus_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

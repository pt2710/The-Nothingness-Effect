'Authoritative theorem title: SOI Cross-Domain Collapse (2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='soi_cross_domain_generalization_and_collapse',
    role=TheoremRole.RIGHT,
    authoritative_title='SOI Cross-Domain Collapse',
    authoritative_title_tex='SOI Cross-Domain Collapse (2A)',
    equation_labels=('eq:soi_collapse_algebraic_2a', 'eq:soi_collapse_calculus_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

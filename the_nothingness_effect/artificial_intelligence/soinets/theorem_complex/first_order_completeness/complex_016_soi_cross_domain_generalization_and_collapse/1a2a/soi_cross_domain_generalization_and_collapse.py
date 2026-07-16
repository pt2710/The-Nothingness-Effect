'Authoritative theorem title: SOI Cross-Domain Generalization and Collapse (1A $\\longleftrightarrow$ 2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='soi_cross_domain_generalization_and_collapse',
    role=TheoremRole.CROSS,
    authoritative_title='SOI Cross-Domain Generalization and Collapse',
    authoritative_title_tex='SOI Cross-Domain Generalization and Collapse (1A $\\longleftrightarrow$ 2A)',
    equation_labels=('eq:soi_crossdomain_generalization_1a2a', 'eq:soi_crossdomain_collapse_1a2a', 'eq:soi_crossdomain_deriv_bounded_1a2a', 'eq:soi_crossdomain_deriv_unbounded_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

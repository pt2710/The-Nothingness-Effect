'Authoritative theorem title: Domain-Specific Calibration Defect.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='universal_domain_specific_k_d_duality',
    role=TheoremRole.RIGHT,
    authoritative_title='Domain-Specific Calibration Defect',
    authoritative_title_tex='Domain-Specific Calibration Defect',
    equation_labels=('eq:ed16_dispersion_2a', 'eq:ed16_universal_iff_2a', 'eq:ed16_cross_domain_defect_2a', 'eq:ed16_product_rule_2a', 'eq:ed16_geometric_mean_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Heterogeneity Produces a Nonzero Calibrated Shift.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='spatial_homogeneity_heterogeneity_duality',
    role=TheoremRole.LEFT,
    authoritative_title='Heterogeneity Produces a Nonzero Calibrated Shift',
    authoritative_title_tex='Heterogeneity Produces a Nonzero Calibrated Shift',
    equation_labels=('eq:ed15_heterogeneity_1a', 'eq:ed15_response_coercivity_1a', 'eq:ed15_heterogeneity_shift_1a', 'eq:ed15_constancy_lemma_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Absolute Infinity Paradox.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='finitizable_infinity_and_the_non_finitization_boundary',
    role=TheoremRole.RIGHT,
    authoritative_title='Absolute Infinity Paradox',
    authoritative_title_tex='Absolute Infinity Paradox',
    equation_labels=('eq:std_soi_approx_domain_2a',),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

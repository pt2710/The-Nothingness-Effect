'Authoritative theorem title: Duality of Infinite/Finitizable Structure.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='finitizable_infinity_and_the_non_finitization_boundary',
    role=TheoremRole.LEFT,
    authoritative_title='Duality of Infinite/Finitizable Structure',
    authoritative_title_tex='Duality of Infinite/Finitizable Structure',
    equation_labels=('eq:soi_finitization_relative_absolute_integrals_1a', 'eq:soi_finitization_absolute_error_1a', 'eq:std_soi_finitization_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

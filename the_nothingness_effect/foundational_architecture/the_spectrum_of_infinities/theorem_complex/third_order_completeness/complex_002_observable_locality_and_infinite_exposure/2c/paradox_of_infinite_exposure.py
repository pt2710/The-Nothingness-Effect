'Authoritative theorem title: Paradox of Infinite Exposure.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='observable_locality_and_infinite_exposure',
    role=TheoremRole.RIGHT,
    authoritative_title='Paradox of Infinite Exposure',
    authoritative_title_tex='Paradox of Infinite Exposure',
    equation_labels=('eq:soi12_negative_b_composition_2c', 'eq:soi12_partial_sum_2c', 'eq:std_soi12_synthesis_2c', 'eq:std_soi12_exposure_2c'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

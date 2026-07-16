'Authoritative theorem title: Flat-Field Nullification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_dubler_e_curvature_duality',
    role=TheoremRole.RIGHT,
    authoritative_title='Flat-Field Nullification',
    authoritative_title_tex='Flat-Field Nullification',
    equation_labels=('eq:ed03_null_flat_definition_2a', 'eq:ed03_flat_nullification_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Two-Sheeted Reciprocity Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='reciprocal_orbit_double_cover',
    role=TheoremRole.LEFT,
    authoritative_title='Two-Sheeted Reciprocity Law',
    authoritative_title_tex='Two-Sheeted Reciprocity Law',
    equation_labels=('eq:drv_duality_b01_1b',),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

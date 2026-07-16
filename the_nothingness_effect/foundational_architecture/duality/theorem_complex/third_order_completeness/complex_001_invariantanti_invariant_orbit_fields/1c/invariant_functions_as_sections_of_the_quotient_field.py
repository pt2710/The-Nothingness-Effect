'Authoritative theorem title: Invariant Functions as Sections of the Quotient Field.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='invariant_anti_invariant_orbit_fields',
    role=TheoremRole.LEFT,
    authoritative_title='Invariant Functions as Sections of the Quotient Field',
    authoritative_title_tex='Invariant Functions as Sections of the Quotient Field',
    equation_labels=('eq:drv_duality_c01_1c', 'eq:drv_duality_c01_theorem_1c'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

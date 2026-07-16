'Authoritative theorem title: Anti-Invariant Functions as Sections of the Sign Field.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='invariant_anti_invariant_orbit_fields',
    role=TheoremRole.RIGHT,
    authoritative_title='Anti-Invariant Functions as Sections of the Sign Field',
    authoritative_title_tex='Anti-Invariant Functions as Sections of the Sign Field',
    equation_labels=('eq:drv_duality_c01_2c', 'eq:drv_duality_c01_theorem_2c'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

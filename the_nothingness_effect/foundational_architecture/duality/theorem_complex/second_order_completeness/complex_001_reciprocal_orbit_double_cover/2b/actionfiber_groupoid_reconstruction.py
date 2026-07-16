'Authoritative theorem title: Action--Fiber Groupoid Reconstruction.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='reciprocal_orbit_double_cover',
    role=TheoremRole.RIGHT,
    authoritative_title='Action–Fiber Groupoid Reconstruction',
    authoritative_title_tex='Action--Fiber Groupoid Reconstruction',
    equation_labels=('eq:drv_duality_b01_2b',),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

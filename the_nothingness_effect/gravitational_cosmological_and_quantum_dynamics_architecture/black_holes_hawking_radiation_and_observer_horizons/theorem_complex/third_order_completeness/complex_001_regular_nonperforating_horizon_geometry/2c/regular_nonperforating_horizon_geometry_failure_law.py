'Authoritative theorem title: Regular Nonperforating Horizon Geometry Failure Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='regular_nonperforating_horizon_geometry',
    role=TheoremRole.RIGHT,
    authoritative_title='Regular Nonperforating Horizon Geometry Failure Law',
    authoritative_title_tex='Regular Nonperforating Horizon Geometry Failure Law',
    equation_labels=('eq:drv_bhhr_c01_2c', 'eq:drv_bhhr_c01_res_2c'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

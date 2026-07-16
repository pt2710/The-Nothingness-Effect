'Authoritative theorem title: Regular Nonperforating Horizon Geometry Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='regular_nonperforating_horizon_geometry',
    role=TheoremRole.LEFT,
    authoritative_title='Regular Nonperforating Horizon Geometry Law',
    authoritative_title_tex='Regular Nonperforating Horizon Geometry Law',
    equation_labels=('eq:drv_bhhr_c01_1c', 'eq:drv_bhhr_c01_theorem_1c', 'eq:drv_bhhr_c01_res_1c'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

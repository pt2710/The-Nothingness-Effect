'Authoritative theorem title: Complete Regular Nonperforating Horizon Geometry Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='regular_nonperforating_horizon_geometry',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Regular Nonperforating Horizon Geometry Classification',
    authoritative_title_tex='Complete Regular Nonperforating Horizon Geometry Classification',
    equation_labels=('eq:drv_bhhr_c01_spatial_carrier', 'eq:drv_bhhr_c01_joint', 'eq:drv_bhhr_c01_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

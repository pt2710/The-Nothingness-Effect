'Authoritative theorem title: Complete Screened Rotation-Halo Geometry Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='screened_rotation_halo_geometry',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Screened Rotation-Halo Geometry Classification',
    authoritative_title_tex='Complete Screened Rotation-Halo Geometry Classification',
    equation_labels=('eq:drv_ldg_c02_spatial_carrier', 'eq:drv_ldg_c02_joint', 'eq:drv_ldg_c02_exchange_square'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

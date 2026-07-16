'Authoritative theorem title: Screened Rotation-Halo Geometry Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='screened_rotation_halo_geometry',
    role=TheoremRole.LEFT,
    authoritative_title='Screened Rotation-Halo Geometry Law',
    authoritative_title_tex='Screened Rotation-Halo Geometry Law',
    equation_labels=('eq:drv_ldg_c02_1c', 'eq:drv_ldg_c02_theorem_1c', 'eq:drv_ldg_c02_res_1c'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

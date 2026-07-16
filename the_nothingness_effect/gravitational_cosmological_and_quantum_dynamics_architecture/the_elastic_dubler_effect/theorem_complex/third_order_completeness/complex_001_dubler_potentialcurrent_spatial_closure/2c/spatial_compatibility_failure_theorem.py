'Authoritative theorem title: Spatial Compatibility Failure Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dubler_potential_current_spatial_closure',
    role=TheoremRole.RIGHT,
    authoritative_title='Spatial Compatibility Failure Theorem',
    authoritative_title_tex='Spatial Compatibility Failure Theorem',
    equation_labels=('eq:drv_dubler_c01_2c', 'eq:drv_dubler_c01_theorem_2c', 'eq:drv_dubler_c01_res_2c'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

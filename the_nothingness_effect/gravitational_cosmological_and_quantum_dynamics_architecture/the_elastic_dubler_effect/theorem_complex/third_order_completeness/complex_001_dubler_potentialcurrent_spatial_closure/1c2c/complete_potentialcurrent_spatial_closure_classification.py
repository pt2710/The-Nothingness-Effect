'Authoritative theorem title: Complete Potential--Current Spatial Closure Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dubler_potential_current_spatial_closure',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Potential–Current Spatial Closure Classification',
    authoritative_title_tex='Complete Potential--Current Spatial Closure Classification',
    equation_labels=('eq:drv_dubler_c01_spatial_carrier', 'eq:drv_dubler_c01_joint', 'eq:drv_dubler_c01_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

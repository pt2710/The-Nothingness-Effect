'Authoritative theorem title: Potential--Current Connection Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dubler_potential_current_spatial_closure',
    role=TheoremRole.LEFT,
    authoritative_title='Potential–Current Connection Theorem',
    authoritative_title_tex='Potential--Current Connection Theorem',
    equation_labels=('eq:drv_dubler_c01_1c', 'eq:drv_dubler_c01_theorem_1c', 'eq:drv_dubler_c01_res_1c'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

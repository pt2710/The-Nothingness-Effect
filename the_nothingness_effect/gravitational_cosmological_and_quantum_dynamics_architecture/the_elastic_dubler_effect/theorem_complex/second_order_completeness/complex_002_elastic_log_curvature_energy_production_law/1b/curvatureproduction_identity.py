'Authoritative theorem title: Curvature--Production Identity.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_log_curvature_energy_production_law',
    role=TheoremRole.LEFT,
    authoritative_title='Curvature–Production Identity',
    authoritative_title_tex='Curvature--Production Identity',
    equation_labels=('eq:drv_dubler_b02_1b', 'eq:drv_dubler_b02_theorem_1b', 'eq:drv_dubler_b02_res_1b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

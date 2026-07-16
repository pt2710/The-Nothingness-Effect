'Authoritative theorem title: Confined Filament Persistence Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='confined_filament_persistence',
    role=TheoremRole.LEFT,
    authoritative_title='Confined Filament Persistence Law',
    authoritative_title_tex='Confined Filament Persistence Law',
    equation_labels=('eq:drv_ldg_b05_1b', 'eq:drv_ldg_b05_theorem_1b', 'eq:drv_ldg_b05_res_1b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

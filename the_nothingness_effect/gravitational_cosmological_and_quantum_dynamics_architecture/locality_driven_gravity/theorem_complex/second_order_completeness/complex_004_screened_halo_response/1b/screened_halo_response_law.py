'Authoritative theorem title: Screened Halo Response Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='screened_halo_response',
    role=TheoremRole.LEFT,
    authoritative_title='Screened Halo Response Law',
    authoritative_title_tex='Screened Halo Response Law',
    equation_labels=('eq:drv_ldg_b04_1b', 'eq:drv_ldg_b04_theorem_1b', 'eq:drv_ldg_b04_res_1b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

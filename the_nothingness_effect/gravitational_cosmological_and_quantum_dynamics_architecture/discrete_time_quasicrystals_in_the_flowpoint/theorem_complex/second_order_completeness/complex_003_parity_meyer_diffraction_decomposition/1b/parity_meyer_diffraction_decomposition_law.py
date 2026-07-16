'Authoritative theorem title: Parity-Meyer Diffraction Decomposition Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='parity_meyer_diffraction_decomposition',
    role=TheoremRole.LEFT,
    authoritative_title='Parity-Meyer Diffraction Decomposition Law',
    authoritative_title_tex='Parity-Meyer Diffraction Decomposition Law',
    equation_labels=('eq:drv_dtqc_b03_1b', 'eq:drv_dtqc_b03_theorem_1b', 'eq:drv_dtqc_b03_res_1b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

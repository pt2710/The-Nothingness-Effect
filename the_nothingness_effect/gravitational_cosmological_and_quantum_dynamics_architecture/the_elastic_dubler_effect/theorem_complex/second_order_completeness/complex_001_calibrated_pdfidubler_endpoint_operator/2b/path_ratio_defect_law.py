'Authoritative theorem title: Path/Ratio Defect Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='calibrated_pdfi_dubler_endpoint_operator',
    role=TheoremRole.RIGHT,
    authoritative_title='Path/Ratio Defect Law',
    authoritative_title_tex='Path/Ratio Defect Law',
    equation_labels=('eq:drv_dubler_b01_2b', 'eq:drv_dubler_b01_theorem_2b', 'eq:drv_dubler_b01_res_2b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

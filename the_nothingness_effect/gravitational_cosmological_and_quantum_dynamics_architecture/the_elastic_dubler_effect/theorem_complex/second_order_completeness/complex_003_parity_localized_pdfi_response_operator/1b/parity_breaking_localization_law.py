'Authoritative theorem title: Parity-Breaking Localization Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='parity_localized_pdfi_response_operator',
    role=TheoremRole.LEFT,
    authoritative_title='Parity-Breaking Localization Law',
    authoritative_title_tex='Parity-Breaking Localization Law',
    equation_labels=('eq:drv_dubler_b03_1b', 'eq:drv_dubler_b03_theorem_1b', 'eq:drv_dubler_b03_res_1b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

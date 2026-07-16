'Authoritative theorem title: Parity-Localized Failure Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='parity_localized_pdfi_response_operator',
    role=TheoremRole.RIGHT,
    authoritative_title='Parity-Localized Failure Law',
    authoritative_title_tex='Parity-Localized Failure Law',
    equation_labels=('eq:drv_dubler_b03_2b', 'eq:drv_dubler_b03_theorem_2b', 'eq:drv_dubler_b03_res_2b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

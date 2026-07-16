'Authoritative theorem title: Complete pDFI--Dubler Endpoint Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='calibrated_pdfi_dubler_endpoint_operator',
    role=TheoremRole.CROSS,
    authoritative_title='Complete pDFI–Dubler Endpoint Classification',
    authoritative_title_tex='Complete pDFI--Dubler Endpoint Classification',
    equation_labels=('eq:drv_dubler_b01_product_carrier', 'eq:drv_dubler_b01_joint', 'eq:drv_dubler_b01_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

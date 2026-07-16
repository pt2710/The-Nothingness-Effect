'Authoritative theorem title: Parity-Definite and Parity-Indeterminate Classification -- Flowpoint--Parity Correspondence and Decoupling.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='parity_flowpoint_transport_law',
    role=TheoremRole.CROSS,
    authoritative_title='Parity-Definite and Parity-Indeterminate Classification – Flowpoint–Parity Correspondence and Decoupling',
    authoritative_title_tex='Parity-Definite and Parity-Indeterminate Classification -- Flowpoint--Parity Correspondence and Decoupling',
    equation_labels=('eq:drv_pdfi_b01_product_carrier', 'eq:drv_pdfi_b01_joint', 'eq:drv_pdfi_b01_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

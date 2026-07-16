'Authoritative theorem title: Complete DFI Existence Classification -- Exact DFI Transformation Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='scale_normalized_dfi_homogeneity_invariant',
    role=TheoremRole.CROSS,
    authoritative_title='Complete DFI Existence Classification – Exact DFI Transformation Classification',
    authoritative_title_tex='Complete DFI Existence Classification -- Exact DFI Transformation Classification',
    equation_labels=('eq:drv_dfi_b01_product_carrier', 'eq:drv_dfi_b01_joint', 'eq:drv_dfi_b01_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Complete Memory--Horizon Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='memory_resolved_horizon_reconstruction',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Memory–Horizon Classification',
    authoritative_title_tex='Complete Memory--Horizon Classification',
    equation_labels=('eq:drv_edi_b02_product_carrier', 'eq:drv_edi_b02_joint', 'eq:drv_edi_b02_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

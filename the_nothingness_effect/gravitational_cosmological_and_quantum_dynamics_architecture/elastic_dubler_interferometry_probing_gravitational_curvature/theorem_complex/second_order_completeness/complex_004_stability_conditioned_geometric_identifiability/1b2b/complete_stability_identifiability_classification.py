'Authoritative theorem title: Complete Stability-Identifiability Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='stability_conditioned_geometric_identifiability',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Stability-Identifiability Classification',
    authoritative_title_tex='Complete Stability-Identifiability Classification',
    equation_labels=('eq:drv_edi_b04_product_carrier', 'eq:drv_edi_b04_joint', 'eq:drv_edi_b04_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

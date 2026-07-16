'Authoritative theorem title: Exact Update--Defect Equivalence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='outcome_conditioned_closure_instrument',
    role=TheoremRole.CROSS,
    authoritative_title='Exact Update–Defect Equivalence',
    authoritative_title_tex='Exact Update--Defect Equivalence',
    equation_labels=('eq:drv_oac_b01_product_carrier', 'eq:drv_oac_b01_joint', 'eq:drv_oac_b01_exchange_square'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

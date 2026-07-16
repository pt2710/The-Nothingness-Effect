'Authoritative theorem title: Complete Locality-Weighted Spiral Order Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='locality_weighted_spiral_order',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Locality-Weighted Spiral Order Classification',
    authoritative_title_tex='Complete Locality-Weighted Spiral Order Classification',
    equation_labels=('eq:drv_ldg_b01_product_carrier', 'eq:drv_ldg_b01_joint', 'eq:drv_ldg_b01_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

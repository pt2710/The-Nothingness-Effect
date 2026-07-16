'Authoritative theorem title: Complete Spatiotemporal Hawking-Flux Density Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='spatiotemporal_hawking_flux_density',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Spatiotemporal Hawking-Flux Density Classification',
    authoritative_title_tex='Complete Spatiotemporal Hawking-Flux Density Classification',
    equation_labels=('eq:drv_bhhr_b03_product_carrier', 'eq:drv_bhhr_b03_joint', 'eq:drv_bhhr_b03_exchange_square'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

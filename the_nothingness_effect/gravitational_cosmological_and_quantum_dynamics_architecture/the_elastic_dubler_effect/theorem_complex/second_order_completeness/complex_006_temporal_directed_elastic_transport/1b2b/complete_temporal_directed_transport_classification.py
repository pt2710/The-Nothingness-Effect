'Authoritative theorem title: Complete Temporal Directed Transport Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='temporal_directed_elastic_transport',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Temporal Directed Transport Classification',
    authoritative_title_tex='Complete Temporal Directed Transport Classification',
    equation_labels=('eq:drv_dubler_b06_product_carrier', 'eq:drv_dubler_b06_joint', 'eq:drv_dubler_b06_exchange_square'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

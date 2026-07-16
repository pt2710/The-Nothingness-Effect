'Authoritative theorem title: Complete Observable Conserved Directed Transport Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='observable_conserved_directed_transport_closure',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Observable Conserved Directed Transport Classification',
    authoritative_title_tex='Complete Observable Conserved Directed Transport Classification',
    equation_labels=('eq:drv_dubler_c03_spatial_carrier', 'eq:drv_dubler_c03_joint', 'eq:drv_dubler_c03_exchange_square'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

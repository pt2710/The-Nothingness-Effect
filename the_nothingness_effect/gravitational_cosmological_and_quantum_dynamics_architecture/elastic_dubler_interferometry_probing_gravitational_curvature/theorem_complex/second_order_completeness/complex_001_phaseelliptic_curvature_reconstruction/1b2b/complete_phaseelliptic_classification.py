'Authoritative theorem title: Complete Phase--Elliptic Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='phase_elliptic_curvature_reconstruction',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Phase–Elliptic Classification',
    authoritative_title_tex='Complete Phase--Elliptic Classification',
    equation_labels=('eq:drv_edi_b01_product_carrier', 'eq:drv_edi_b01_joint', 'eq:drv_edi_b01_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

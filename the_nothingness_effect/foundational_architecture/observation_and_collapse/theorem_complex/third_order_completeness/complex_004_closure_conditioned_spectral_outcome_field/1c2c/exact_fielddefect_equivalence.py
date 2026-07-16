'Authoritative theorem title: Exact Field--Defect Equivalence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='closure_conditioned_spectral_outcome_field',
    role=TheoremRole.CROSS,
    authoritative_title='Exact Field–Defect Equivalence',
    authoritative_title_tex='Exact Field--Defect Equivalence',
    equation_labels=('eq:drv_oac_c01_spatial_carrier', 'eq:drv_oac_c01_joint', 'eq:drv_oac_c01_exchange_square'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

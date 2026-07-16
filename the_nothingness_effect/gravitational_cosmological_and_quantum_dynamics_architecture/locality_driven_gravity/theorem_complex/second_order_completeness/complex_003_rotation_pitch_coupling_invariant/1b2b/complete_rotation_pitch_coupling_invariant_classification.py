'Authoritative theorem title: Complete Rotation-Pitch Coupling Invariant Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='rotation_pitch_coupling_invariant',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Rotation-Pitch Coupling Invariant Classification',
    authoritative_title_tex='Complete Rotation-Pitch Coupling Invariant Classification',
    equation_labels=('eq:drv_ldg_b03_product_carrier', 'eq:drv_ldg_b03_joint', 'eq:drv_ldg_b03_exchange_square'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

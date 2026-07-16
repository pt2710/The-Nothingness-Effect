'Authoritative theorem title: Norm--Seminorm Domain Dichotomy -- Weight Regularity Dichotomy.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='weighted_path_ratio_regularity_functional',
    role=TheoremRole.CROSS,
    authoritative_title='Norm–Seminorm Domain Dichotomy – Weight Regularity Dichotomy',
    authoritative_title_tex='Norm--Seminorm Domain Dichotomy -- Weight Regularity Dichotomy',
    equation_labels=('eq:drv_epinorm_b01_product_carrier', 'eq:drv_epinorm_b01_joint', 'eq:drv_epinorm_b01_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

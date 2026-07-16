'Authoritative theorem title: Complete Regular Observer-Horizon Hypersurface Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='regular_observer_horizon_hypersurface',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Regular Observer-Horizon Hypersurface Classification',
    authoritative_title_tex='Complete Regular Observer-Horizon Hypersurface Classification',
    equation_labels=('eq:drv_bhhr_b02_product_carrier', 'eq:drv_bhhr_b02_joint', 'eq:drv_bhhr_b02_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

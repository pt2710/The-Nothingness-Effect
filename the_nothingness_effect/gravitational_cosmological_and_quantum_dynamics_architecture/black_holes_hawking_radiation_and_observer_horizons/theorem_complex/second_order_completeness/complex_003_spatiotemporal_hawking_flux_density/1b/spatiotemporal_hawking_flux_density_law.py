'Authoritative theorem title: Spatiotemporal Hawking-Flux Density Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='spatiotemporal_hawking_flux_density',
    role=TheoremRole.LEFT,
    authoritative_title='Spatiotemporal Hawking-Flux Density Law',
    authoritative_title_tex='Spatiotemporal Hawking-Flux Density Law',
    equation_labels=('eq:drv_bhhr_b03_1b', 'eq:drv_bhhr_b03_theorem_1b', 'eq:drv_bhhr_b03_res_1b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

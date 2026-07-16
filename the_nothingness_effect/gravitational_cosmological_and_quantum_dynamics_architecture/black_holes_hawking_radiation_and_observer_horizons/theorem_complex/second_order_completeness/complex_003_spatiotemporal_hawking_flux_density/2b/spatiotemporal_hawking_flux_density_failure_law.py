'Authoritative theorem title: Spatiotemporal Hawking-Flux Density Failure Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='spatiotemporal_hawking_flux_density',
    role=TheoremRole.RIGHT,
    authoritative_title='Spatiotemporal Hawking-Flux Density Failure Law',
    authoritative_title_tex='Spatiotemporal Hawking-Flux Density Failure Law',
    equation_labels=('eq:drv_bhhr_b03_2b', 'eq:drv_bhhr_b03_theorem_2b', 'eq:drv_bhhr_b03_res_2b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Locality-Weighted Spiral Order Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='locality_weighted_spiral_order',
    role=TheoremRole.LEFT,
    authoritative_title='Locality-Weighted Spiral Order Law',
    authoritative_title_tex='Locality-Weighted Spiral Order Law',
    equation_labels=('eq:drv_ldg_b01_1b', 'eq:drv_ldg_b01_theorem_1b', 'eq:drv_ldg_b01_res_1b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

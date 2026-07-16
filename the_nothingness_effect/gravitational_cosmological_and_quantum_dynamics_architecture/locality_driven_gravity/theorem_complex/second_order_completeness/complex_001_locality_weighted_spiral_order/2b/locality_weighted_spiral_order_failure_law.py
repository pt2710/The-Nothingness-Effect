'Authoritative theorem title: Locality-Weighted Spiral Order Failure Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='locality_weighted_spiral_order',
    role=TheoremRole.RIGHT,
    authoritative_title='Locality-Weighted Spiral Order Failure Law',
    authoritative_title_tex='Locality-Weighted Spiral Order Failure Law',
    equation_labels=('eq:drv_ldg_b01_2b', 'eq:drv_ldg_b01_theorem_2b', 'eq:drv_ldg_b01_res_2b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

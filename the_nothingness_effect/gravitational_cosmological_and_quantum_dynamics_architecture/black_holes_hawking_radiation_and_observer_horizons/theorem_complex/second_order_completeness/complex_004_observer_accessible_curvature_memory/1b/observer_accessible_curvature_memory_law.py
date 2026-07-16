'Authoritative theorem title: Observer-Accessible Curvature Memory Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='observer_accessible_curvature_memory',
    role=TheoremRole.LEFT,
    authoritative_title='Observer-Accessible Curvature Memory Law',
    authoritative_title_tex='Observer-Accessible Curvature Memory Law',
    equation_labels=('eq:drv_bhhr_b04_1b', 'eq:drv_bhhr_b04_theorem_1b', 'eq:drv_bhhr_b04_res_1b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

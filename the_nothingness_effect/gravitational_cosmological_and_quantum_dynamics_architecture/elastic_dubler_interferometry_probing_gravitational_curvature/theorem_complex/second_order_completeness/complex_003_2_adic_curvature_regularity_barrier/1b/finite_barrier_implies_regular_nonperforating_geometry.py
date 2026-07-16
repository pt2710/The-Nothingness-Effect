'Authoritative theorem title: Finite Barrier Implies Regular Nonperforating Geometry.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='2_adic_curvature_regularity_barrier',
    role=TheoremRole.LEFT,
    authoritative_title='Finite Barrier Implies Regular Nonperforating Geometry',
    authoritative_title_tex='Finite Barrier Implies Regular Nonperforating Geometry',
    equation_labels=('eq:drv_edi_b03_1b', 'eq:drv_edi_b03_theorem_1b', 'eq:drv_edi_b03_res_1b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

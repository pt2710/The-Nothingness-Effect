'Authoritative theorem title: Existence and Stable Uniqueness of the Regularized Geometry.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='regularized_stable_geometric_reconstruction',
    role=TheoremRole.LEFT,
    authoritative_title='Existence and Stable Uniqueness of the Regularized Geometry',
    authoritative_title_tex='Existence and Stable Uniqueness of the Regularized Geometry',
    equation_labels=('eq:drv_edi_c02_1c', 'eq:drv_edi_c02_theorem_1c', 'eq:drv_edi_c02_res_1c'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

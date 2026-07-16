'Authoritative theorem title: Injective Phase--Elliptic Reconstruction Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='phase_elliptic_curvature_reconstruction',
    role=TheoremRole.LEFT,
    authoritative_title='Injective Phase–Elliptic Reconstruction Law',
    authoritative_title_tex='Injective Phase--Elliptic Reconstruction Law',
    equation_labels=('eq:drv_edi_b01_1b', 'eq:drv_edi_b01_theorem_1b', 'eq:drv_edi_b01_res_1b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

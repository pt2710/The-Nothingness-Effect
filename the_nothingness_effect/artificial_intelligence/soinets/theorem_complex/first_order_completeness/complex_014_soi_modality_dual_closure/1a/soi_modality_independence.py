'Authoritative theorem title: SOI-Modality Independence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='soi_modality_dual_closure',
    role=TheoremRole.LEFT,
    authoritative_title='SOI-Modality Independence',
    authoritative_title_tex='SOI-Modality Independence',
    equation_labels=(),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

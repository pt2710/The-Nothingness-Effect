'Authoritative theorem title: SOI Universal Collapse-Completeness.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='soi_modality_invariant_convergence_and_collapse_completeness',
    role=TheoremRole.RIGHT,
    authoritative_title='SOI Universal Collapse-Completeness',
    authoritative_title_tex='SOI Universal Collapse-Completeness',
    equation_labels=(),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

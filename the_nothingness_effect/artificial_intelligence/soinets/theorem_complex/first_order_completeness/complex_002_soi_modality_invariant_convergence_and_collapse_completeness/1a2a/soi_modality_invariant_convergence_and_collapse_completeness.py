'Authoritative theorem title: SOI-Modality-Invariant Convergence and Collapse-Completeness (1A\\leftrightarrow2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='soi_modality_invariant_convergence_and_collapse_completeness',
    role=TheoremRole.CROSS,
    authoritative_title='SOI-Modality-Invariant Convergence and Collapse-Completeness',
    authoritative_title_tex='SOI-Modality-Invariant Convergence and Collapse-Completeness (1A\\leftrightarrow2A)',
    equation_labels=(),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: DFI Contextual Instability Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dfi_adaptive_applicability_and_contextual_instability',
    role=TheoremRole.RIGHT,
    authoritative_title='DFI Contextual Instability Theorem',
    authoritative_title_tex='DFI Contextual Instability Theorem',
    equation_labels=('eq:dfi04_contextual_defect_2a', 'eq:dfi04_nonzero_contextual_defect_2a', 'eq:dfi04_loss_universality_2a', 'eq:dfi04_synthesis_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

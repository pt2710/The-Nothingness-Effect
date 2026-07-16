'Authoritative theorem title: DFI Adaptive Applicability Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dfi_adaptive_applicability_and_contextual_instability',
    role=TheoremRole.LEFT,
    authoritative_title='DFI Adaptive Applicability Theorem',
    authoritative_title_tex='DFI Adaptive Applicability Theorem',
    equation_labels=('eq:dfi04_application_chain_1a', 'eq:dfi04_composite_mapping_1a', 'eq:dfi04_conditional_universality_1a', 'eq:dfi04_synthesis_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: DFI Non-Normalization Breakdown.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dfi_spectrum_normalized_existence_and_normalization_breakdown',
    role=TheoremRole.RIGHT,
    authoritative_title='DFI Non-Normalization Breakdown',
    authoritative_title_tex='DFI Non-Normalization Breakdown',
    equation_labels=('eq:dfi01_breakdown_conditions_2a', 'eq:dfi01_divergence_witness_2a', 'eq:dfi01_divergence_conclusion_2a', 'eq:dfi01_scaled_singularity_2a', 'eq:dfi01_synthesis_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Localized Curvature–Information Preservation Duality (1A $\\leftrightarrow$ 2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='localized_curvature_information_preservation_duality',
    role=TheoremRole.CROSS,
    authoritative_title='Localized Curvature–Information Preservation Duality',
    authoritative_title_tex='Localized Curvature–Information Preservation Duality (1A $\\leftrightarrow$ 2A)',
    equation_labels=('eq:ldg12_information_status_1a2a', 'eq:local_information_flow', 'eq:global_information_loss', 'eq:localized_curvature_info_1a2a', 'eq:local_information_conservation', 'eq:curvature_entropy_integral_1a2a', 'eq:lemma_transition_phase_1a2a', 'eq:lemma_local_vs_global_integral_1a2a', 'eq:duality_transition_1a2a', 'eq:proof_duality_integral_1a2a', 'eq:corollary_recovery_threshold_1a2a', 'eq:corollary_info_threshold_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

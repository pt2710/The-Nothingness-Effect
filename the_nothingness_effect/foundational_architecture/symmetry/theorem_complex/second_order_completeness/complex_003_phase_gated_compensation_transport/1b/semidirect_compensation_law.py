'Authoritative theorem title: Semidirect Compensation Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='phase_gated_compensation_transport',
    role=TheoremRole.LEFT,
    authoritative_title='Semidirect Compensation Law',
    authoritative_title_tex='Semidirect Compensation Law',
    equation_labels=('eq:phase_gated_compensation_operator_1b', 'eq:semidirect_compensation_law_1b', 'eq:phase_gated_balance_invariance_1b', 'eq:phase_gated_semidirect_product_1b', 'eq:phase_gated_conjugacy_1b', 'eq:phase_gated_inverse_1b', 'eq:translated_reflection_involution_1b', 'eq:translation_reflection_normal_forms_1b', 'eq:dual_motion_involutive_phase_synthesis_1b', 'eq:phase_gated_compensation_principle_1b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

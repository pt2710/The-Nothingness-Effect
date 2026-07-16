'Authoritative theorem title: Localized Curvature–Information Preservation (1A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='localized_curvature_information_preservation_duality',
    role=TheoremRole.LEFT,
    authoritative_title='Localized Curvature–Information Preservation',
    authoritative_title_tex='Localized Curvature–Information Preservation (1A)',
    equation_labels=('eq:ldg12_information_order_parameter_1a', 'eq:ldg12_information_branch_condition_1a', 'eq:local_curvature_preserves_info_1a', 'eq:local_curvature_didt_1a', 'eq:local_support_info_lemma_1a', 'eq:lemma_info_integral_1a', 'eq:proof_local_operator_1a', 'eq:proof_local_curvature_time_1a', 'eq:local_error_correction_1a', 'eq:local_error_correction_integral_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

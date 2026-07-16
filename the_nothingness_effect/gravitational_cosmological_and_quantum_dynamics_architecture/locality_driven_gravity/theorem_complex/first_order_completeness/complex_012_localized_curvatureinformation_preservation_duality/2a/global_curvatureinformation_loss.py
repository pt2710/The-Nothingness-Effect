'Authoritative theorem title: Global Curvature–Information Loss (2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='localized_curvature_information_preservation_duality',
    role=TheoremRole.RIGHT,
    authoritative_title='Global Curvature–Information Loss',
    authoritative_title_tex='Global Curvature–Information Loss (2A)',
    equation_labels=('eq:ldg12_information_order_parameter_2a', 'eq:ldg12_information_branch_condition_2a', 'eq:global_curvature_erasure_2a', 'eq:global_curvature_decay_2a', 'eq:globalization_dilutes_2a', 'eq:lemma_integral_loss_2a', 'eq:proof_2a_no_retrieval', 'eq:proof_info_decay_2a', 'eq:no_inverse_global_2a', 'eq:corollary_global_integral_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

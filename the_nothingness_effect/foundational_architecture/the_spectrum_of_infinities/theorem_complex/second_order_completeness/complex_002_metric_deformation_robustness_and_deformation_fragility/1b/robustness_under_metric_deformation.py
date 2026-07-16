'Authoritative theorem title: Robustness under Metric Deformation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='metric_deformation_robustness_and_deformation_fragility',
    role=TheoremRole.LEFT,
    authoritative_title='Robustness under Metric Deformation',
    authoritative_title_tex='Robustness under Metric Deformation',
    equation_labels=('eq:soi_metric_positive_branch_composition_1b', 'eq:soi_metric_theorem_pushforward_1b', 'eq:soi_metric_theorem_lp_isometry_1b', 'eq:soi_metric_theorem_entropy_transport_1b', 'eq:soi_metric_theorem_dynamic_transport_1b', 'eq:soi_metric_theorem_representation_transport_1b', 'eq:soi_metric_lemma_pushforward_identity_1b', 'eq:soi_metric_lemma_change_variables_1b', 'eq:soi_metric_lemma_dynamic_identity_1b', 'eq:soi_metric_proof_pushforward_1b', 'eq:soi_metric_proof_intertwining_1b', 'eq:soi_metric_proof_factorization_1b', 'eq:soi_metric_corollary_dfi_baseline_1b', 'eq:soi_metric_corollary_dfi_fluctuation_1b', 'eq:soi_metric_corollary_address_map_1b', 'eq:soi_metric_synthesis_positive_1b', 'eq:std_soi_metric_robust_1b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

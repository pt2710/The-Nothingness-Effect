'Authoritative theorem title: Fragility under Deformation Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='metric_deformation_robustness_and_deformation_fragility',
    role=TheoremRole.RIGHT,
    authoritative_title='Fragility under Deformation Theorem',
    authoritative_title_tex='Fragility under Deformation Theorem',
    equation_labels=('eq:soi_metric_negative_branch_composition_2b', 'eq:soi_metric_defect_tuple_2b', 'eq:soi_metric_collision_defect_2b', 'eq:soi_metric_gap_defect_2b', 'eq:soi_metric_metric_defect_2b', 'eq:soi_metric_normalization_defect_2b', 'eq:soi_metric_lp_defect_2b', 'eq:soi_metric_entropy_defect_2b', 'eq:soi_metric_dynamic_commutator_2b', 'eq:soi_metric_representation_residual_2b', 'eq:soi_metric_nonzero_defect_condition_2b', 'eq:soi_metric_corollary_independent_defects_2b', 'eq:soi_metric_synthesis_negative_2b', 'eq:std_soi_metric_defect_2b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

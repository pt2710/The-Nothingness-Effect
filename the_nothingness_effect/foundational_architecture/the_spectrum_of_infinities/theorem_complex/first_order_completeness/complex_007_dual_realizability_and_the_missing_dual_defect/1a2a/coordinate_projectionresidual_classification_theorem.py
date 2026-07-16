'Authoritative theorem title: Coordinate Projection--Residual Classification Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dual_realizability_and_the_missing_dual_defect',
    role=TheoremRole.CROSS,
    authoritative_title='Coordinate Projection–Residual Classification Theorem',
    authoritative_title_tex='Coordinate Projection--Residual Classification Theorem',
    equation_labels=('eq:soi_dual_realizability_original_soi_1a2a', 'eq:soi_dual_realizability_measure_scaling_1a2a', 'eq:soi_dual_realizability_pushforward_pair_1a2a', 'eq:std_soi_projection_joint', 'eq:soi_dual_realizability_absolute_scale_1a2a', 'eq:soi_dual_realizability_residual_scale_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

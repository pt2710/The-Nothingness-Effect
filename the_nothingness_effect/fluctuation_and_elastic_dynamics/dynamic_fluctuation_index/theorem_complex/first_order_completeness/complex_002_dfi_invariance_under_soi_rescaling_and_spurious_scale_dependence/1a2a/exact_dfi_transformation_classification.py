'Authoritative theorem title: Exact DFI Transformation Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dfi_invariance_under_soi_rescaling_and_spurious_scale_dependence',
    role=TheoremRole.CROSS,
    authoritative_title='Exact DFI Transformation Classification',
    authoritative_title_tex='Exact DFI Transformation Classification',
    equation_labels=('eq:dfi02_global_rescaling_1a2a', 'eq:dfi02_rescaled_total_denominator_1a2a', 'eq:dfi02_invariance_group_1a2a', 'eq:dfi02_exact_dichotomy_1a2a', 'eq:dfi02_ratio_criterion_1a2a', 'eq:dfi02_scale_covariance_1a2a', 'eq:dfi02_joint_synthesis_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

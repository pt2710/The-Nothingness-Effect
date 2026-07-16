'Authoritative theorem title: SOI--DFI Regularity Transfer Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='spectrum_dfi_duality_and_dfi_divergence',
    role=TheoremRole.CROSS,
    authoritative_title='SOI–DFI Regularity Transfer Theorem',
    authoritative_title_tex='SOI--DFI Regularity Transfer Theorem',
    equation_labels=('eq:soi_dfi_original_soi_1a2a', 'eq:soi_dfi_measure_scaling_1a2a', 'eq:soi_dfi_pushforward_pair_1a2a', 'eq:soi_dfi_core_equations_1a2a', 'eq:soi_dfi_absolute_relative_baseline_1a2a', 'eq:soi_dfi_exponential_response_1a2a', 'eq:std_soi_dfi_joint', 'eq:soi_dfi_scale_covariance_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

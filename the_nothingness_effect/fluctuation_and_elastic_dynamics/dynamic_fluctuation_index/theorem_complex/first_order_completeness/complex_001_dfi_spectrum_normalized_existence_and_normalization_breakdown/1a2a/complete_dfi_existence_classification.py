'Authoritative theorem title: Complete DFI Existence Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dfi_spectrum_normalized_existence_and_normalization_breakdown',
    role=TheoremRole.CROSS,
    authoritative_title='Complete DFI Existence Classification',
    authoritative_title_tex='Complete DFI Existence Classification',
    equation_labels=('eq:dfi_soi', 'eq:dfi_volume', 'eq:dfi_sum', 'eq:dfi_sigma', 'eq:dfi_vi', 'eq:dfi_si', 'eq:dfi01_denominator_1a2a', 'eq:dfi01_status_set_1a2a', 'eq:dfi01_exact_closed_form_1a2a', 'eq:dfi01_domain_1a2a', 'eq:dfi01_joint_synthesis_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

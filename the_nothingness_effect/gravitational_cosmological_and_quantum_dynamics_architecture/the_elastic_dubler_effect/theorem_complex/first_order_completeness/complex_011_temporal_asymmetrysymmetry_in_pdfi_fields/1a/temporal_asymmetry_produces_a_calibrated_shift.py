'Authoritative theorem title: Temporal Asymmetry Produces a Calibrated Shift.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='temporal_asymmetry_symmetry_in_pdfi_fields',
    role=TheoremRole.LEFT,
    authoritative_title='Temporal Asymmetry Produces a Calibrated Shift',
    authoritative_title_tex='Temporal Asymmetry Produces a Calibrated Shift',
    equation_labels=('eq:ed11_asymmetry_norm_1a', 'eq:ed11_shift_iff_1a', 'eq:ed11_signed_cancellation_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Spectrum--DFI Duality Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='spectrum_dfi_duality_and_dfi_divergence',
    role=TheoremRole.LEFT,
    authoritative_title='Spectrum–DFI Duality Theorem',
    authoritative_title_tex='Spectrum--DFI Duality Theorem',
    equation_labels=(),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

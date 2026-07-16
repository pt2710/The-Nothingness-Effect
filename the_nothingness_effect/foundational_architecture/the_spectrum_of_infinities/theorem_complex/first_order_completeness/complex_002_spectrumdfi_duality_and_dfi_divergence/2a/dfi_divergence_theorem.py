'Authoritative theorem title: DFI Divergence Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='spectrum_dfi_duality_and_dfi_divergence',
    role=TheoremRole.RIGHT,
    authoritative_title='DFI Divergence Theorem',
    authoritative_title_tex='DFI Divergence Theorem',
    equation_labels=('eq:std_soi_dfi_regularity_2a',),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

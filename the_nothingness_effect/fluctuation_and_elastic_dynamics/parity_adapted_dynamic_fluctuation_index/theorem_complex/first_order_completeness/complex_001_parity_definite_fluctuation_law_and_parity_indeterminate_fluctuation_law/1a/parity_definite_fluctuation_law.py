'Authoritative theorem title: Parity-Definite Fluctuation Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='parity_definite_fluctuation_law_and_parity_indeterminate_fluctuation_law',
    role=TheoremRole.LEFT,
    authoritative_title='Parity-Definite Fluctuation Law',
    authoritative_title_tex='Parity-Definite Fluctuation Law',
    equation_labels=('eq:reversible_pDFI_fluctuation_1a', 'eq:pDFI_inverse_relation_proof_1a', 'eq:parity_definite_pDFI_derivative_1a', 'eq:parity_closed_pDFI_1a', 'eq:predictable_fluctuation_pDFI_corollary_1a', 'eq:pdfi01_synthesis_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Locality Decomposition $\\leftrightarrow$ Nonlocal Entropic Divergence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='locality_decomposition_nonlocal_entropic_divergence',
    role=TheoremRole.CROSS,
    authoritative_title='Locality Decomposition <-> Nonlocal Entropic Divergence',
    authoritative_title_tex='Locality Decomposition $\\leftrightarrow$ Nonlocal Entropic Divergence',
    equation_labels=('eq:ldg01_locality_decomposition_status_1a2a', 'eq:locality_decomposition_sum_1a2a', 'eq:nonlocal_entropic_integral_1a2a', 'eq:locality_length_formula_1a2a', 'eq:global_flatness_limit_1a2a', 'eq:locality_limit_lemma_1a2a', 'eq:locality_limit_calculus_1a2a', 'eq:locality_nonlocality_proof_calculus_1a2a', 'eq:survival_loss_algebraic_1a2a', 'eq:survival_loss_calculus_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

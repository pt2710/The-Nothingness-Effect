'Authoritative theorem title: Locality Decomposition Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='locality_decomposition_nonlocal_entropic_divergence',
    role=TheoremRole.LEFT,
    authoritative_title='Locality Decomposition Theorem',
    authoritative_title_tex='Locality Decomposition Theorem',
    equation_labels=('eq:ldg01_locality_decomposition_order_parameter_1a', 'eq:ldg01_locality_decomposition_branch_condition_1a', 'eq:locality_decomposition_sum_1a', 'eq:locality_length_formula_1a', 'eq:locality_length_lemma_1a', 'eq:locality_gradient_derivative_1a', 'eq:cross_exponential_decay_1a', 'eq:proof_calculus_decay_1a', 'eq:spiral_pitch_law_1a', 'eq:spiral_pitch_derivative_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

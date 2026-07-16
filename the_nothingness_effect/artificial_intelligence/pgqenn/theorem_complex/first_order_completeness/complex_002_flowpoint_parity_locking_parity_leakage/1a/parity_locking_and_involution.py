'Authoritative theorem title: Parity Locking and Involution (1A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='flowpoint_parity_locking_parity_leakage',
    role=TheoremRole.LEFT,
    authoritative_title='Parity Locking and Involution',
    authoritative_title_tex='Parity Locking and Involution (1A)',
    equation_labels=('eq:flowpoint_parity_locking_algebraic_align_1a', 'eq:flowpoint_parity_locking_algebraic_equation_1a', 'eq:flowpoint_parity_locking_calculus_align_1a', 'eq:flowpoint_parity_locking_calculus_equation_1a', 'eq:eigen_flowpoint_reduction_algebraic_align_1a', 'eq:eigen_flowpoint_reduction_algebraic_equation_1a', 'eq:eigen_flowpoint_reduction_calculus_align_1a', 'eq:eigen_flowpoint_reduction_calculus_equation_1a', 'eq:flowpoint_parity_locking_proof_algebraic_align_1a', 'eq:flowpoint_parity_locking_proof_algebraic_equation_1a', 'eq:flowpoint_parity_locking_proof_calculus_align_1a', 'eq:flowpoint_parity_locking_proof_calculus_equation_1a', 'eq:bounded_stacking_algebraic_align_1a', 'eq:bounded_stacking_algebraic_equation_1a', 'eq:bounded_stacking_calculus_align_1a', 'eq:bounded_stacking_calculus_equation_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

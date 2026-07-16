'Authoritative theorem title: Flowpoint Parity Locking $\\leftrightarrow$ Parity Leakage.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='flowpoint_parity_locking_parity_leakage',
    role=TheoremRole.CROSS,
    authoritative_title='Flowpoint Parity Locking <-> Parity Leakage',
    authoritative_title_tex='Flowpoint Parity Locking $\\leftrightarrow$ Parity Leakage',
    equation_labels=('eq:flowpoint_parity_locking_algebraic_align_1a2a', 'eq:flowpoint_parity_locking_algebraic_equation_1a2a', 'eq:flowpoint_parity_locking_calculus_align_1a2a', 'eq:flowpoint_parity_locking_calculus_equation_1a2a', 'eq:eigen_flowpoint_lemma_algebraic_align_1a2a', 'eq:eigen_flowpoint_lemma_algebraic_equation_1a2a', 'eq:eigen_flowpoint_lemma_calculus_align_1a2a', 'eq:eigen_flowpoint_lemma_calculus_equation_1a2a', 'eq:flowpoint_parity_locking_dual_proof_algebraic_align_1a2a', 'eq:flowpoint_parity_locking_dual_proof_algebraic_equation_1a2a', 'eq:flowpoint_parity_locking_dual_proof_calculus_align_1a2a', 'eq:flowpoint_parity_locking_dual_proof_calculus_equation_1a2a', 'eq:dual_phase_diagnostics_algebraic_align_1a2a', 'eq:dual_phase_diagnostics_algebraic_equation_1a2a', 'eq:dual_phase_diagnostics_calculus_align_1a2a', 'eq:dual_phase_diagnostics_calculus_equation_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

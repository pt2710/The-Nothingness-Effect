'Authoritative theorem title: Commutation $\\leftrightarrow$ Misalignment.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='commutation_of_closure_with_parity_soi_and_misaligned_closures',
    role=TheoremRole.CROSS,
    authoritative_title='Commutation <-> Misalignment',
    authoritative_title_tex='Commutation $\\leftrightarrow$ Misalignment',
    equation_labels=('eq:completeness_synthesis_formal_16', 'eq:completeness_principle_formal_17', 'eq:completeness_synthesis_formal_17', 'eq:completeness_principle_formal_18', 'eq:cps_theorem_algebraic_equation_1a2a_8', 'eq:cps_theorem_calculus_equation_1a2a_8', 'eq:cps_theorem_quantum_equation_1a2a_8', 'eq:cps_lemma_algebraic_equation_1a2a_8', 'eq:cps_lemma_calculus_equation_1a2a_8', 'eq:cps_lemma_quantum_equation_1a2a_8', 'eq:cps_proof_algebraic_equation_1a2a_8', 'eq:cps_proof_calculus_equation_1a2a_8', 'eq:cps_proof_quantum_equation_1a2a_8', 'eq:cps_cor_algebraic_equation_1a2a_8', 'eq:cps_cor_calculus_equation_1a2a_8', 'eq:cps_cor_quantum_equation_1a2a_8', 'eq:completeness_synthesis_formal_18', 'eq:completeness_principle_formal_19'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

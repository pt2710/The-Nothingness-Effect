'Authoritative theorem title: Conservativity $\\leftrightarrow$ Overreach.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='conservativity_of_dual_closure_over_base_theory_and_trivialization_overreach',
    role=TheoremRole.CROSS,
    authoritative_title='Conservativity <-> Overreach',
    authoritative_title_tex='Conservativity $\\leftrightarrow$ Overreach',
    equation_labels=('eq:completeness_synthesis_formal_19', 'eq:completeness_principle_formal_20', 'eq:completeness_synthesis_formal_20', 'eq:completeness_principle_formal_21', 'eq:cons_theorem_algebraic_equation_1a2a_9', 'eq:cons_theorem_calculus_equation_1a2a_9', 'eq:cons_theorem_quantum_equation_1a2a_9', 'eq:cons_lemma_algebraic_equation_1a2a_9', 'eq:cons_lemma_calculus_equation_1a2a_9', 'eq:cons_lemma_quantum_equation_1a2a_9', 'eq:cons_proof_algebraic_equation_1a2a_9', 'eq:cons_proof_calculus_equation_1a2a_9', 'eq:cons_proof_quantum_equation_1a2a_9', 'eq:cons_cor_algebraic_equation_1a2a_9', 'eq:cons_cor_calculus_equation_1a2a_9', 'eq:cons_cor_quantum_equation_1a2a_9', 'eq:completeness_synthesis_formal_21', 'eq:completeness_principle_formal_22'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

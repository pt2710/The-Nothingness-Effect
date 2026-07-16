'Authoritative theorem title: Karoubi Equivalence $\\leftrightarrow$ Missing Splittings.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='karoubi_envelope_equivalence_and_missing_idempotent_splittings',
    role=TheoremRole.CROSS,
    authoritative_title='Karoubi Equivalence <-> Missing Splittings',
    authoritative_title_tex='Karoubi Equivalence $\\leftrightarrow$ Missing Splittings',
    equation_labels=('eq:completeness_synthesis_formal_13', 'eq:completeness_principle_formal_14', 'eq:completeness_synthesis_formal_14', 'eq:completeness_principle_formal_15', 'eq:karoubi_theorem_algebraic_align_1a2a_73', 'eq:karoubi_theorem_calculus_align_1a2a_73', 'eq:karoubi_theorem_quantum_align_1a2a_73', 'eq:karoubi_lemma_algebraic_equation_1a2a_73', 'eq:karoubi_lemma_calculus_equation_1a2a_73', 'eq:karoubi_lemma_quantum_equation_1a2a_73', 'eq:karoubi_proof_algebraic_equation_1a2a_73', 'eq:karoubi_proof_calculus_equation_1a2a_73', 'eq:karoubi_proof_quantum_equation_1a2a_73', 'eq:karoubi_cor_algebraic_equation_1a2a_73', 'eq:karoubi_cor_calculus_equation_1a2a_73', 'eq:karoubi_cor_quantum_equation_1a2a_73', 'eq:completeness_synthesis_formal_15', 'eq:completeness_principle_formal_16'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

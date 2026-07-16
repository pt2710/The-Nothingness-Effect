'Authoritative theorem title: Karoubi Envelope Equivalence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='karoubi_envelope_equivalence_and_missing_idempotent_splittings',
    role=TheoremRole.LEFT,
    authoritative_title='Karoubi Envelope Equivalence',
    authoritative_title_tex='Karoubi Envelope Equivalence',
    equation_labels=('eq:karoubi_1a_algebraic_align_1a_73', 'eq:karoubi_1a_calculus_align_1a_73', 'eq:karoubi_1a_quantum_align_1a_73', 'eq:karoubi_lemma_algebraic_align_1a_73', 'eq:karoubi_lemma_calculus_align_1a_73', 'eq:karoubi_lemma_quantum_align_1a_73', 'eq:karoubi_proof_algebraic_align_1a_73', 'eq:karoubi_proof_calculus_align_1a_73', 'eq:karoubi_proof_quantum_align_1a_73', 'eq:karoubi_cor_algebraic_equation_1a_73', 'eq:karoubi_cor_calculus_equation_1a_73', 'eq:karoubi_cor_quantum_equation_1a_73'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Flowpoint--Parity Correspondence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='flowpoint_parity_correspondence_and_decoupling',
    role=TheoremRole.LEFT,
    authoritative_title='Flowpoint–Parity Correspondence',
    authoritative_title_tex='Flowpoint--Parity Correspondence',
    equation_labels=('eq:pdfi02_zero_coupling_defect_1a', 'eq:flowpoint_parity_commute_1a', 'eq:flowpoint_parity_coupling_lemma_1a', 'eq:flowpoint_parity_entropy_jump_corollary_1a', 'eq:pdfi02_synthesis_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

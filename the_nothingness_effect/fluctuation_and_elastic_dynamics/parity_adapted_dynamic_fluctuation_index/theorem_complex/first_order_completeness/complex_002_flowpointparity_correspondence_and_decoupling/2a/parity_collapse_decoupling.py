'Authoritative theorem title: Parity Collapse/Decoupling.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='flowpoint_parity_correspondence_and_decoupling',
    role=TheoremRole.RIGHT,
    authoritative_title='Parity Collapse/Decoupling',
    authoritative_title_tex='Parity Collapse/Decoupling',
    equation_labels=('eq:parity_collapse_commutator_2a', 'eq:flowpoint_parity_independent_lemma_2a', 'eq:parity_collapse_entropy_flat_corollary_2a', 'eq:pdfi02_synthesis_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

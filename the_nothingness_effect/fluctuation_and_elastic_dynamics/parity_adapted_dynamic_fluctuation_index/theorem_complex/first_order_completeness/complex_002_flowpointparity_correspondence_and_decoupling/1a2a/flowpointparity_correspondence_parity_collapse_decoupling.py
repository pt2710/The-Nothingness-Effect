'Authoritative theorem title: Flowpoint--Parity Correspondence $\\longleftrightarrow$ Parity Collapse/Decoupling.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='flowpoint_parity_correspondence_and_decoupling',
    role=TheoremRole.CROSS,
    authoritative_title='Flowpoint–Parity Correspondence <-> Parity Collapse/Decoupling',
    authoritative_title_tex='Flowpoint--Parity Correspondence $\\longleftrightarrow$ Parity Collapse/Decoupling',
    equation_labels=('eq:flowpoint_parity_commute_1a2a', 'eq:flowpoint_parity_decouple_1a2a', 'eq:pdfi02_status_set_1a2a', 'eq:flowpoint_parity_coupling_lemma_1a2a', 'eq:pdfi02_joint_synthesis_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

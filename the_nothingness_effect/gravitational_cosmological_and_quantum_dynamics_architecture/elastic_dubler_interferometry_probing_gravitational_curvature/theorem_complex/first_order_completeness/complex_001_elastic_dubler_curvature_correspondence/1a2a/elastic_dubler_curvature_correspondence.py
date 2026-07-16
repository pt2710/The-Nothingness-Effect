'Authoritative theorem title: Elastic Dubler Curvature Correspondence (1A $\\leftrightarrow$ 2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_dubler_curvature_correspondence',
    role=TheoremRole.CROSS,
    authoritative_title='Elastic Dubler Curvature Correspondence',
    authoritative_title_tex='Elastic Dubler Curvature Correspondence (1A $\\leftrightarrow$ 2A)',
    equation_labels=('eq:edi01_curvature_correspondence_status_1a2a', 'eq:edi_forward_map_1a2a', 'eq:edi_jacobian_1a2a', 'eq:edi_invertibility_1a2a', 'eq:edi_phase_evolution_1a2a', 'eq:edi_lemma_bijection_1a2a', 'eq:edi_lemma_invert_1a2a', 'eq:edi_dual_proof_1a2a', 'eq:edi_dual_proof_invert_1a2a', 'eq:edi_dual_corollary_1a2a', 'eq:edi_dual_corollary_lock_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

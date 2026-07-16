'Authoritative theorem title: Elastic Dubler Curvature Determinacy (1A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_dubler_curvature_correspondence',
    role=TheoremRole.LEFT,
    authoritative_title='Elastic Dubler Curvature Determinacy',
    authoritative_title_tex='Elastic Dubler Curvature Determinacy (1A)',
    equation_labels=('eq:edi01_curvature_correspondence_order_parameter_1a', 'eq:edi01_curvature_correspondence_branch_condition_1a', 'eq:edi_jacobian_invert_1a', 'eq:edi_reconstruction_1a', 'eq:edi_phase_evolution_1a', 'eq:edi_lemma_inv_1a', 'eq:edi_lemma_monotonic_1a', 'eq:edi_proof_unique_1a', 'eq:edi_proof_one2one_1a', 'eq:edi_corollary_imaging_1a', 'eq:edi_corollary_partial_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

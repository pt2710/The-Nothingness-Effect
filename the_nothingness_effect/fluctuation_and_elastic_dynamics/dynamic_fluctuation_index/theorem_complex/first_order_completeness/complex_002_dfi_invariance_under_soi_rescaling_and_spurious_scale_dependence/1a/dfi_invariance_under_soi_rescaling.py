'Authoritative theorem title: DFI Invariance Under SOI Rescaling.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dfi_invariance_under_soi_rescaling_and_spurious_scale_dependence',
    role=TheoremRole.LEFT,
    authoritative_title='DFI Invariance Under SOI Rescaling',
    authoritative_title_tex='DFI Invariance Under SOI Rescaling',
    equation_labels=('eq:dfi02_invariance_definition_1a', 'eq:dfi02_exact_invariance_1a', 'eq:dfi02_homogeneity_identity_1a', 'eq:dfi02_ranking_preservation_1a', 'eq:dfi02_synthesis_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

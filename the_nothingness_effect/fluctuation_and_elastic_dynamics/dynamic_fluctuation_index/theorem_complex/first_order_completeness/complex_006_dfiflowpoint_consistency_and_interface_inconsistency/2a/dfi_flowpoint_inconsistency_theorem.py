'Authoritative theorem title: DFI-Flowpoint Inconsistency Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dfi_flowpoint_consistency_and_interface_inconsistency',
    role=TheoremRole.RIGHT,
    authoritative_title='DFI-Flowpoint Inconsistency Theorem',
    authoritative_title_tex='DFI-Flowpoint Inconsistency Theorem',
    equation_labels=('eq:dfi06_component_defect_2a', 'eq:dfi06_vector_defect_2a', 'eq:dfi06_noncommuting_interface_2a', 'eq:dfi06_inconsistent_vectors_2a', 'eq:dfi06_defect_decomposition_2a', 'eq:dfi06_synthesis_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

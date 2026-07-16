'Authoritative theorem title: Modality-Invariant Collapse Principle.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='soinet_cross_modal_compositionality_modality_invariant_collapse_principle',
    role=TheoremRole.RIGHT,
    authoritative_title='Modality-Invariant Collapse Principle',
    authoritative_title_tex='Modality-Invariant Collapse Principle',
    equation_labels=('eq:soinet_collapse_2a', 'eq:soinet_calculus_collapse_2a', 'eq:fixedpoint_flowpoint_2a', 'eq:fixedpoint_derivative_2a', 'eq:fixpoint_intersection_2a', 'eq:collapse_derivative_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Nonlocal Entropic Divergence Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='locality_decomposition_nonlocal_entropic_divergence',
    role=TheoremRole.RIGHT,
    authoritative_title='Nonlocal Entropic Divergence Theorem',
    authoritative_title_tex='Nonlocal Entropic Divergence Theorem',
    equation_labels=('eq:ldg01_locality_decomposition_order_parameter_2a', 'eq:ldg01_locality_decomposition_branch_condition_2a', 'eq:nonlocal_curvature_2a', 'eq:nonlocal_calculus_flat_2a', 'eq:global_collapse_flat_2a', 'eq:collapse_grad_vanish_2a', 'eq:nonlocal_constant_integral_2a', 'eq:proof_flat_grad_2a', 'eq:pattern_loss_algebraic_2a', 'eq:pattern_loss_calculus_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

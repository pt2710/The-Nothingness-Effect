'Authoritative theorem title: Entropic Curvature Superposition Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='entropic_curvature_superposition_duality',
    role=TheoremRole.LEFT,
    authoritative_title='Entropic Curvature Superposition Theorem',
    authoritative_title_tex='Entropic Curvature Superposition Theorem',
    equation_labels=('eq:ldg03_curvature_superposition_order_parameter_1a', 'eq:ldg03_curvature_superposition_branch_condition_1a', 'eq:entropic_curvature_superposition_structure_1a', 'eq:entropic_curvature_superposition_integral_1a', 'eq:entropic_curvature_gradient_1a', 'eq:entropic_curvature_gradient_integral_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

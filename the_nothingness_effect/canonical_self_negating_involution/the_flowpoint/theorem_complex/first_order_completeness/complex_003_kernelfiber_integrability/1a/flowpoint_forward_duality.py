'Authoritative theorem title: Flowpoint Forward Duality.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='kernel_fiber_integrability',
    role=TheoremRole.LEFT,
    authoritative_title='Flowpoint Forward Duality',
    authoritative_title_tex='Flowpoint Forward Duality',
    equation_labels=('eq:forward_flowpoint_legal_increment_definition_1a', 'eq:forward_flowpoint_update_definition_1a', 'eq:flowpoint_forward_duality_alg_oprtr_eq1_1a', 'eq:flowpoint_forward_balance_invariance_1a', 'eq:flowpoint_forward_update_inverse_1a', 'eq:flowpoint_forward_update_composition_1a', 'eq:minimal_closure_balance_condition_1a', 'eq:minimal_closure_kernel_condition_1a', 'eq:minimal_closure_membership_condition_1a', 'eq:minimal_closure_antisymmetry_condition_1a', 'eq:flowpoint_forward_conservation_derivative_1a', 'eq:flowpoint_forward_rate_antisymmetry_1a', 'eq:flowpoint_forward_affine_trajectory_1a', 'eq:forward_kernel_conservation_principle_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

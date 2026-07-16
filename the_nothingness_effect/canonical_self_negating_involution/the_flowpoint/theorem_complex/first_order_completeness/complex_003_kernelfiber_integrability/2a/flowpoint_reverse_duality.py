'Authoritative theorem title: Flowpoint Reverse Duality.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='kernel_fiber_integrability',
    role=TheoremRole.RIGHT,
    authoritative_title='Flowpoint Reverse Duality',
    authoritative_title_tex='Flowpoint Reverse Duality',
    equation_labels=('eq:reverse_flowpoint_legal_increment_definition_2a', 'eq:reverse_flowpoint_update_definition_2a', 'eq:flowpoint_reverse_duality_alg_oprtr_eq1_2a', 'eq:flowpoint_reverse_update_inverse_2a', 'eq:flowpoint_reverse_update_composition_2a', 'eq:dual_symmetry_parameter_reversal_2a', 'eq:dual_symmetry_swap_conjugacy_2a', 'eq:reverse_dual_rate_antisymmetry_2a', 'eq:reverse_dual_conservation_derivative_2a', 'eq:reverse_dual_affine_trajectory_2a', 'eq:reverse_kernel_conservation_principle_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Parseval Energy Bijection (1A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='parseval_energy_bijection_l_2_energy_mismatch',
    role=TheoremRole.LEFT,
    authoritative_title='Parseval Energy Bijection',
    authoritative_title_tex='Parseval Energy Bijection (1A)',
    equation_labels=('eq:psv_parseval_identity_1a', 'eq:psv_hessian_zero_residual_1a', 'eq:psv_projection_formula_1a', 'eq:psv_cross_kill_1a', 'eq:J_value_at_w_1a', 'eq:Jmin_zero_implies_parseval_1a', 'eq:psv_energy_partition_1a', 'eq:hessian_identity_1a', 'eq:strict_convexity_unique_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

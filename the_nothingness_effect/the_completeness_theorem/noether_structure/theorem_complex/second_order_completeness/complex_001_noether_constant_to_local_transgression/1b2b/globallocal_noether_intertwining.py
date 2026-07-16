'Authoritative theorem title: Global–Local Noether Intertwining.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='noether_constant_to_local_transgression',
    role=TheoremRole.CROSS,
    authoritative_title='Global–Local Noether Intertwining',
    authoritative_title_tex='Global–Local Noether Intertwining',
    equation_labels=('eq:noether_constant_injection', 'eq:noether_variation_restriction', 'eq:noether_constant_local_compatibility_1a2a', 'eq:noether_injection_conditions', 'eq:noether_local_implies_global', 'eq:noether_symmetry_synthesis', 'eq:noether_symmetry_principle', 'eq:noether_transgression_definition', 'eq:noether_transgression_balance', 'eq:noether_boundary_separation', 'eq:noether_local_to_global_charge', 'eq:noether_charge_synthesis', 'eq:noether_charge_principle', 'eq:noether_joint_predicate_1a2a', 'eq:noether_transgression_square', 'eq:noether_intertwining', 'eq:noether_global_local_common_composite', 'eq:noether_source_removal', 'eq:noether_joint_conservation', 'eq:noether_joint_synthesis', 'eq:noether_joint_principle'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

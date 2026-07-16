'Authoritative theorem title: Global Symmetry--KD-Charge Equivalence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='global_symmetry_and_kd_charge_conservation',
    role=TheoremRole.CROSS,
    authoritative_title='Global Symmetry–KD-Charge Equivalence',
    authoritative_title_tex='Global Symmetry--KD-Charge Equivalence',
    equation_labels=('eq:completeness_synthesis_formal_31', 'eq:completeness_principle_formal_32', 'eq:kd_conservation_appendix', 'eq:completeness_synthesis_formal_32', 'eq:completeness_principle_formal_33', 'eq:noether_global_joint_1a2a', 'eq:completeness_synthesis_formal_33', 'eq:completeness_principle_formal_34'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

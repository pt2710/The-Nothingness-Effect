'Authoritative theorem title: Instability Lobe (2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='hyper_parameter_stability_wedge_instability_lobe',
    role=TheoremRole.RIGHT,
    authoritative_title='Instability Lobe',
    authoritative_title_tex='Instability Lobe (2A)',
    equation_labels=('eq:instability_indicator_2a', 'eq:sideband_condition_2a', 'eq:instability_growth_rate_2a', 'eq:support_divergence_rate_2a', 'eq:lobe_logic_2a', 'eq:nonclosure_de_morgan_2a', 'eq:violation_flow_2a', 'eq:support_violation_persistence_2a', 'eq:proof_indicator_equiv_2a', 'eq:proof_lobe_membership_2a', 'eq:proof_persistence_lobe_2a', 'eq:proof_necessity_descent_2a', 'eq:autotuner_rule_2a', 'eq:autotuner_probability_2a', 'eq:autotuner_calculus_align_2a', 'eq:autotuner_calculus_equation_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: DTQC 02 -- Support Mismatch/Leakage.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dtqc::dual_support_equivalence_support_mismatch_leakage',
    role=TheoremRole.RIGHT,
    authoritative_title='DTQC 02 – Support Mismatch/Leakage',
    authoritative_title_tex='DTQC 02 -- Support Mismatch/Leakage',
    equation_labels=('eq:leakage_mass_2a', 'eq:nonempty_leakage_implies_mismatch_2a', 'eq:l2_bias_from_leakage_2a', 'eq:single_violation_implies_leakage_2a', 'eq:cardinality_leakage_positive_2a', 'eq:test_window_violation_2a', 'eq:triangle_inequality_support_2a', 'eq:parseval_energy_split_2a', 'eq:leakage_energy_lower_2a', 'eq:leakage_bias_consequence_2a', 'eq:nonvanishing_residual_2a', 'eq:triangle_noise_2a', 'eq:noisy_bias_lower_bound_2a', 'eq:noise_persistence_limit_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

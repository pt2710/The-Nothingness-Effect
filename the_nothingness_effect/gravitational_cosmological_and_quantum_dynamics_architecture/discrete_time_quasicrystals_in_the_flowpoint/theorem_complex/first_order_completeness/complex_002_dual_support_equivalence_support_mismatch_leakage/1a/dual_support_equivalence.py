'Authoritative theorem title: Dual Support Equivalence (1A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dtqc::dual_support_equivalence_support_mismatch_leakage',
    role=TheoremRole.LEFT,
    authoritative_title='Dual Support Equivalence',
    authoritative_title_tex='Dual Support Equivalence (1A)',
    equation_labels=('eq:occupancy_equivalence_1a', 'eq:leakage_zero_1a', 'eq:lattice_windows_pairing_1a', 'eq:indicator_zero_difference_1a', 'eq:l1_indicator_zero_1a', 'eq:window_integral_equivalence_1a', 'eq:support_equality_conclusion_1a', 'eq:selector_equivalence_1a', 'eq:amplitude_map_bijection_1a', 'eq:calibration_relation_1a', 'eq:l2_error_bound_equal_support_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

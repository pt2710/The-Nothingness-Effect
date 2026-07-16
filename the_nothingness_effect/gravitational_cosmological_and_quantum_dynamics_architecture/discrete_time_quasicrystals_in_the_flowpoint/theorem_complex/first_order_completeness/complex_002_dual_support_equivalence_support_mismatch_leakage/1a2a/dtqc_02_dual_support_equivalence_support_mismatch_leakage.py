'Authoritative theorem title: DTQC 02 -- Dual Support Equivalence $\\leftrightarrow$ Support Mismatch/Leakage.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dtqc::dual_support_equivalence_support_mismatch_leakage',
    role=TheoremRole.CROSS,
    authoritative_title='DTQC 02 – Dual Support Equivalence <-> Support Mismatch/Leakage',
    authoritative_title_tex='DTQC 02 -- Dual Support Equivalence $\\leftrightarrow$ Support Mismatch/Leakage',
    equation_labels=('eq:dtqc02_joint_status_1a2a', 'eq:freq_lattice_def_1a2a', 'eq:predicted_spectrum_1a2a', 'eq:empirical_measure_1a2a', 'eq:support_sets_1a2a', 'eq:indicator_equivalence_1a2a', 'eq:leakage_set_1a2a', 'eq:fourier_inversion_linesum_1a2a', 'eq:distribution_pairing_model_1a2a', 'eq:distribution_pairing_empirical_1a2a', 'eq:equivalence_leakage_empty_1a2a', 'eq:counting_equivalence_1a2a', 'eq:test_family_equivalence_1a2a', 'eq:set_algebra_equivalence_1a2a', 'eq:model_pairing_selectors_1a2a', 'eq:empirical_pairing_selectors_1a2a', 'eq:pairing_to_indicator_1a2a', 'eq:support_equality_from_pairings_explicit_1a2a', 'eq:golden_test_statistic_1a2a', 'eq:golden_test_equivalence_1a2a', 'eq:golden_test_window_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

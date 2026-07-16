'Authoritative theorem title: PGQENN 05 -- Support Mismatch/Leakage.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='prime_quasicrystal_support_equivalence_support_mismatch_leakage',
    role=TheoremRole.RIGHT,
    authoritative_title='PGQENN 05 – Support Mismatch/Leakage',
    authoritative_title_tex='PGQENN 05 -- Support Mismatch/Leakage',
    equation_labels=('eq:prime_qc_periodic_align_2a', 'eq:prime_qc_mismatch_equation_2a', 'eq:prime_qc_leakage_rate_align_2a', 'eq:prime_qc_leakage_rate_equation_2a', 'eq:prime_qc_geom_series_align_2a', 'eq:prime_qc_lines_equation_2a', 'eq:prime_qc_band_growth_align_2a', 'eq:prime_qc_band_growth_equation_2a', 'eq:prime_qc_leakage_increment_align_2a', 'eq:prime_qc_leakage_increment_equation_2a', 'eq:prime_qc_leakage_average_align_2a', 'eq:prime_qc_leakage_average_equation_2a', 'eq:prime_qc_threshold_align_2a', 'eq:prime_qc_threshold_equation_2a', 'eq:prime_qc_mavg_align_2a', 'eq:prime_qc_mavg_equation_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

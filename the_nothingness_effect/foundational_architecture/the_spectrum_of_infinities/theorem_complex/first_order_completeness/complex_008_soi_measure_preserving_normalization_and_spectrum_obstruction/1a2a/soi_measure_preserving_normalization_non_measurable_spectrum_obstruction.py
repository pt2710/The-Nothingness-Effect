'Authoritative theorem title: SOI Measure-Preserving Normalization \\(\\leftrightarrow\\) Non-Measurable Spectrum Obstruction.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='soi_measure_preserving_normalization_and_spectrum_obstruction',
    role=TheoremRole.CROSS,
    authoritative_title='SOI Measure-Preserving Normalization <-> Non-Measurable Spectrum Obstruction',
    authoritative_title_tex='SOI Measure-Preserving Normalization \\(\\leftrightarrow\\) Non-Measurable Spectrum Obstruction',
    equation_labels=('eq:soi_mpn_original_soi_1a2a', 'eq:soi_mpn_measure_scaling_1a2a', 'eq:soi_mpn_pushforward_pair_1a2a', 'eq:soi_mpn_algebraic_equation_1a2a', 'eq:soi_mpn_calculus_equation_1a2a', 'eq:soi_mpn_quantum_equation_1a2a', 'eq:soi_mpn_lemma_algebraic_equation_1a2a', 'eq:soi_mpn_lemma_calculus_equation_1a2a', 'eq:soi_mpn_lemma_quantum_equation_1a2a', 'eq:soi_mpn_proof_algebraic_equation_1a2a', 'eq:soi_mpn_proof_calculus_equation_1a2a', 'eq:soi_mpn_proof_quantum_equation_1a2a', 'eq:soi_mpn_corollary_calculus_equation_1a2a', 'eq:soi_mpn_corollary_algebraic_equation_1a2a', 'eq:soi_mpn_corollary_quantum_equation_1a2a', 'eq:std_soi_mpn_joint', 'eq:soi_mpn_absolute_scale_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

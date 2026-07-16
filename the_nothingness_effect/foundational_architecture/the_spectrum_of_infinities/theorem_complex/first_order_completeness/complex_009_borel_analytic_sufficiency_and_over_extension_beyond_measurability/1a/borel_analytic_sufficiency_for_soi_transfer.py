'Authoritative theorem title: Borel/Analytic Sufficiency for SOI Transfer.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='borel_analytic_sufficiency_and_over_extension_beyond_measurability',
    role=TheoremRole.LEFT,
    authoritative_title='Borel/Analytic Sufficiency for SOI Transfer',
    authoritative_title_tex='Borel/Analytic Sufficiency for SOI Transfer',
    equation_labels=('eq:soi_bas_alg_1a', 'eq:soi_bas_absolute_norm_1a', 'eq:soi_bas_calc_1a', 'eq:soi_bas_quant_1a', 'eq:std_soi_definable_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Over-Extension Beyond Measurability.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='borel_analytic_sufficiency_and_over_extension_beyond_measurability',
    role=TheoremRole.RIGHT,
    authoritative_title='Over-Extension Beyond Measurability',
    authoritative_title_tex='Over-Extension Beyond Measurability',
    equation_labels=('eq:soi_bas_alg_2a', 'eq:soi_bas_calc_2a', 'eq:soi_bas_quant_2a', 'eq:std_soi_no_extension_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

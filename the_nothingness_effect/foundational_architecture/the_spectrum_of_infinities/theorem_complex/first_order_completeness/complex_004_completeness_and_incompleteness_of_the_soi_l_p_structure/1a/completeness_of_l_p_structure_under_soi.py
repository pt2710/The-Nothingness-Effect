'Authoritative theorem title: Completeness of \\(L^p\\) Structure under SOI.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='completeness_and_incompleteness_of_the_soi_l_p_structure',
    role=TheoremRole.LEFT,
    authoritative_title='Completeness of L^p Structure under SOI',
    authoritative_title_tex='Completeness of \\(L^p\\) Structure under SOI',
    equation_labels=('eq:soi_lp_absolute_norm_scaling_1a', 'eq:std_soi_lp_generated_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

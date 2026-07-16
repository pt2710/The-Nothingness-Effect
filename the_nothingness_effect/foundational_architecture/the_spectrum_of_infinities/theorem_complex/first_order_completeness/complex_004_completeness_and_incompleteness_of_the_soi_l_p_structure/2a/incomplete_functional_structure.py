'Authoritative theorem title: Incomplete Functional Structure.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='completeness_and_incompleteness_of_the_soi_l_p_structure',
    role=TheoremRole.RIGHT,
    authoritative_title='Incomplete Functional Structure',
    authoritative_title_tex='Incomplete Functional Structure',
    equation_labels=('eq:std_soi_lp_bridge_2a',),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Elastic-Gain OU Support Margin Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_gain_ou_support_margin',
    role=TheoremRole.LEFT,
    authoritative_title='Elastic-Gain OU Support Margin Law',
    authoritative_title_tex='Elastic-Gain OU Support Margin Law',
    equation_labels=('eq:drv_dtqc_b04_1b', 'eq:drv_dtqc_b04_theorem_1b', 'eq:drv_dtqc_b04_res_1b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

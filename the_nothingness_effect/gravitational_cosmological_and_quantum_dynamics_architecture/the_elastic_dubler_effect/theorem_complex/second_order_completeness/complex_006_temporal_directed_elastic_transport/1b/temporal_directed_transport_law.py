'Authoritative theorem title: Temporal Directed-Transport Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='temporal_directed_elastic_transport',
    role=TheoremRole.LEFT,
    authoritative_title='Temporal Directed-Transport Law',
    authoritative_title_tex='Temporal Directed-Transport Law',
    equation_labels=('eq:drv_dubler_b06_1b', 'eq:drv_dubler_b06_theorem_1b', 'eq:drv_dubler_b06_res_1b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

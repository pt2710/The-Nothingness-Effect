'Authoritative theorem title: Temporal Directed-Transport Failure Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='temporal_directed_elastic_transport',
    role=TheoremRole.RIGHT,
    authoritative_title='Temporal Directed-Transport Failure Law',
    authoritative_title_tex='Temporal Directed-Transport Failure Law',
    equation_labels=('eq:drv_dubler_b06_2b', 'eq:drv_dubler_b06_theorem_2b', 'eq:drv_dubler_b06_res_2b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

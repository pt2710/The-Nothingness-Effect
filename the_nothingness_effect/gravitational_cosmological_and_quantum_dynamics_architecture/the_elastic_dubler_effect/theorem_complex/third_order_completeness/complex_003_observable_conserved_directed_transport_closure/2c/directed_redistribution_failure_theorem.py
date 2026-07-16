'Authoritative theorem title: Directed-Redistribution Failure Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='observable_conserved_directed_transport_closure',
    role=TheoremRole.RIGHT,
    authoritative_title='Directed-Redistribution Failure Theorem',
    authoritative_title_tex='Directed-Redistribution Failure Theorem',
    equation_labels=('eq:drv_dubler_c03_2c', 'eq:drv_dubler_c03_theorem_2c', 'eq:drv_dubler_c03_res_2c'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

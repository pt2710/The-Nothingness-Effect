'Authoritative theorem title: Observable Directed-Redistribution Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='observable_conserved_directed_transport_closure',
    role=TheoremRole.LEFT,
    authoritative_title='Observable Directed-Redistribution Theorem',
    authoritative_title_tex='Observable Directed-Redistribution Theorem',
    equation_labels=('eq:drv_dubler_c03_1c', 'eq:drv_dubler_c03_theorem_1c', 'eq:drv_dubler_c03_res_1c'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

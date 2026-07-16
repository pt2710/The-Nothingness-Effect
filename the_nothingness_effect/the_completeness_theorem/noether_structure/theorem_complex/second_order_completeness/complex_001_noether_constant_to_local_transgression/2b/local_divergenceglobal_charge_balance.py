'Authoritative theorem title: Local Divergence–Global Charge Balance.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='noether_constant_to_local_transgression',
    role=TheoremRole.RIGHT,
    authoritative_title='Local Divergence–Global Charge Balance',
    authoritative_title_tex='Local Divergence–Global Charge Balance',
    equation_labels=(),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

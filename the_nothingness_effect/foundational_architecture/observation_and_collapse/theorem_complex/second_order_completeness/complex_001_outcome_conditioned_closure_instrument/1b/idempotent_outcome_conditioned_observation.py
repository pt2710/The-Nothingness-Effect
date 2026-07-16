'Authoritative theorem title: Idempotent Outcome-Conditioned Observation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='outcome_conditioned_closure_instrument',
    role=TheoremRole.LEFT,
    authoritative_title='Idempotent Outcome-Conditioned Observation',
    authoritative_title_tex='Idempotent Outcome-Conditioned Observation',
    equation_labels=('eq:drv_oac_b01_1b', 'eq:drv_oac_b01_theorem_1b', 'eq:drv_oac_b01_res_1b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

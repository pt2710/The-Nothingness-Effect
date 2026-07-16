'Authoritative theorem title: Dual Support Equality -- Bounded-Remainder Drift -- Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='support_transport_drift_certificate',
    role=TheoremRole.LEFT,
    authoritative_title='Dual Support Equality – Bounded-Remainder Drift – Law',
    authoritative_title_tex='Dual Support Equality -- Bounded-Remainder Drift -- Law',
    equation_labels=('eq:drv_qenn_b04_1b', 'eq:drv_qenn_b04_theorem_1b', 'eq:drv_qenn_b04_res_1b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

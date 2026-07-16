'Authoritative theorem title: Subluminal Transport with Coherent Lag.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='subluminal_gw_transport_and_em_gw_lag_null_lag_correspondence',
    role=TheoremRole.LEFT,
    authoritative_title='Subluminal Transport with Coherent Lag',
    authoritative_title_tex='Subluminal Transport with Coherent Lag',
    equation_labels=('eq:grw04_gw_lag_order_parameter_1a', 'eq:grw04_gw_lag_branch_condition_1a', 'eq:gw_lag_transport_operational_1a', 'eq:gw_lag_distance_trend_1a', 'eq:gw_lag_bandavg_1a', 'eq:gw_lag_direct_1a', 'eq:gw_lag_derivative_1a', 'eq:gw_lag_regression_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

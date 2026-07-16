'Authoritative theorem title: Null Lag Correspondence (GR Limit).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='subluminal_gw_transport_and_em_gw_lag_null_lag_correspondence',
    role=TheoremRole.RIGHT,
    authoritative_title='Null Lag Correspondence (GR Limit)',
    authoritative_title_tex='Null Lag Correspondence (GR Limit)',
    equation_labels=('eq:grw04_gw_lag_order_parameter_2a', 'eq:grw04_gw_lag_branch_condition_2a', 'eq:gw_lag_null_2a', 'eq:gw_lag_derivs_null_2a', 'eq:gw_lag_beta_null_2a', 'eq:gw_lag_eta_2a', 'eq:gw_lag_bound_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

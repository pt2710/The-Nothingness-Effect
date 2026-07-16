'Authoritative theorem title: Subluminal GW Transport \\& EM--GW Lag $\\leftrightarrow$ Null Lag Correspondence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='subluminal_gw_transport_and_em_gw_lag_null_lag_correspondence',
    role=TheoremRole.CROSS,
    authoritative_title='Subluminal GW Transport \\& EM–GW Lag <-> Null Lag Correspondence',
    authoritative_title_tex='Subluminal GW Transport \\& EM--GW Lag $\\leftrightarrow$ Null Lag Correspondence',
    equation_labels=('eq:grw04_gw_lag_status_1a2a', 'eq:gw_lag_transport_operational_1a2a', 'eq:gw_speed_defect_dfi_1a2a', 'eq:gw_lag_sign_stability_1a2a', 'eq:gw_lag_frequency_slope_1a2a', 'eq:gw_lag_distance_trend_1a2a', 'eq:gw_lag_equivalence_operational_1a2a', 'eq:gw_lag_equivalence_proof_1a2a', 'eq:gw_lag_bound_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

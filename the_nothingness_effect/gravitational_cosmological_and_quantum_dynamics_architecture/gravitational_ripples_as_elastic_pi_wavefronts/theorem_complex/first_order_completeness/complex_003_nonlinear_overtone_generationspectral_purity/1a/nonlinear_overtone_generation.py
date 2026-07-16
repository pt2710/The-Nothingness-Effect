'Authoritative theorem title: Nonlinear Overtone Generation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='nonlinear_overtone_generation_spectral_purity',
    role=TheoremRole.LEFT,
    authoritative_title='Nonlinear Overtone Generation',
    authoritative_title_tex='Nonlinear Overtone Generation',
    equation_labels=('eq:grw03_overtone_purity_order_parameter_1a', 'eq:grw03_overtone_purity_branch_condition_1a', 'eq:ratio_3f_2f_1a', 'eq:amp_eqs_1a', 'eq:phase_bound_1a', 'eq:phase_sensitivity_1a', 'eq:cos_identity_1a', 'eq:harm_proj_1a', 'eq:dP_dA_1a', 'eq:limit_small_amp_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

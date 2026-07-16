'Authoritative theorem title: Non-Meyer/Diffuse Support.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='meyer_cut_and_project_structure_non_meyer_diffuse_support',
    role=TheoremRole.RIGHT,
    authoritative_title='Non-Meyer/Diffuse Support',
    authoritative_title_tex='Non-Meyer/Diffuse Support',
    equation_labels=('eq:dtqc_meyer_cap_nonmeyer_criterion_2a', 'eq:dtqc_meyer_cap_contmass_2a', 'eq:dtqc_meyer_cap_paircorr_2a', 'eq:dtqc_meyer_cap_L2mass_2a', 'eq:dtqc_meyer_cap_lb_contmass_2a', 'eq:dtqc_meyer_cap_testfn_lb_2a', 'eq:dtqc_meyer_cap_nonmeyer_indicator_2a'),
    implementation_status='blocked',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

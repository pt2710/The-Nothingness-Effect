'Authoritative theorem title: Meyer Cut-and-Project Structure $\\leftrightarrow$ Non-Meyer/Diffuse Support.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='meyer_cut_and_project_structure_non_meyer_diffuse_support',
    role=TheoremRole.CROSS,
    authoritative_title='Meyer Cut-and-Project Structure <-> Non-Meyer/Diffuse Support',
    authoritative_title_tex='Meyer Cut-and-Project Structure $\\leftrightarrow$ Non-Meyer/Diffuse Support',
    equation_labels=('eq:dtqc05_typed_obstruction_class', 'eq:dtqc05_joint_status_1a2a', 'eq:dtqc_meyer_cap_lattice_window_1a2a', 'eq:dtqc_meyer_cap_modelset_1a2a', 'eq:dtqc_meyer_cap_ud_rd_1a2a', 'eq:dtqc_meyer_cap_meyer_inclusion_1a2a', 'eq:dtqc_meyer_cap_autocorr_1a2a', 'eq:dtqc_meyer_cap_pp_diffraction_1a2a', 'eq:dtqc_meyer_cap_structure_factor_1a2a', 'eq:dtqc_meyer_cap_equiv_1a2a', 'eq:dtqc_meyer_cap_poisson_equiv_1a2a', 'eq:dtqc_meyer_cap_support_spectrum_equiv_1a2a', 'eq:dtqc_meyer_cap_diag_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

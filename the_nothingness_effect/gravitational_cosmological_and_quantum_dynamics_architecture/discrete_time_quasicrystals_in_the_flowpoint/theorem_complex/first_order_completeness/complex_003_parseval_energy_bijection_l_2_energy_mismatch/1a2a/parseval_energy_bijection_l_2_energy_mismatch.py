'Authoritative theorem title: Parseval Energy Bijection $\\leftrightarrow$ $L^2$ Energy Mismatch.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='parseval_energy_bijection_l_2_energy_mismatch',
    role=TheoremRole.CROSS,
    authoritative_title='Parseval Energy Bijection <-> L^2 Energy Mismatch',
    authoritative_title_tex='Parseval Energy Bijection $\\leftrightarrow$ $L^2$ Energy Mismatch',
    equation_labels=('eq:dtqc03_joint_status_1a2a', 'eq:psv_basis_orthonormality_1a2a', 'eq:psv_coeff_def_1a2a', 'eq:psv_projection_residual_1a2a', 'eq:psv_energy_decomposition_1a2a', 'eq:psv_energy_mismatch_nonneg_1a2a', 'eq:psv_normal_equations_1a2a', 'eq:gram_energy_identity_1a2a', 'eq:Gnormal_1a2a', 'eq:gram_expand_proof_1a2a', 'eq:grad_G_b_1a2a', 'eq:parseval_equivalence_statement_1a2a', 'eq:Jmin_zero_equiv_resid_zero_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Halo Structure Formation Duality.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='halo_structure_formation_duality',
    role=TheoremRole.CROSS,
    authoritative_title='Halo Structure Formation Duality',
    authoritative_title_tex='Halo Structure Formation Duality',
    equation_labels=('eq:ldg08_halo_status_1a2a', 'eq:halo_grad_cond_1a2a', 'eq:halo_grad_vanish_1a2a', 'eq:halo_diff_eq_1a2a', 'eq:halo_gradient_decay_1a2a', 'eq:halo_duality_lemma_1a2a', 'eq:halo_integral_lemma_1a2a', 'eq:halo_dual_proof_1a2a', 'eq:halo_dual_integral_proof_1a2a', 'eq:halo_dual_cor_1a2a', 'eq:halo_dual_gradient_cor_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

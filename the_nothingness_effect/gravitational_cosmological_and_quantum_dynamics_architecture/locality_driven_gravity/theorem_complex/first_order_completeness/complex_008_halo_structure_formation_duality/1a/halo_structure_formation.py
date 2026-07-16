'Authoritative theorem title: Halo Structure Formation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='halo_structure_formation_duality',
    role=TheoremRole.LEFT,
    authoritative_title='Halo Structure Formation',
    authoritative_title_tex='Halo Structure Formation',
    equation_labels=('eq:ldg08_halo_order_parameter_1a', 'eq:ldg08_halo_branch_condition_1a', 'eq:halo_structure_config_1a', 'eq:halo_growth_1a', 'eq:halo_dissolution_lemma_1a', 'eq:halo_flat_field_lemma_1a', 'eq:halo_gradient_proof_1a', 'eq:halo_evolution_proof_1a', 'eq:halo_persistence_cor_1a', 'eq:halo_static_cor_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

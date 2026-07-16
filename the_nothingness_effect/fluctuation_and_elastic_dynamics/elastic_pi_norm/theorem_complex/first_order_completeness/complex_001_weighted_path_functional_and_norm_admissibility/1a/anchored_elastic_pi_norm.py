'Authoritative theorem title: Anchored Elastic $\\pi$ Norm.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='weighted_path_functional_and_norm_admissibility',
    role=TheoremRole.LEFT,
    authoritative_title='Anchored Elastic pi Norm',
    authoritative_title_tex='Anchored Elastic $\\pi$ Norm',
    equation_labels=('eq:epinorm_c1_anchored_space_1a', 'eq:epinorm_c1_anchored_functional_1a', 'eq:epinorm_c1_difference_map_1a', 'eq:epinorm_c1_weighted_product_norm_1a', 'eq:epinorm_c1_homogeneity_difference_1a', 'eq:epinorm_c1_additivity_difference_1a', 'eq:epinorm_c1_constant_quotient_1a', 'eq:epinorm_c1_synthesis_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

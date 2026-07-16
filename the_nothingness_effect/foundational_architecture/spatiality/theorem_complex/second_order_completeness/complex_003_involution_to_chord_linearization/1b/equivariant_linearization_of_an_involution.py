'Authoritative theorem title: Equivariant Linearization of an Involution.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='involution_to_chord_linearization',
    role=TheoremRole.LEFT,
    authoritative_title='Equivariant Linearization of an Involution',
    authoritative_title_tex='Equivariant Linearization of an Involution',
    equation_labels=('eq:free_vector_space_on_involution_1b', 'eq:canonical_linearized_involution_1b', 'eq:canonical_affine_orbit_embedding_1b', 'eq:canonical_affine_involution_1b', 'eq:canonical_affine_equivariance_1b', 'eq:canonical_orbit_midpoint_1b', 'eq:canonical_orbit_chord_1b', 'eq:canonical_orbit_chord_decomposition_1b', 'eq:canonical_chord_metric_1b', 'eq:involution_spatial_chord_synthesis_1b', 'eq:involution_spatial_chord_pair_synthesis_1b', 'eq:canonical_affine_realization_principle_1b', 'eq:canonical_affine_orbit_classification_principle_1b'),
    implementation_status='blocked',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

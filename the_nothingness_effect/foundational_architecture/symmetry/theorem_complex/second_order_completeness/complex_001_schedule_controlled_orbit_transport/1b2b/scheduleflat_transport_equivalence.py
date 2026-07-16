'Authoritative theorem title: Schedule--Flat-Transport Equivalence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='schedule_controlled_orbit_transport',
    role=TheoremRole.CROSS,
    authoritative_title='Schedule–Flat-Transport Equivalence',
    authoritative_title_tex='Schedule--Flat-Transport Equivalence',
    equation_labels=('eq:symmetry_transport_involution', 'eq:symmetry_transport_schedule_parity', 'eq:symmetry_transport_tape_recursion', 'eq:symmetry_transport_parity_cocycle', 'eq:symmetry_transport_forward_map_j', 'eq:symmetry_transport_reverse_map_j', 'eq:symmetry_transport_equivalence_j', 'eq:symmetry_transport_bijection_j', 'eq:symmetry_transport_intertwiner_j', 'eq:symmetry_transport_naturality_j', 'eq:symmetry_transport_closed_path_holonomy_j', 'eq:symmetry_transport_mutual_reconstruction_synthesis_j', 'eq:symmetry_transport_equivalence_principle_j', 'eq:symmetry_transport_completeness_principle_j'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

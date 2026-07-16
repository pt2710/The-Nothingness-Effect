'Authoritative theorem title: Parity-Locked Reachability.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='signed_shortlex_cubic_transduction',
    role=TheoremRole.LEFT,
    authoritative_title='Parity-Locked Reachability',
    authoritative_title_tex='Parity-Locked Reachability',
    equation_labels=('eq:ci_b01_displacement_1b', 'eq:ci_b01_cube_action_1b', 'eq:ci_b01_state_operator_1b', 'eq:ci_b01_cube_parity_1b', 'eq:ci_b01_lattice_1b', 'eq:ci_b01_transducer_1b', 'eq:ci_b01_action_law_1b', 'eq:ci_b01_exact_image_1b', 'eq:ci_b01_parity_lock_1b', 'eq:ci_b01_double_parity_1b', 'eq:ci_b01_fibre_criterion_1b', 'eq:ci_b01_infinite_fibres_1b', 'eq:ci_b01_synthesis_1b', 'eq:ci_b01_transduction_principle_1b', 'eq:ci_b01_parity_principle_1b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

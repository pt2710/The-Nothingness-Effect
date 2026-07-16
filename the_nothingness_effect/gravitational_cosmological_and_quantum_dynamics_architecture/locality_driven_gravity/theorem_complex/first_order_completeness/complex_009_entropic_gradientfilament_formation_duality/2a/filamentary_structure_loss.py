'Authoritative theorem title: Filamentary Structure Loss (2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='entropic_gradient_filament_formation_duality',
    role=TheoremRole.RIGHT,
    authoritative_title='Filamentary Structure Loss',
    authoritative_title_tex='Filamentary Structure Loss (2A)',
    equation_labels=('eq:ldg09_filament_order_parameter_2a', 'eq:ldg09_filament_branch_condition_2a', 'eq:filament_dissolution_2a', 'eq:filament_decay_2a', 'eq:lemma_filament_dissolution_2a', 'eq:proof_filament_loss_2a', 'eq:proof_filament_decay_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

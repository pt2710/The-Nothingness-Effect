'Authoritative theorem title: Tail-Driven Mass Imbalance.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dfi_compatible_tail_control_tail_driven_mass_imbalance',
    role=TheoremRole.RIGHT,
    authoritative_title='Tail-Driven Mass Imbalance',
    authoritative_title_tex='Tail-Driven Mass Imbalance',
    equation_labels=('eq:dfi_cont_mass_bound_2a', 'eq:dfi_tail_lower_bound_2a', 'eq:dfi_tail_persistence_2a', 'eq:dfi_cont_survive_2a', 'eq:dfi_cont_derivative_2a', 'eq:dfi_mass_imbalance_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

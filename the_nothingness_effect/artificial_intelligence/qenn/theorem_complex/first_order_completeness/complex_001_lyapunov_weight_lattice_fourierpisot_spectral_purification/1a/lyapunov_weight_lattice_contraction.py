'Authoritative theorem title: Lyapunov Weight Lattice Contraction (1A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='lyapunov_weight_lattice_fourier_pisot_spectral_purification',
    role=TheoremRole.LEFT,
    authoritative_title='Lyapunov Weight Lattice Contraction',
    authoritative_title_tex='Lyapunov Weight Lattice Contraction (1A)',
    equation_labels=('eq:delta_recursive_bound_1a', 'eq:cauchy_from_geometric_1a', 'eq:total_variation_finite_1a', 'eq:cauchy_summable_1a', 'eq:epsilon_tail_control_1a', 'eq:pv_norm_contracts_1a', 'eq:lyapunov_exponent_negative_1a', 'eq:lyapunov_calc_bound_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

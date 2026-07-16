'Authoritative theorem title: Spectral Purity.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='nonlinear_overtone_generation_spectral_purity',
    role=TheoremRole.RIGHT,
    authoritative_title='Spectral Purity',
    authoritative_title_tex='Spectral Purity',
    equation_labels=('eq:grw03_overtone_purity_order_parameter_2a', 'eq:grw03_overtone_purity_branch_condition_2a', 'eq:undefined_phase_2a', 'eq:lin_fourier_2a', 'eq:limit_zero_coupling_2a', 'eq:proj_zero_2a', 'eq:diagonal_evolution_2a', 'eq:orthogonality_2a', 'eq:xi_bound_2a', 'eq:small_amp_limit_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

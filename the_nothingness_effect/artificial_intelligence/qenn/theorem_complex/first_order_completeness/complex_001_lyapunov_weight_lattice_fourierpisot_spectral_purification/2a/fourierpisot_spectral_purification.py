'Authoritative theorem title: Fourier--Pisot Spectral Purification (2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='lyapunov_weight_lattice_fourier_pisot_spectral_purification',
    role=TheoremRole.RIGHT,
    authoritative_title='Fourier–Pisot Spectral Purification',
    authoritative_title_tex='Fourier--Pisot Spectral Purification (2A)',
    equation_labels=('eq:uniform_gap_decay_2a', 'eq:tv_convergence_2a', 'eq:leakage_differential_2a', 'eq:moat_uniform_decay_2a', 'eq:integrated_leakage_bound_2a', 'eq:tv_purification_proof_2a', 'eq:parseval_pure_point_limit_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

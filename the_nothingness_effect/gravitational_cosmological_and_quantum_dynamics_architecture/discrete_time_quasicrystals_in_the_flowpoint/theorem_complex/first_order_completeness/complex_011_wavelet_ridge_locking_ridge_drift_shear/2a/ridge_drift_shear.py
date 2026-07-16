'Authoritative theorem title: Ridge Drift/Shear (2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='wavelet_ridge_locking_ridge_drift_shear',
    role=TheoremRole.RIGHT,
    authoritative_title='Ridge Drift/Shear',
    authoritative_title_tex='Ridge Drift/Shear (2A)',
    equation_labels=('eq:drift_positive_gap_2a', 'eq:modulated_shift_2a', 'eq:effective_shift_2a', 'eq:shear_leakage_equivalence_2a', 'eq:jensen_bound_2a', 'eq:shear_statistic_2a', 'eq:shear_gradient_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Nonlinear Leakage.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_invariance_of_support_nonlinear_leakage',
    role=TheoremRole.RIGHT,
    authoritative_title='Nonlinear Leakage',
    authoritative_title_tex='Nonlinear Leakage',
    equation_labels=('eq:epsi_support_minkowski_2a', 'eq:epsi_leakage_set_def_2a', 'eq:epsi_leakage_bias_lower_bound_2a', 'eq:epsi_single_shift_leak_2a', 'eq:epsi_persistence_offlattice_2a', 'eq:epsi_support_difference_2a', 'eq:epsi_best_approx_error_2a', 'eq:epsi_bias_floor_calc_2a'),
    implementation_status='blocked',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

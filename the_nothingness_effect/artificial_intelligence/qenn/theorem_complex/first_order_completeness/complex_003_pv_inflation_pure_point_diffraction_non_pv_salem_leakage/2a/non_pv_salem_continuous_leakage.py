'Authoritative theorem title: Non-PV/Salem $\\Rightarrow$ Continuous Leakage (2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='pv_inflation_pure_point_diffraction_non_pv_salem_leakage',
    role=TheoremRole.RIGHT,
    authoritative_title='Non-PV/Salem Continuous Leakage',
    authoritative_title_tex='Non-PV/Salem $\\Rightarrow$ Continuous Leakage (2A)',
    equation_labels=('eq:nonpv_salem_leakage_algebraic_align_2a', 'eq:nonpv_salem_leakage_algebraic_equation_2a', 'eq:nonpv_salem_leakage_calculus_align_2a', 'eq:nonpv_salem_leakage_calculus_equation_2a', 'eq:nondecay_internal_coords_algebraic_align_2a', 'eq:nondecay_internal_coords_algebraic_equation_2a', 'eq:nondecay_internal_coords_calculus_align_2a', 'eq:nondecay_internal_coords_calculus_equation_2a', 'eq:continuous_leakage_nonpv_algebraic_align_2a', 'eq:continuous_leakage_nonpv_algebraic_equation_2a', 'eq:continuous_leakage_nonpv_calculus_align_2a', 'eq:continuous_leakage_nonpv_calculus_equation_2a', 'eq:broadening_offlattice_algebraic_align_2a', 'eq:broadening_offlattice_algebraic_equation_2a', 'eq:broadening_offlattice_calculus_align_2a', 'eq:broadening_offlattice_calculus_equation_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

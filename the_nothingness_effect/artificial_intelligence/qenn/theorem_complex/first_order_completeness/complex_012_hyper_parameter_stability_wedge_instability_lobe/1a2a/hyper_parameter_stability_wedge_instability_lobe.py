'Authoritative theorem title: Hyper-Parameter Stability Wedge $\\leftrightarrow$ Instability Lobe (1A $\\leftrightarrow$ 2A).'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='hyper_parameter_stability_wedge_instability_lobe',
    role=TheoremRole.CROSS,
    authoritative_title='Hyper-Parameter Stability Wedge <-> Instability Lobe',
    authoritative_title_tex='Hyper-Parameter Stability Wedge $\\leftrightarrow$ Instability Lobe (1A $\\leftrightarrow$ 2A)',
    equation_labels=('eq:hyperparam_wedge_def_1a2a', 'eq:hyperparam_objective_phi_1a2a', 'eq:hyperparam_differential_phi_1a2a', 'eq:hyperparam_flow_monotonicity_1a2a', 'eq:boundary_active_set_1a2a', 'eq:boundary_characterization_1a2a', 'eq:normal_cone_wedge_1a2a', 'eq:sliding_boundary_flow_1a2a', 'eq:partition_identity_1a2a', 'eq:boundary_via_phi_1a2a', 'eq:implicit_function_boundary_1a2a', 'eq:boundary_crossing_flow_1a2a', 'eq:acceptance_region_1a2a', 'eq:acceptance_implications_1a2a', 'eq:screening_portability_calculus_align_1a2a', 'eq:screening_portability_calculus_equation_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

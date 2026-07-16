'Authoritative theorem title: Invertible Source–Transport–Detection Map $\\leftrightarrow$ Non-Invertible Degeneracy.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='invertible_source_transport_detection_map_non_invertible_degeneracy',
    role=TheoremRole.CROSS,
    authoritative_title='Invertible Source–Transport–Detection Map <-> Non-Invertible Degeneracy',
    authoritative_title_tex='Invertible Source–Transport–Detection Map $\\leftrightarrow$ Non-Invertible Degeneracy',
    equation_labels=('eq:grw10_source_transport_detection_status_1a2a', 'eq:fisher_metric_pd_1a2a', 'eq:global_injectivity_1a2a', 'eq:inverse_function_rank_1a2a', 'eq:singular_fisher_null_1a2a', 'eq:kernel_equiv_1a2a', 'eq:det_equiv_1a2a', 'eq:strict_maximum_truth_1a2a', 'eq:flat_directions_1a2a', 'eq:biconditional_pd_injectivity_1a2a', 'eq:strict_extremum_unique_1a2a', 'eq:singular_nonunique_1a2a', 'eq:d_optimal_design_1a2a', 'eq:design_constraints_1a2a', 'eq:design_gradient_1a2a', 'eq:stationary_design_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Elastic Geometric Consistency $\\leftrightarrow$ Geometric Degeneracy.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_geometric_consistency_geometric_degeneracy',
    role=TheoremRole.CROSS,
    authoritative_title='Elastic Geometric Consistency <-> Geometric Degeneracy',
    authoritative_title_tex='Elastic Geometric Consistency $\\leftrightarrow$ Geometric Degeneracy',
    equation_labels=('eq:edi08_global_injectivity_contract', 'eq:edi08_local_regular_contract', 'eq:edi08_first_order_degeneracy_contract', 'eq:edi08_geometric_consistency_status_1a2a', 'eq:elastic_geom_injectivity_1a2a', 'eq:elastic_geom_stability_1a2a', 'eq:elastic_geom_degeneracy_1a2a', 'eq:elastic_geom_dual_closure_1a2a', 'eq:jacobian_injectivity_1a2a', 'eq:jacobian_degeneracy_1a2a', 'eq:kernel_criterion_1a2a', 'eq:diagnostic_statement_1a2a', 'eq:rank_semicont_1a2a', 'eq:degeneracy_onset_1a2a', 'eq:rank_duality_1a2a', 'eq:dual_closure_conclusion_1a2a', 'eq:ift_regions_1a2a', 'eq:rank_partition_1a2a', 'eq:frontier_set_1a2a', 'eq:frontier_switch_1a2a', 'eq:det_frontier_1a2a', 'eq:generic_restoration_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

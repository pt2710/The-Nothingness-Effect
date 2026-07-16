'Authoritative theorem title: Collapse Divergence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='observation_induced_collapse_and_collapse_divergence',
    role=TheoremRole.RIGHT,
    authoritative_title='Collapse Divergence',
    authoritative_title_tex='Collapse Divergence',
    equation_labels=('eq:obs01_general_average_2a', 'eq:obs01_non_cauchy_witness_2a', 'eq:obs01_no_collapse_limit_2a', 'eq:obs01_liminf_limsup_gap_2a', 'eq:obs01_synthesis_2a', 'eq:std_obs01_principle_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

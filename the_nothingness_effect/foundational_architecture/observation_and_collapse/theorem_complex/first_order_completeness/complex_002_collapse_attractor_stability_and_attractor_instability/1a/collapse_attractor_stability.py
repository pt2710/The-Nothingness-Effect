'Authoritative theorem title: Collapse-Attractor Stability.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='collapse_attractor_stability_and_attractor_instability',
    role=TheoremRole.LEFT,
    authoritative_title='Collapse-Attractor Stability',
    authoritative_title_tex='Collapse-Attractor Stability',
    equation_labels=('eq:obs02_attractor_limit_1a', 'eq:obs02_zero_mean_perturbation_1a', 'eq:obs02_stability_hypotheses_1a', 'eq:obs02_stability_conclusion_1a', 'eq:obs02_stability_error_bound_1a', 'eq:obs02_synthesis_1a', 'eq:std_obs02_principle_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

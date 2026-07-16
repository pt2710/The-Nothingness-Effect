'Authoritative theorem title: Unique Collapse under Ergodic Generation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='uniqueness_and_non_uniqueness_of_collapse',
    role=TheoremRole.LEFT,
    authoritative_title='Unique Collapse under Ergodic Generation',
    authoritative_title_tex='Unique Collapse under Ergodic Generation',
    equation_labels=('eq:obs03_pathwise_unique_1a', 'eq:obs03_ensemble_unique_1a', 'eq:obs03_ergodic_unique_limit_1a', 'eq:obs03_strong_law_1a', 'eq:obs03_synthesis_1a', 'eq:std_obs03_principle_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

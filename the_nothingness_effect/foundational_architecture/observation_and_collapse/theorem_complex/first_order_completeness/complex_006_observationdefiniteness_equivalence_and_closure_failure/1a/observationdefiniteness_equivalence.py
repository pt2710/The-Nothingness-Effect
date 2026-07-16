'Authoritative theorem title: Observation--Definiteness Equivalence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='observation_definiteness_equivalence_and_closure_failure',
    role=TheoremRole.LEFT,
    authoritative_title='Observation–Definiteness Equivalence',
    authoritative_title_tex='Observation--Definiteness Equivalence',
    equation_labels=('eq:obs09_local_definiteness_1a', 'eq:obs09_stable_state_1a', 'eq:obs09_global_equivalence_1a', 'eq:obs09_output_fixedness_1a', 'eq:obs09_eventual_idempotence_1a', 'eq:obs09_synthesis_1a', 'eq:std_obs09_principle_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Failure of Positive Definiteness on Unanchored Sequences.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='weighted_path_functional_and_norm_admissibility',
    role=TheoremRole.RIGHT,
    authoritative_title='Failure of Positive Definiteness on Unanchored Sequences',
    authoritative_title_tex='Failure of Positive Definiteness on Unanchored Sequences',
    equation_labels=('eq:epinorm_c1_unanchored_functional_2a', 'eq:epinorm_c1_constant_null_2a', 'eq:epinorm_c1_constant_transition_zero_2a', 'eq:epinorm_c1_synthesis_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

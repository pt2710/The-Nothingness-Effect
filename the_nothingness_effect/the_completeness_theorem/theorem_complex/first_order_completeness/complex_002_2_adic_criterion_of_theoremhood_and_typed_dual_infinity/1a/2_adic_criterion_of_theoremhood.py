'Authoritative theorem title: 2-Adic Criterion of Theoremhood.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='2_adic_criterion_of_theoremhood_and_typed_dual_infinity',
    role=TheoremRole.LEFT,
    authoritative_title='2-Adic Criterion of Theoremhood',
    authoritative_title_tex='2-Adic Criterion of Theoremhood',
    equation_labels=(),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

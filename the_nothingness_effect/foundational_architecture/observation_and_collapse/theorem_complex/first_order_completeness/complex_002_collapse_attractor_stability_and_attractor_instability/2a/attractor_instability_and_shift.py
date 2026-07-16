'Authoritative theorem title: Attractor Instability and Shift.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='collapse_attractor_stability_and_attractor_instability',
    role=TheoremRole.RIGHT,
    authoritative_title='Attractor Instability and Shift',
    authoritative_title_tex='Attractor Instability and Shift',
    equation_labels=('eq:obs02_defect_sequence_2a', 'eq:obs02_shifted_attractor_2a', 'eq:obs02_unbounded_zero_mean_example_2a', 'eq:obs02_synthesis_2a', 'eq:std_obs02_principle_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

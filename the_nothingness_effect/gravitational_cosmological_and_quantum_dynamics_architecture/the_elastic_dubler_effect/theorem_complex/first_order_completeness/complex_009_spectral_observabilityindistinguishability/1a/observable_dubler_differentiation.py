'Authoritative theorem title: Observable Dubler Differentiation.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='spectral_observability_indistinguishability',
    role=TheoremRole.LEFT,
    authoritative_title='Observable Dubler Differentiation',
    authoritative_title_tex='Observable Dubler Differentiation',
    equation_labels=('eq:ed09_observable_condition_1a', 'eq:ed09_observation_kernel_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

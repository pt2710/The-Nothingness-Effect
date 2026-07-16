'Authoritative theorem title: Dual Realizability of Spectral Structures.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dual_realizability_and_the_missing_dual_defect',
    role=TheoremRole.LEFT,
    authoritative_title='Dual Realizability of Spectral Structures',
    authoritative_title_tex='Dual Realizability of Spectral Structures',
    equation_labels=('eq:std_soi_coordinate_realizability_1a',),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Differential Role Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_dubler_e_curvature_duality',
    role=TheoremRole.CROSS,
    authoritative_title='Differential Role Classification',
    authoritative_title_tex='Differential Role Classification',
    equation_labels=('eq:ed03_preserved_proportionality_1a2a', 'eq:ed03_curvature_status_vector_1a2a', 'eq:ed03_curvature_implication_1a2a', 'eq:ed03_curvature_closure_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

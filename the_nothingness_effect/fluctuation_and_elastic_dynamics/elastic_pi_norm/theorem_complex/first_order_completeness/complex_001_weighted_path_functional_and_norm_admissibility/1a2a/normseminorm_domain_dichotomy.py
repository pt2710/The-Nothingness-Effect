'Authoritative theorem title: Norm--Seminorm Domain Dichotomy.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='weighted_path_functional_and_norm_admissibility',
    role=TheoremRole.CROSS,
    authoritative_title='Norm–Seminorm Domain Dichotomy',
    authoritative_title_tex='Norm--Seminorm Domain Dichotomy',
    equation_labels=('eq:epinorm_c1_preserved_path_functional_1a2a', 'eq:epinorm_c1_domain_status_1a2a', 'eq:epinorm_c1_kernel_definition_1a2a', 'eq:epinorm_c1_joint_synthesis_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Weight Regularity Dichotomy.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='elastic_field_ratios_and_weight_regularity',
    role=TheoremRole.CROSS,
    authoritative_title='Weight Regularity Dichotomy',
    authoritative_title_tex='Weight Regularity Dichotomy',
    equation_labels=('eq:epinorm_c2_preserved_ratio_1a2a', 'eq:epinorm_c2_weight_state_1a2a', 'eq:epinorm_c2_positive_finite_criterion_1a2a', 'eq:epinorm_c2_joint_synthesis_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

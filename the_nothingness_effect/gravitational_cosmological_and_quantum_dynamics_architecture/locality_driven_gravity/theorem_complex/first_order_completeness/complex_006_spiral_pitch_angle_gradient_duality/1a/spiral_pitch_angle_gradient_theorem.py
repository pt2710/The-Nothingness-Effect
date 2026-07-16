'Authoritative theorem title: Spiral Pitch-Angle Gradient Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='spiral_pitch_angle_gradient_duality',
    role=TheoremRole.LEFT,
    authoritative_title='Spiral Pitch-Angle Gradient Theorem',
    authoritative_title_tex='Spiral Pitch-Angle Gradient Theorem',
    equation_labels=('eq:ldg06_pitch_angle_order_parameter_1a', 'eq:ldg06_pitch_angle_branch_condition_1a', 'eq:pitch_angle_unique_1a', 'eq:static_pitch_angle_1a', 'eq:gradient_pitch_lemma_1a', 'eq:gradient_pitch_lemma_static_1a', 'eq:proof_pitch_angle_unique_1a', 'eq:predictive_spiral_1a', 'eq:static_spiral_corollary_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

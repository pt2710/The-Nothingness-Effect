'Authoritative theorem title: Spiral Pitch-Angle Gradient Duality.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='spiral_pitch_angle_gradient_duality',
    role=TheoremRole.CROSS,
    authoritative_title='Spiral Pitch-Angle Gradient Duality',
    authoritative_title_tex='Spiral Pitch-Angle Gradient Duality',
    equation_labels=('eq:ldg06_pitch_angle_status_1a2a', 'eq:pitch_angle_unique_1a2a', 'eq:pitch_angle_indeterminate_1a2a', 'eq:theta_p_time_derivative_1a2a', 'eq:theta_p_static_entropy_1a2a', 'eq:closure_lemma_spiral_1a2a', 'eq:closure_lemma_spiral_calculus_1a2a', 'eq:dual_closure_proof_spiral_1a2a', 'eq:dual_corollary_spiral_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

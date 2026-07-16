'Authoritative theorem title: Emergent Spiral Density-Wave $\\leftrightarrow$ Spiral Dissolution.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='emergent_spiral_density_wave_spiral_dissolution',
    role=TheoremRole.CROSS,
    authoritative_title='Emergent Spiral Density-Wave <-> Spiral Dissolution',
    authoritative_title_tex='Emergent Spiral Density-Wave $\\leftrightarrow$ Spiral Dissolution',
    equation_labels=('eq:ldg02_spiral_density_wave_status_1a2a', 'eq:spiral_pitch_spiral_density_wave_1a2a', 'eq:locality_length_spiral_density_wave_1a2a', 'eq:curvature_gradient_dissolution_1a2a', 'eq:spiral_pitch_gradient_derivative_1a2a', 'eq:gradient_vanishes_spiral_density_wave_1a2a', 'eq:existence_spiral_arms_1a2a', 'eq:loss_spiral_arms_1a2a', 'eq:lemma_pitch_gradient_1a2a', 'eq:proof_pitch_gradient_duality_1a2a', 'eq:corollary_pitch_limit_1a2a', 'eq:corollary_pitch_limit_calculus_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

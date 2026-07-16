'Authoritative theorem title: Common-State Cosmological Wave Projection.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='wave_sector_and_expansion_sector_cosmological_projection',
    role=TheoremRole.LEFT,
    authoritative_title='Common-State Cosmological Wave Projection',
    authoritative_title_tex='Common-State Cosmological Wave Projection',
    equation_labels=('eq:sc04_wave_norm_1a', 'eq:sc04_wave_bound_1a', 'eq:sc04_wave_residual_1a', 'eq:sc04_product_operator_1a', 'eq:sc04_wave_stability_1a', 'eq:sc04_wave_synthesis_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

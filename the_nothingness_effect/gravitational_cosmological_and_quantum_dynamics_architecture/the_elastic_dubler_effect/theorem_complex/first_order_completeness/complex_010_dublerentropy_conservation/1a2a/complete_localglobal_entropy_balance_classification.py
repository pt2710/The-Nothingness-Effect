'Authoritative theorem title: Complete Local--Global Entropy Balance Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dubler_entropy_conservation',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Local–Global Entropy Balance Classification',
    authoritative_title_tex='Complete Local--Global Entropy Balance Classification',
    equation_labels=('eq:ed10_entropy_local_residual_1a2a', 'eq:ed10_entropy_boundary_flux_1a2a', 'eq:ed10_entropy_global_residual_1a2a', 'eq:ed10_entropy_conservation_closure_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

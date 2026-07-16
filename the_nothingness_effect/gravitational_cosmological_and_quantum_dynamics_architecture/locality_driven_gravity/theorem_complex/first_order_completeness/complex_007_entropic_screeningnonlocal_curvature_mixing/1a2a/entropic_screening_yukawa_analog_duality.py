'Authoritative theorem title: Entropic Screening (Yukawa Analog) Duality.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='entropic_screening_nonlocal_curvature_mixing',
    role=TheoremRole.CROSS,
    authoritative_title='Entropic Screening (Yukawa Analog) Duality',
    authoritative_title_tex='Entropic Screening (Yukawa Analog) Duality',
    equation_labels=('eq:ldg07_screening_status_1a2a', 'eq:entropic_screening_yukawa_operator_1a2a', 'eq:entropic_screening_yukawa_decay_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Black-Hole Observability--Triviality and Regularity Joint Closure.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='black_hole_observability_triviality_and_regularity',
    role=TheoremRole.CROSS,
    authoritative_title='Black-Hole Observability–Triviality and Regularity Joint Closure',
    authoritative_title_tex='Black-Hole Observability--Triviality and Regularity Joint Closure',
    equation_labels=('eq:bhhr04_black_hole_observability_status_1a2a', 'eq:bhhr04_black_hole_observability_joint_implications_1a2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

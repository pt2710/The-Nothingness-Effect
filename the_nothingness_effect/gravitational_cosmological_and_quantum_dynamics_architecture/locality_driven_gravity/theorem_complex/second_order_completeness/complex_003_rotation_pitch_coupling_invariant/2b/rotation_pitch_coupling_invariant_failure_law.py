'Authoritative theorem title: Rotation-Pitch Coupling Invariant Failure Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='rotation_pitch_coupling_invariant',
    role=TheoremRole.RIGHT,
    authoritative_title='Rotation-Pitch Coupling Invariant Failure Law',
    authoritative_title_tex='Rotation-Pitch Coupling Invariant Failure Law',
    equation_labels=('eq:drv_ldg_b03_2b', 'eq:drv_ldg_b03_theorem_2b', 'eq:drv_ldg_b03_res_2b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

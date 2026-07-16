'Authoritative theorem title: Equivariant Positive-Orientation Transport.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='flowpoint_unity_orientation_and_integer_unfolding',
    role=TheoremRole.LEFT,
    authoritative_title='Equivariant Positive-Orientation Transport',
    authoritative_title_tex='Equivariant Positive-Orientation Transport',
    equation_labels=('eq:tne_mpl_tc_chi_plus_1a', 'eq:tne_mpl_tc_positive_equivariance_1a', 'eq:tne_mpl_tc_orbit_transport_1a', 'eq:tne_mpl_tc_positive_spectrum_1a', 'eq:tne_mpl_tc_positive_synthesis_1a', 'eq:tne_mpl_tc_positive_principle_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

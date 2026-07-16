'Authoritative theorem title: Equivariant Counter-Orientation Transport.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='flowpoint_unity_orientation_and_integer_unfolding',
    role=TheoremRole.RIGHT,
    authoritative_title='Equivariant Counter-Orientation Transport',
    authoritative_title_tex='Equivariant Counter-Orientation Transport',
    equation_labels=('eq:tne_mpl_tc_chi_minus_2a', 'eq:tne_mpl_tc_negative_equivariance_2a', 'eq:tne_mpl_tc_counter_orbit_transport_2a', 'eq:tne_mpl_tc_negative_spectrum_2a', 'eq:tne_mpl_tc_negative_synthesis_2a', 'eq:tne_mpl_tc_negative_principle_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Intrinsic Cyclic Flowpoint Time.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='phase_clock',
    role=TheoremRole.LEFT,
    authoritative_title='Intrinsic Cyclic Flowpoint Time',
    authoritative_title_tex='Intrinsic Cyclic Flowpoint Time',
    equation_labels=('eq:origin_free_phase_time_torsor_definition_1a', 'eq:origin_free_phase_time_shift_definition_1a', 'eq:origin_free_phase_time_shift_properties_1a', 'eq:intrinsic_cyclic_time_recursion_1a', 'eq:intrinsic_cyclic_time_periodicity_1a', 'eq:intrinsic_cyclic_time_order_invariance_1a', 'eq:torsor_origin_coordinate_bijection_1a', 'eq:torsor_origin_shift_1a', 'eq:torsor_origin_coordinate_shift_1a', 'eq:torsor_no_invariant_origin_1a', 'eq:phase_origin_clock_sequence_1a', 'eq:phase_origin_gauge_shift_1a', 'eq:phase_origin_period_invariance_1a', 'eq:intrinsic_flowpoint_time_principle_involution_1a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

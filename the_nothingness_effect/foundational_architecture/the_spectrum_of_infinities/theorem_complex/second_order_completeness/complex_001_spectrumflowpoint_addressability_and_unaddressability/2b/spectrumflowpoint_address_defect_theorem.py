'Authoritative theorem title: Spectrum--Flowpoint Address-Defect Theorem.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='spectrum_flowpoint_addressability_and_unaddressability',
    role=TheoremRole.RIGHT,
    authoritative_title='Spectrum–Flowpoint Address-Defect Theorem',
    authoritative_title_tex='Spectrum--Flowpoint Address-Defect Theorem',
    equation_labels=('eq:soi_flowpoint_branch_composition_2b', 'eq:soi_flowpoint_omission_set_2b', 'eq:soi_flowpoint_collision_set_2b', 'eq:soi_flowpoint_range_gap_2b', 'eq:soi_flowpoint_calibration_defect_2b', 'eq:soi_flowpoint_representation_residual_2b', 'eq:soi_flowpoint_unaddressability_modes_2b', 'eq:soi_flowpoint_absolute_calibration_defect_2b', 'eq:soi_flowpoint_complete_address_criterion_2b', 'eq:soi_flowpoint_negative_symmetric_synthesis_2b', 'eq:std_soi_address_defect_2b'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

'Authoritative theorem title: Exact Affine History--Field Equivalence.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='affine_history_field',
    role=TheoremRole.CROSS,
    authoritative_title='Exact Affine History–Field Equivalence',
    authoritative_title_tex='Exact Affine History--Field Equivalence',
    equation_labels=('eq:drv_flowpoint_c01_interface_data', 'eq:drv_flowpoint_c01_balance_internal_map', 'eq:drv_flowpoint_c01_balance_internal_inverse', 'eq:drv_flowpoint_c01_internal_affine_reflection', 'eq:drv_flowpoint_c01_spatial_involution', 'eq:drv_flowpoint_c01_spatial_center', 'eq:drv_flowpoint_c01_construction_map_joint', 'eq:drv_flowpoint_c01_reconstruction_type_joint', 'eq:drv_flowpoint_c01_orientation_involution_joint', 'eq:drv_flowpoint_c01_forget_orientation_joint', 'eq:drv_flowpoint_c01_field_residual_joint', 'eq:drv_flowpoint_c01_inverse_maps_joint', 'eq:drv_flowpoint_c01_orientation_gauge_joint', 'eq:drv_flowpoint_c01_residual_characterization_joint', 'eq:drv_flowpoint_c01_gauge_components_joint', 'eq:drv_flowpoint_c01_gauge_field_identity_joint', 'eq:drv_flowpoint_c01_unoriented_quotient_joint', 'eq:drv_flowpoint_c01_two_records_paradox_joint', 'eq:drv_flowpoint_c01_synthesis_joint', 'eq:drv_flowpoint_c01_principle_joint'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

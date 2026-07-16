'Authoritative theorem title: Local-Residue--Exposure Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='observable_locality_and_infinite_exposure',
    role=TheoremRole.CROSS,
    authoritative_title='Local-Residue–Exposure Classification',
    authoritative_title_tex='Local-Residue--Exposure Classification',
    equation_labels=('eq:soi12_source_temporal_b_1c2c', 'eq:soi12_source_spectral_b_1c2c', 'eq:soi12_branch_exchange_1c2c', 'eq:soi12_spatial_local_readout_1c2c', 'eq:soi12_spatial_exterior_residual_1c2c', 'eq:soi12_joint_status_1c2c', 'eq:std_soi12_synthesis_joint', 'eq:std_soi12_joint'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

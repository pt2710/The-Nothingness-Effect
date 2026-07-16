'Authoritative theorem title: Lyapunov Weight Lattice $\\leftrightarrow$ Fourier--Pisot Spectral Purification -- PV Inflation (Pure-Point Diffraction) $\\leftrightarrow$ Non-PV/Salem Leakage.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='lyapunov_parseval_training_isometry_closure',
    role=TheoremRole.CROSS,
    authoritative_title='Lyapunov Weight Lattice <-> Fourier–Pisot Spectral Purification – PV Inflation (Pure-Point Diffraction) <-> Non-PV/Salem Leakage',
    authoritative_title_tex='Lyapunov Weight Lattice $\\leftrightarrow$ Fourier--Pisot Spectral Purification -- PV Inflation (Pure-Point Diffraction) $\\leftrightarrow$ Non-PV/Salem Leakage',
    equation_labels=('eq:drv_qenn_c01_spatial_carrier', 'eq:drv_qenn_c01_joint', 'eq:drv_qenn_c01_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

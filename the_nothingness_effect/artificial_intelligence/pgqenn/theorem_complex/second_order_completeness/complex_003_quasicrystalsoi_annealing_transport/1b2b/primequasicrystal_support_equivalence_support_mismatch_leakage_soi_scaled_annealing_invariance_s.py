'Authoritative theorem title: Prime–Quasicrystal Support Equivalence $\\leftrightarrow$ Support Mismatch/Leakage -- SOI-Scaled Annealing Invariance $\\leftrightarrow$ SOI Mis-Scaling / Spurious Entropy.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='quasicrystal_soi_annealing_transport',
    role=TheoremRole.CROSS,
    authoritative_title='Prime–Quasicrystal Support Equivalence <-> Support Mismatch/Leakage – SOI-Scaled Annealing Invariance <-> SOI Mis-Scaling / Spurious Entropy',
    authoritative_title_tex='Prime–Quasicrystal Support Equivalence $\\leftrightarrow$ Support Mismatch/Leakage -- SOI-Scaled Annealing Invariance $\\leftrightarrow$ SOI Mis-Scaling / Spurious Entropy',
    equation_labels=('eq:drv_pgqenn_b03_product_carrier', 'eq:drv_pgqenn_b03_joint', 'eq:drv_pgqenn_b03_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

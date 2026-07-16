'Authoritative theorem title: Parity-Orthogonal Optimization $\\leftrightarrow$ Cross-Parity Gradient Contamination -- Prime-Shell Growth Regularity $\\leftrightarrow$ Shell Instability / Phase Slips.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='parity_orthogonal_shell_growth_connection',
    role=TheoremRole.CROSS,
    authoritative_title='Parity-Orthogonal Optimization <-> Cross-Parity Gradient Contamination – Prime-Shell Growth Regularity <-> Shell Instability / Phase Slips',
    authoritative_title_tex='Parity-Orthogonal Optimization $\\leftrightarrow$ Cross-Parity Gradient Contamination -- Prime-Shell Growth Regularity $\\leftrightarrow$ Shell Instability / Phase Slips',
    equation_labels=('eq:drv_pgqenn_b05_product_carrier', 'eq:drv_pgqenn_b05_joint', 'eq:drv_pgqenn_b05_exchange_square'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

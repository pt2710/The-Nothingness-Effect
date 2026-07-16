'Authoritative theorem title: Cross-Parity Gradient Contamination -- Shell Instability / Phase Slips -- Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='parity_orthogonal_shell_growth_connection',
    role=TheoremRole.RIGHT,
    authoritative_title='Cross-Parity Gradient Contamination – Shell Instability / Phase Slips – Law',
    authoritative_title_tex='Cross-Parity Gradient Contamination -- Shell Instability / Phase Slips -- Law',
    equation_labels=('eq:drv_pgqenn_b05_2b', 'eq:drv_pgqenn_b05_theorem_2b', 'eq:drv_pgqenn_b05_res_2b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

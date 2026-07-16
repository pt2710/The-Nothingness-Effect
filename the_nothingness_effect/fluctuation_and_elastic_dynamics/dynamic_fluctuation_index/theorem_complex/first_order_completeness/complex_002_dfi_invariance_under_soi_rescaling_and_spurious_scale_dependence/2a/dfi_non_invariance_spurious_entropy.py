'Authoritative theorem title: DFI Non-Invariance/Spurious Entropy.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dfi_invariance_under_soi_rescaling_and_spurious_scale_dependence',
    role=TheoremRole.RIGHT,
    authoritative_title='DFI Non-Invariance/Spurious Entropy',
    authoritative_title_tex='DFI Non-Invariance/Spurious Entropy',
    equation_labels=('eq:dfi02_scale_defect_2a', 'eq:dfi02_counterexample_before_2a', 'eq:dfi02_counterexample_after_2a', 'eq:dfi02_defect_decomposition_2a', 'eq:dfi02_spurious_vectors_2a', 'eq:dfi02_synthesis_2a'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

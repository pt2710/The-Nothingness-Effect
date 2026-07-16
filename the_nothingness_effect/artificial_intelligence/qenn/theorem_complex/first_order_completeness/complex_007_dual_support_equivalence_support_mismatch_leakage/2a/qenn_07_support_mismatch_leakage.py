'Authoritative theorem title: QENN 07 -- Support Mismatch/Leakage.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='qenn::dual_support_equivalence_support_mismatch_leakage',
    role=TheoremRole.RIGHT,
    authoritative_title='QENN 07 – Support Mismatch/Leakage',
    authoritative_title_tex='QENN 07 -- Support Mismatch/Leakage',
    equation_labels=('eq:support_mismatch_algebraic_align_2a', 'eq:support_mismatch_algebraic_equation_2a', 'eq:support_mismatch_calculus_align_2a', 'eq:support_mismatch_calculus_equation_2a', 'eq:drift_sidebanding_algebraic_align_2a', 'eq:drift_sidebanding_algebraic_equation_2a', 'eq:drift_sidebanding_calculus_align_2a', 'eq:drift_sidebanding_calculus_equation_2a', 'eq:contrapositive_dual_equality_algebraic_align_2a', 'eq:contrapositive_dual_equality_algebraic_equation_2a', 'eq:contrapositive_dual_equality_calculus_align_2a', 'eq:contrapositive_dual_equality_calculus_equation_2a', 'eq:parity_breaking_algebraic_align_2a', 'eq:parity_breaking_algebraic_equation_2a', 'eq:parity_breaking_calculus_align_2a', 'eq:parity_breaking_calculus_equation_2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

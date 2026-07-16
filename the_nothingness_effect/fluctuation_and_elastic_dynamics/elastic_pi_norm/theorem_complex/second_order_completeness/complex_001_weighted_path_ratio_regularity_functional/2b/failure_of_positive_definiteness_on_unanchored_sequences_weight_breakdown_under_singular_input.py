'Authoritative theorem title: Failure of Positive Definiteness on Unanchored Sequences -- Weight Breakdown under Singular Input.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='weighted_path_ratio_regularity_functional',
    role=TheoremRole.RIGHT,
    authoritative_title='Failure of Positive Definiteness on Unanchored Sequences – Weight Breakdown under Singular Input',
    authoritative_title_tex='Failure of Positive Definiteness on Unanchored Sequences -- Weight Breakdown under Singular Input',
    equation_labels=('eq:drv_epinorm_b01_2b', 'eq:drv_epinorm_b01_theorem_2b', 'eq:drv_epinorm_b01_res_2b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

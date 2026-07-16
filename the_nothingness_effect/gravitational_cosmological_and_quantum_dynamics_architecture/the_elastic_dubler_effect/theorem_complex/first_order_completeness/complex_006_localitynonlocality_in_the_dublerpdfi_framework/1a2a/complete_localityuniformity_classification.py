'Authoritative theorem title: Complete Locality--Uniformity Classification.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='locality_nonlocality_in_the_dubler_pdfi_framework',
    role=TheoremRole.CROSS,
    authoritative_title='Complete Locality–Uniformity Classification',
    authoritative_title_tex='Complete Locality--Uniformity Classification',
    equation_labels=('eq:ed06_locality_status_1a2a', 'eq:ed06_locality_coercive_bound_1a2a', 'eq:ed06_locality_closure_1a2a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

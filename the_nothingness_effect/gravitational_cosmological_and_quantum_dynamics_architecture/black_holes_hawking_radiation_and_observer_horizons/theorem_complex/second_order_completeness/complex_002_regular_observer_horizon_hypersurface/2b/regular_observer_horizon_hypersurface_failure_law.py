'Authoritative theorem title: Regular Observer-Horizon Hypersurface Failure Law.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='regular_observer_horizon_hypersurface',
    role=TheoremRole.RIGHT,
    authoritative_title='Regular Observer-Horizon Hypersurface Failure Law',
    authoritative_title_tex='Regular Observer-Horizon Hypersurface Failure Law',
    equation_labels=('eq:drv_bhhr_b02_2b', 'eq:drv_bhhr_b02_theorem_2b', 'eq:drv_bhhr_b02_res_2b'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

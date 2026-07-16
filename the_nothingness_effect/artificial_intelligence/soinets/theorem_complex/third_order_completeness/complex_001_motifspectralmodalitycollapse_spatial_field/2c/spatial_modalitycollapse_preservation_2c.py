'Authoritative theorem title: Spatial Modality--Collapse Preservation 2C.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='motif_spectral_modality_collapse_spatial_field',
    role=TheoremRole.RIGHT,
    authoritative_title='Spatial Modality–Collapse Preservation 2C',
    authoritative_title_tex='Spatial Modality--Collapse Preservation 2C',
    equation_labels=('eq:soinet29_definition_2c', 'eq:soinet29_residual_2c', 'eq:soinet29_theorem_2c', 'eq:soinet29_lemma_2c', 'eq:soinet29_corollary_2c'),
    implementation_status='implemented',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

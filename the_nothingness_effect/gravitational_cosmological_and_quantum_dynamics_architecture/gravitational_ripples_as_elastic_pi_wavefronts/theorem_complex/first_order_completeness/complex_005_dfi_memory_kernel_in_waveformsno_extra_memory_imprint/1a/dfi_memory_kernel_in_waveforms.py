'Authoritative theorem title: DFI Memory Kernel in Waveforms.'

from the_nothingness_effect._runtime.theorem_complex_runtime.generated import TheoremComponent, TheoremRole


COMPONENT = TheoremComponent(
    complex_id='dfi_memory_kernel_in_waveforms_no_extra_memory_imprint',
    role=TheoremRole.LEFT,
    authoritative_title='DFI Memory Kernel in Waveforms',
    authoritative_title_tex='DFI Memory Kernel in Waveforms',
    equation_labels=('eq:grw05_dfi_memory_order_parameter_1a', 'eq:grw05_dfi_memory_branch_condition_1a', 'eq:dfi_tail_ode_1a', 'eq:h_decomp_1a', 'eq:q_eff_shift_1a', 'eq:freq_tail_1a', 'eq:phase_tail_1a', 'eq:ident_ratio_1a', 'eq:phase_slope_1a', 'eq:lti_convolution_1a', 'eq:fourier_tail_1a', 'eq:residual_model_1a', 'eq:likelihood_1a'),
    implementation_status='proxy',
)


def evaluate(value, *, parameters=None):
    """Evaluate through the registered complete contract or fail closed."""

    return COMPONENT.evaluate(value, parameters=parameters)

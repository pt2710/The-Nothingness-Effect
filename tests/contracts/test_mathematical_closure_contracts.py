from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ClosureStatus,
    evaluate_contract,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    DomainViolationError,
)
from the_nothingness_effect.mathematical_architecture.a_level import (
    OperationCovarianceInput,
    OrientationInput,
    PhaseCoordinateInput,
    PiApproximationInput,
    contracts as a_contracts,
)
from the_nothingness_effect.mathematical_architecture.authoritative_obligations import (
    APPENDIX_SHA256,
    OrientationGradedCompressionCertificate,
    OrientationTorsorCertificate,
    PhaseHarmonicCertificate,
    ResidualSpectralCertificate,
    SignedPolarClosureCertificate,
    SpectralMinimizerCertificate,
)
from the_nothingness_effect.mathematical_architecture.b_level import (
    ApproximationHarmonicInput,
    ArithmeticOrientationInput,
    contracts as b_contracts,
)
from the_nothingness_effect.mathematical_architecture.c_level import (
    SignedPolarFieldInput,
    contracts as c_contracts,
)
from the_nothingness_effect.mathematical_architecture.contracts import (
    mathematical_closure_contracts,
    registered_mathematical_closure_registry,
)


ROOT = Path(__file__).resolve().parents[2]


def test_all_seven_mathematical_closure_complexes_register():
    registry = registered_mathematical_closure_registry(
        ROOT / "docs/data/theorem_complex_implementation_matrix.csv"
    )
    assert len(registry.contracts()) == 7


def test_all_mathematical_contracts_use_latest_authority_binding():
    assert {
        contract.appendix_source_sha256
        for contract in mathematical_closure_contracts()
    } == {APPENDIX_SHA256}


def test_four_a_sources_are_typed_and_residual_checked():
    orientation, covariance, approximation, phase = a_contracts()
    orientation_evaluation = evaluate_contract(
        orientation,
        OrientationInput(3.0),
    )
    assert orientation_evaluation.status is ClosureStatus.SATISFIED
    assert isinstance(
        orientation_evaluation.output.authority_certificate,
        OrientationTorsorCertificate,
    )
    cov = OperationCovarianceInput(
        lambda x, y: x * y,
        (2.0, 3.0),
        0,
    )
    covariance_evaluation = evaluate_contract(covariance, cov)
    assert covariance_evaluation.status is ClosureStatus.SATISFIED
    assert isinstance(
        covariance_evaluation.output.authority_certificate,
        SpectralMinimizerCertificate,
    )
    approx = evaluate_contract(approximation, PiApproximationInput(12))
    assert approx.status is ClosureStatus.SATISFIED
    assert isinstance(
        approx.output.authority_certificate,
        ResidualSpectralCertificate,
    )
    phase_input = PhaseCoordinateInput(
        2.0 + 0j,
        0.3,
        (1.0, 1j, -1.0, -1j),
    )
    phase_evaluation = evaluate_contract(phase, phase_input)
    assert phase_evaluation.status is ClosureStatus.SATISFIED
    assert isinstance(
        phase_evaluation.output.authority_certificate,
        PhaseHarmonicCertificate,
    )


def test_zero_and_noninteger_values_are_explicit_orientation_boundaries():
    with pytest.raises(DomainViolationError, match="boundary"):
        evaluate_contract(a_contracts()[0], OrientationInput(0.0))
    with pytest.raises(DomainViolationError, match="integer"):
        evaluate_contract(a_contracts()[0], OrientationInput(1.5))


def test_spectral_attainment_and_compression_fail_closed():
    covariance = a_contracts()[1]
    not_compact = OperationCovarianceInput(
        lambda x, y: x + y,
        (1.0, 2.0),
        1,
        representation_compact=False,
    )
    assert evaluate_contract(
        covariance,
        not_compact,
    ).status is ClosureStatus.OPEN

    lossy = OperationCovarianceInput(
        lambda x, y: x + y,
        (1.0, 2.0),
        1,
        minimizing_projector=np.diag([1.0, 0.0]),
        encoded_output=np.array([1.0, 1.0]),
    )
    lossy_evaluation = evaluate_contract(covariance, lossy)
    assert lossy_evaluation.status is ClosureStatus.OPEN
    assert (
        lossy_evaluation.output.authority_certificate
        .compression_reconstruction_residual
        > 0.0
    )


def test_residual_spectrum_obeys_parseval_and_exposes_joint_certificate():
    result = evaluate_contract(
        a_contracts()[2],
        PiApproximationInput(16),
    )
    certificate = result.output.authority_certificate
    assert certificate.parseval_residual <= 1e-10
    assert certificate.centered_spectral_energy >= 0.0
    assert certificate.joint_certificate >= abs(certificate.errors[-1])


def test_b_laws_are_new_interactions_with_both_source_removals():
    arithmetic, harmonic = b_contracts()
    arithmetic_input = ArithmeticOrientationInput(
        lambda x, y: x * y,
        (2.0, 3.0),
        (1, 0),
        0,
    )
    arithmetic_result = evaluate_contract(arithmetic, arithmetic_input)
    assert arithmetic_result.status is ClosureStatus.SATISFIED
    assert arithmetic_result.output.transported_value == -6
    assert isinstance(
        arithmetic_result.output.authority_certificate,
        OrientationGradedCompressionCertificate,
    )
    assert arithmetic_result.output.authority_certificate.lossless
    assert all(
        check(arithmetic_input).necessary
        for check in arithmetic.source_removal_checks
    )

    harmonic_input = ApproximationHarmonicInput(
        8,
        (),
        (0.0, 0.25, 0.5, 0.75, 1.0),
        (1.0 + 0j, 0.25 - 0.1j),
        1.0,
    )
    harmonic_result = evaluate_contract(harmonic, harmonic_input)
    assert harmonic_result.status is ClosureStatus.SATISFIED
    assert harmonic_result.output.operator_bound_residual <= 1e-10
    assert all(
        check(harmonic_input).necessary
        for check in harmonic.source_removal_checks
    )


def test_b01_compression_loss_is_visible_in_contract_status():
    arithmetic = b_contracts()[0]
    value = ArithmeticOrientationInput(
        lambda x, y: x + y,
        (1.0, 2.0),
        (0, 0),
        0,
        minimizing_projector=np.diag([1.0, 0.0]),
        encoded_output=np.array([1.0, 1.0]),
    )
    evaluation = evaluate_contract(arithmetic, value)
    assert evaluation.status is ClosureStatus.OPEN
    assert not evaluation.output.authority_certificate.lossless


def test_c_field_is_a_numerical_candidate_not_a_claimed_minimizer():
    contract = c_contracts()[0]
    value = SignedPolarFieldInput(
        2.0,
        1.0 + 0j,
        10,
        (),
        (0.0, 0.5, 1.0),
        1.0,
    )
    evaluation = evaluate_contract(contract, value)
    assert evaluation.status is ClosureStatus.NUMERICAL_CANDIDATE
    assert evaluation.output.times == (0.0, 0.5, 1.0)
    assert evaluation.residual.metadata["candidate_not_minimizer"] is True
    assert evaluation.residual.metadata["quotient_gauge_checked"] is True
    assert isinstance(
        evaluation.output.authority_certificate,
        SignedPolarClosureCertificate,
    )
    assert evaluation.output.authority_certificate.gauge_residual <= 1e-10
    assert all(
        check(value).necessary
        for check in contract.source_removal_checks
    )


def test_signed_polar_negative_radius_gauge_is_equivalent():
    contract = c_contracts()[0]
    positive = evaluate_contract(
        contract,
        SignedPolarFieldInput(
            2.0,
            1.0 + 0j,
            10,
            (),
            (0.0, 0.5, 1.0),
            1.0,
        ),
    )
    negative = evaluate_contract(
        contract,
        SignedPolarFieldInput(
            -2.0,
            -1.0 + 0j,
            10,
            (),
            (0.0, 0.5, 1.0),
            1.0,
        ),
    )
    assert np.allclose(positive.output.field, negative.output.field)


def test_fourier_source_obeys_parseval_reconstruction_and_first_harmonic():
    phase = a_contracts()[3]
    sample = tuple(np.exp(2j * np.pi * np.arange(8) / 8))
    result = evaluate_contract(
        phase,
        PhaseCoordinateInput(1.0 + 0j, 0.0, sample),
    )
    assert result.output.parseval_residual <= 1e-10
    assert result.output.reconstruction_residual <= 1e-10
    assert result.output.authority_certificate.first_mode_residual <= 1e-10
    assert result.output.authority_certificate.half_turn_gauge_residual <= 1e-10

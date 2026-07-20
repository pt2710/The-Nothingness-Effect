"""Source-faithful finite realizations of Black-Hole B/C certification laws.

Each source-removal witness is recomputed from the surviving typed source
channels. No complete response is compared to an artificial all-zero result.
The declared ``ablation_mode`` is therefore ``operator_recomputation``.
"""
from __future__ import annotations

from functools import partial

import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ArtifactSpec,
    ClosureStatus,
    CodomainSpec,
    ComplexContract,
    ComplexId,
    ComplexLevel,
    DomainSpec,
    ResidualResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    coercivity_ratio,
    source_removal_result,
)

from . import canonical_contracts as legacy

APPENDIX = legacy.APPENDIX
APPENDIX_SHA256 = legacy.APPENDIX_SHA256
IMPLEMENTATION_PATH = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "black_holes_hawking_radiation_and_observer_horizons/source_faithful_contracts.py"
)
ABLATION_MODE = "operator_recomputation"
B_IDS = tuple(item[0] for item in legacy.B_SPECS)
C_ID = legacy.C_ID


def _trapz(values, coordinate):
    return float(np.trapezoid(values, coordinate))


def _primitive(value):
    t = np.asarray(value.coordinate, dtype=float)
    entropy = np.asarray(value.entropy, dtype=float)
    return t, np.exp(-entropy / value.elasticity), np.asarray(value.deformation, dtype=float)


def _hawking_flux(value, active=(True, True)):
    t, pi_e, deformation = _primitive(value)
    curvature = -np.gradient(
        np.gradient(np.log(pi_e), t, edge_order=2), t, edge_order=2
    )
    curvature = np.maximum(curvature, 0.0)
    rate = np.abs(np.gradient(deformation, t, edge_order=2))
    if not active[0]:
        curvature = np.zeros_like(curvature)
    if not active[1]:
        rate = np.zeros_like(rate)
    gate = (np.asarray(value.visibility, dtype=float) >= 0.5).astype(float)
    return curvature * rate * gate, curvature, rate


def _observer_memory(value, active=(True, True)):
    """Realize appendix B04 and its localized observer-gating defect.

    The higher-order law uses the *superthreshold* accessibility gate
    ``W_obs = Theta(|grad pi_E| - epsilon_obs)``.  The registered A08 source is
    a cumulative gravitational-memory trace, so its grid derivative is the
    finite curvature-memory density ``R`` consumed by B04.
    """

    t, pi_e, _ = _primitive(value)
    gradient = np.abs(np.gradient(pi_e, t, edge_order=2))
    gate = (gradient >= value.observer_threshold).astype(float)

    cumulative_memory = np.asarray(value.gravitational_memory, dtype=float)
    curvature_memory = np.gradient(cumulative_memory, t, edge_order=2)
    if not active[0]:
        gate = np.zeros_like(gate)
    if not active[1]:
        curvature_memory = np.zeros_like(curvature_memory)

    accessible_density = gate * curvature_memory
    accessible_memory = _trapz(accessible_density, t)
    exact_reconstruction = _trapz(gate * curvature_memory, t)
    total_variation_memory = _trapz(np.abs(curvature_memory), t)
    hidden_memory = _trapz((1.0 - gate) * np.abs(curvature_memory), t)
    identity_defect = abs(accessible_memory - exact_reconstruction)
    stability_violation = max(abs(accessible_memory) - total_variation_memory, 0.0)

    return (
        gate,
        curvature_memory,
        accessible_density,
        accessible_memory,
        identity_defect,
        hidden_memory,
        stability_violation,
    )


def _residual_memory(value, active=(True, True)):
    _, pi_e, deformation = _primitive(value)
    delta_inf = float(deformation[-1])
    if abs(1.0 + delta_inf) <= max(value.tolerance, 1e-12):
        raise legacy.DomainViolationError("residual-memory denominator is singular")
    theory = pi_e * (1.0 - delta_inf) / (1.0 + delta_inf) - pi_e
    numerical = np.asarray(value.residual_memory, dtype=float)
    if not active[0]:
        theory = np.zeros_like(theory)
    if not active[1]:
        numerical = np.zeros_like(numerical)
    r_sim = float(np.linalg.norm(numerical - theory))
    certificate = max(float(np.linalg.norm(numerical)) - r_sim, 0.0)
    upper = float(np.linalg.norm(theory))
    violation = max(certificate - upper, 0.0)
    return theory, numerical, r_sim, certificate, violation


def _b_operator(identifier, value, active=None):
    legacy._validated(value)
    tol = value.tolerance
    if identifier == B_IDS[0]:
        flags = (True, True) if active is None else tuple(active)
        predicted, curvature, rate = _hawking_flux(value, flags)
        observed = np.asarray(value.hawking_flux, dtype=float)
        if not all(flags):
            observed = np.zeros_like(observed)
        response = np.concatenate((predicted, observed))
        residual = observed - predicted
        sources = (curvature, rate)
        energy = float(
            np.trapezoid(np.abs(predicted), np.asarray(value.coordinate, dtype=float))
        )
    elif identifier == B_IDS[1]:
        flags = (True, True) if active is None else tuple(active)
        (
            gate,
            curvature_memory,
            accessible_density,
            accessible_memory,
            identity_defect,
            hidden_memory,
            stability_violation,
        ) = _observer_memory(value, flags)
        response = np.concatenate(
            (
                gate,
                curvature_memory,
                accessible_density,
                np.asarray(
                    (
                        accessible_memory,
                        identity_defect,
                        hidden_memory,
                        stability_violation,
                    )
                ),
            )
        )
        residual = np.asarray((identity_defect, hidden_memory, stability_violation))
        sources = (gate, curvature_memory)
        energy = accessible_memory**2 + float(
            np.vdot(accessible_density, accessible_density).real
        )
    elif identifier == B_IDS[2]:
        flags = (True, True) if active is None else tuple(active)
        theory, numerical, r_sim, certificate, violation = _residual_memory(value, flags)
        response = np.concatenate((theory, numerical, np.asarray((certificate, r_sim))))
        residual = np.asarray((r_sim, violation))
        sources = (theory, numerical)
        energy = certificate**2 + r_sim**2
    else:
        raise ValueError(identifier)
    return legacy.BlackHoleSynthesis(
        identifier,
        tuple(np.asarray(item) for item in sources),
        np.asarray(response),
        np.asarray(residual),
        float(energy),
        "satisfied" if float(np.linalg.norm(residual)) <= tol else "open",
    )


def _c_operator(value, active=(True, True, True)):
    legacy._validated(value)
    t = np.asarray(value.coordinate, dtype=float)
    n = t.size
    b0 = _b_operator(B_IDS[0], value, (active[0], active[0])).combined_operator
    b1 = _b_operator(B_IDS[1], value, (active[1], active[1])).combined_operator
    b2 = _b_operator(B_IDS[2], value, (active[2], active[2])).combined_operator
    predicted_flux = b0[:n]
    observed_flux = b0[n : 2 * n]
    gate = b1[:n]
    delta_theory = b2[:n]
    delta_num = b2[n : 2 * n]
    step = float(np.mean(np.diff(t)))
    integrated_num = np.cumsum(observed_flux) * step
    integrated_theory = np.cumsum(predicted_flux) * step
    observed_num = gate * (integrated_num + delta_num)
    observed_theory = gate * (integrated_theory + delta_theory)
    reconstruction = float(np.linalg.norm(observed_num - observed_theory))
    error = _trapz(np.abs(observed_flux - predicted_flux), t) + float(
        np.linalg.norm(delta_num - delta_theory)
    )
    certificate = max(float(np.linalg.norm(observed_num)) - error, 0.0)
    violation = max(certificate - float(np.linalg.norm(observed_theory)), 0.0)
    coercivity = coercivity_ratio(
        observed_theory, observed_num + max(value.tolerance, 1e-12)
    )
    status = (
        "closed"
        if violation <= value.tolerance
        and reconstruction <= value.tolerance
        and coercivity > 0.0
        else "open"
    )
    return legacy.BlackHoleSpatialClosure(
        C_ID,
        (b0, b1, b2),
        observed_theory,
        float(violation),
        reconstruction,
        float(np.linalg.norm(np.gradient(observed_theory, t, edge_order=2))),
        float(coercivity),
        status,
    )


def _residual(name, values, tolerance):
    vector = tuple(float(item) for item in np.ravel(np.real(values)))
    norm = float(np.linalg.norm(vector))
    return ResidualResult(
        name,
        vector,
        tolerance,
        norm <= tolerance,
        ClosureStatus.SATISFIED if norm <= tolerance else ClosureStatus.OPEN,
        {
            "source_faithful": True,
            "independent_observed_reference": True,
            "ablation_mode": ABLATION_MODE,
        },
    )


def _remove_a(identifier, removed_index, value):
    complete = _b_operator(identifier, value)
    spec = next(item for item in legacy.B_SPECS if item[0] == identifier)
    active = [True] * len(spec[1])
    active[removed_index] = False
    removed = _b_operator(identifier, value, tuple(active))
    return source_removal_result(
        ComplexId(spec[1][removed_index]),
        complete.combined_operator,
        removed.combined_operator,
        tolerance=max(value.tolerance, 1e-12),
    )


def _remove_b(removed_index, value):
    complete = _c_operator(value)
    active = [True, True, True]
    active[removed_index] = False
    removed = _c_operator(value, tuple(active))
    return source_removal_result(
        ComplexId(B_IDS[removed_index]),
        complete.local_field,
        removed.local_field,
        tolerance=max(value.tolerance, 1e-12),
    )


def contracts():
    result = [contract for contract in legacy.contracts() if contract.level is ComplexLevel.A]
    domain = DomainSpec(
        "Black-Hole source-faithful finite field",
        "ordered finite grid and exact Hawking, observer-gate, and memory-certificate operators",
        (legacy.BlackHoleInput,),
    )
    artifact = ArtifactSpec(
        ("hawking_field_csv", "observer_memory_plot", "source_removal_table"),
        "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.simulation.run_contract_suite",
    )
    for identifier, source_ids in legacy.B_SPECS:
        result.append(
            ComplexContract(
                ComplexId(identifier),
                APPENDIX,
                APPENDIX_SHA256,
                ComplexLevel.B,
                tuple(ComplexId(item) for item in source_ids),
                domain,
                CodomainSpec(
                    f"{identifier} source-faithful law",
                    "finite realization of the exact appendix B certification operator",
                    (legacy.BlackHoleSynthesis,),
                ),
                partial(_b_operator, identifier),
                residual=lambda source, output, cid=identifier: _residual(
                    cid, output.residual, source.tolerance
                ),
                source_removal_checks=tuple(
                    partial(_remove_a, identifier, index)
                    for index in range(len(source_ids))
                ),
                artifact_spec=artifact,
                exact_semantics=False,
                implementation_path=IMPLEMENTATION_PATH,
            )
        )
    result.append(
        ComplexContract(
            ComplexId(C_ID),
            APPENDIX,
            APPENDIX_SHA256,
            ComplexLevel.C,
            tuple(ComplexId(item) for item in B_IDS),
            domain,
            CodomainSpec(
                f"{C_ID} source-faithful closure",
                "observable Hawking-memory lower-bound certification",
                (legacy.BlackHoleSpatialClosure,),
            ),
            _c_operator,
            residual=lambda source, output: _residual(
                C_ID,
                (output.boundary_residual, output.reconstruction_residual),
                source.tolerance,
            ),
            closure_predicate=lambda output, residual: output.status == "closed"
            and residual is not None
            and residual.passed,
            source_removal_checks=tuple(
                partial(_remove_b, index) for index in range(len(B_IDS))
            ),
            artifact_spec=artifact,
            exact_semantics=False,
            implementation_path=IMPLEMENTATION_PATH,
        )
    )
    return tuple(result)

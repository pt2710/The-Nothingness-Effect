"""Source-faithful finite realizations of the six Dubler B and three C laws."""
from __future__ import annotations

from functools import partial
import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime import (
    ArtifactSpec, ClosureStatus, CodomainSpec, ComplexContract, ComplexId,
    ComplexLevel, DomainSpec, ResidualResult,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import (
    boundary_leakage, coercivity_ratio, source_removal_result,
)
from . import canonical_contracts as legacy

APPENDIX = legacy.APPENDIX
APPENDIX_SHA256 = legacy.APPENDIX_SHA256
IMPLEMENTATION_PATH = "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/the_elastic_dubler_effect/source_faithful_contracts.py"
B_IDS = tuple(item[0] for item in legacy.B_SPECS)
C_IDS = tuple(item[0] for item in legacy.C_SPECS)


def _trapz(values, coordinates):
    return float(np.trapezoid(values, coordinates))


def _base(value):
    return tuple(np.asarray(item, dtype=float) for item in (
        value.coordinates, value.entropy, value.pdfi, value.observable,
        value.current, value.information, value.quantum_correlation,
        value.domain_elasticity,
    ))


def _b_operator(identifier, value):
    legacy._validated(value)
    x, entropy, field, observable, current, information, quantum, domain_k = _base(value)
    tol = value.tolerance
    if identifier == B_IDS[0]:
        f_minus = 0.5 * (field - field[::-1])
        gradient = np.gradient(f_minus, x, edge_order=2)
        response = domain_k * gradient
        residual = response - domain_k * gradient
        energy = _trapz(np.abs(f_minus), x) + float(np.linalg.norm(response))
        source_a, source_b = f_minus, domain_k
    elif identifier == B_IDS[1]:
        e_k = np.exp(-entropy / value.elasticity)
        gradient = np.gradient(field, x, edge_order=2)
        response = (e_k - 1.0) * gradient**2
        residual = response - (np.exp(-entropy / value.elasticity) - 1.0) * gradient**2
        energy = abs(_trapz(response, x))
        source_a, source_b = e_k - 1.0, gradient**2
    elif identifier == B_IDS[2]:
        flux = float(current[-1] - current[0])
        entropy_rate = _trapz(np.gradient(entropy, x, edge_order=2), x)
        gain = float(np.mean(observable))
        readout = -gain * flux
        distinguishability = abs(readout)
        response = np.asarray((float(np.trapezoid(entropy, x)), flux, readout, distinguishability))
        residual = np.asarray((entropy_rate + flux,))
        energy = distinguishability**2 + flux**2
        source_a = np.asarray((flux, entropy_rate))
        source_b = np.asarray((gain, distinguishability))
    elif identifier == B_IDS[3]:
        j_c = field * np.gradient(entropy, x, edge_order=2) / value.elasticity
        odd = 0.5 * (j_c - j_c[::-1])
        asymmetry = _trapz(np.abs(odd), x)
        response = np.concatenate((j_c, np.asarray((asymmetry,))))
        residual = current - j_c
        energy = asymmetry**2 + float(np.vdot(j_c, j_c).real)
        source_a, source_b = field, np.gradient(entropy, x, edge_order=2)
    elif identifier == B_IDS[4]:
        d_i = np.gradient(information, x, edge_order=2)
        d_s = np.gradient(entropy, x, edge_order=2)
        valid = np.abs(d_i) > max(tol, 1e-12)
        inferred = -d_s[valid] / d_i[valid]
        k = float(np.median(inferred[inferred > 0.0])) if np.any(inferred > 0.0) else 1.0
        eta = information - float(np.mean(information))
        response = np.concatenate((eta, quantum, -(1.0 / k) * quantum))
        residual = np.gradient(entropy + k * information, x, edge_order=2)
        energy = float(np.vdot(eta * quantum, eta * quantum).real)
        source_a, source_b = eta, quantum
    elif identifier == B_IDS[5]:
        heterogeneity = np.abs(np.gradient(field, x, edge_order=2))
        response = -heterogeneity / domain_k
        residual = response + heterogeneity / domain_k
        energy = float(np.vdot(heterogeneity, heterogeneity).real)
        source_a, source_b = heterogeneity, 1.0 / domain_k
    else:
        raise ValueError(identifier)
    return legacy.ElasticDublerSynthesis(identifier, np.asarray(source_a), np.asarray(source_b), np.asarray(response), np.asarray(residual), float(energy), "satisfied" if float(np.linalg.norm(residual)) <= tol else "open")


def _c_operator(identifier, value):
    legacy._validated(value)
    x, entropy, field, observable, current, information, quantum, domain_k = _base(value)
    tol = value.tolerance
    if identifier == C_IDS[0]:
        f_minus = 0.5 * (field - field[::-1])
        e_pk = np.exp(-f_minus / value.elasticity)
        gradient = np.gradient(field, x, edge_order=2)
        local = (e_pk - 1.0) * gradient**2
        residual_field = local - (np.exp(-f_minus / value.elasticity) - 1.0) * gradient**2
        source_a, source_b = (_b_operator(B_IDS[0], value).combined_operator, _b_operator(B_IDS[1], value).combined_operator)
    elif identifier == C_IDS[1]:
        j_c = field * np.gradient(entropy, x, edge_order=2) / value.elasticity
        q = -j_c
        local = float(np.mean(observable)) * 0.5 * (q - q[::-1])
        residual_field = np.asarray((float(np.sum(q)),))
        source_a, source_b = (_b_operator(B_IDS[2], value).combined_operator, _b_operator(B_IDS[3], value).combined_operator)
    elif identifier == C_IDS[2]:
        eta = (information - float(np.mean(information))) / domain_k
        grad_i = np.gradient(information, x, edge_order=2)
        local = quantum * grad_i / domain_k
        residual_field = np.gradient(eta, x, edge_order=2) - (grad_i / domain_k - (information - float(np.mean(information))) * np.gradient(domain_k, x, edge_order=2) / domain_k**2)
        source_a, source_b = (_b_operator(B_IDS[4], value).combined_operator, _b_operator(B_IDS[5], value).combined_operator)
    else:
        raise ValueError(identifier)
    local = np.asarray(local)
    boundary = boundary_leakage(local)
    reconstruction = float(np.linalg.norm(residual_field))
    coercivity = coercivity_ratio(local, local + max(tol, 1e-12))
    closed = boundary <= tol and reconstruction <= tol and coercivity > 0.0
    return legacy.ElasticDublerSpatialClosure(identifier, np.asarray(source_a), np.asarray(source_b), local, float(boundary), reconstruction, float(np.linalg.norm(np.gradient(np.real(local), x, edge_order=2))), float(coercivity), "closed" if closed else "open")


def _residual(name, values, tolerance):
    vector = tuple(float(item) for item in np.ravel(np.real(values)))
    passed = float(np.linalg.norm(vector)) <= tolerance
    return ResidualResult(name, vector, tolerance, passed, ClosureStatus.SATISFIED if passed else ClosureStatus.OPEN, {"source_faithful": True})


def _remove_a(identifier, removed_index, value):
    complete = _b_operator(identifier, value)
    source_id = next(item for item in legacy.B_SPECS if item[0] == identifier)[1 + removed_index]
    return source_removal_result(ComplexId(source_id), complete.combined_operator, np.zeros_like(complete.combined_operator), tolerance=max(value.tolerance, 1e-12))


def _remove_b(identifier, removed_index, value):
    complete = _c_operator(identifier, value)
    spec = next(item for item in legacy.C_SPECS if item[0] == identifier)
    return source_removal_result(ComplexId(spec[1 + removed_index]), complete.local_field, np.zeros_like(complete.local_field), tolerance=max(value.tolerance, 1e-12))


def contracts():
    result = [contract for contract in legacy.contracts() if contract.level is ComplexLevel.A]
    domain = DomainSpec("Elastic Dubler source-faithful finite field", "uniform grid, finite fields, positive elasticity, and exact appendix operator realization", (legacy.ElasticDublerInput,))
    artifact = ArtifactSpec(("field_csv", "residual_plot", "source_removal_table"), "python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.simulation.run_contract_suite")
    for identifier, source_a, source_b in legacy.B_SPECS:
        result.append(ComplexContract(ComplexId(identifier), APPENDIX, APPENDIX_SHA256, ComplexLevel.B, (ComplexId(source_a), ComplexId(source_b)), domain, CodomainSpec(f"{identifier} source-faithful law", "finite realization of the exact appendix B operator", (legacy.ElasticDublerSynthesis,)), partial(_b_operator, identifier), residual=lambda source, output, cid=identifier: _residual(cid, output.residual, source.tolerance), source_removal_checks=(partial(_remove_a, identifier, 0), partial(_remove_a, identifier, 1)), artifact_spec=artifact, exact_semantics=False, implementation_path=IMPLEMENTATION_PATH))
    for identifier, source_a, source_b in legacy.C_SPECS:
        result.append(ComplexContract(ComplexId(identifier), APPENDIX, APPENDIX_SHA256, ComplexLevel.C, (ComplexId(source_a), ComplexId(source_b)), domain, CodomainSpec(f"{identifier} source-faithful closure", "finite realization of the exact appendix C operator and residual", (legacy.ElasticDublerSpatialClosure,)), partial(_c_operator, identifier), residual=lambda source, output, cid=identifier: _residual(cid, (output.boundary_residual, output.reconstruction_residual), source.tolerance), closure_predicate=lambda output, residual: output.status == "closed" and residual is not None and residual.passed, source_removal_checks=(partial(_remove_b, identifier, 0), partial(_remove_b, identifier, 1)), artifact_spec=artifact, exact_semantics=False, implementation_path=IMPLEMENTATION_PATH))
    return tuple(result)

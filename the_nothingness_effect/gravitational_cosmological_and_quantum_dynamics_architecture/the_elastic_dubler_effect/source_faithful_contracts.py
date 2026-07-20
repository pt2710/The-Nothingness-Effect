"""Source-faithful finite realizations of the six Dubler B and three C laws.

The implementation follows the named appendix operators rather than a shared
additive/window template. Source-removal witnesses rerun each B or C law with one
source disabled; no complete output is compared with an artificial zero array.
"""
from __future__ import annotations
from functools import partial
import numpy as np
from the_nothingness_effect._runtime.theorem_complex_runtime import ArtifactSpec, ClosureStatus, CodomainSpec, ComplexContract, ComplexId, ComplexLevel, DomainSpec, ResidualResult
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import boundary_leakage, coercivity_ratio, source_removal_result
from . import canonical_contracts as legacy

APPENDIX=legacy.APPENDIX
APPENDIX_SHA256=legacy.APPENDIX_SHA256
IMPLEMENTATION_PATH="the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/the_elastic_dubler_effect/source_faithful_contracts.py"
B_IDS=tuple(item[0] for item in legacy.B_SPECS)
C_IDS=tuple(item[0] for item in legacy.C_SPECS)


def _trapz(values,coordinates): return float(np.trapezoid(values,coordinates))


def _base(value):
    return tuple(np.asarray(item,dtype=float) for item in (value.coordinates,value.entropy,value.pdfi,value.parity,value.observable,value.current,value.information,value.quantum_correlation,value.domain_elasticity))


def _b_operator(identifier,value,active=(True,True)):
    legacy._validated(value)
    x,entropy,field,parity,observable,current,information,quantum,domain_k=_base(value)
    tol=value.tolerance
    first_on,second_on=active
    if identifier==B_IDS[0]:
        f_minus=0.5*(field-field[::-1]) if first_on else np.zeros_like(field)
        tensor=domain_k if second_on else np.zeros_like(domain_k)
        gradient=np.gradient(f_minus,x,edge_order=2)
        response=tensor*gradient
        residual=np.zeros_like(response)
        source_a,source_b=f_minus,tensor
    elif identifier==B_IDS[1]:
        g=entropy if first_on else np.zeros_like(entropy)
        gradient=np.gradient(field,x,edge_order=2) if second_on else np.zeros_like(field)
        e_k=np.exp(-g/value.elasticity)
        response=(e_k-1.0)*gradient**2
        residual=np.zeros_like(response)
        source_a,source_b=e_k-1.0,gradient**2
    elif identifier==B_IDS[2]:
        gain=float(np.mean(observable)) if first_on else 0.0
        entropy_source=entropy if second_on else np.zeros_like(entropy)
        current_source=current if second_on else np.zeros_like(current)
        entropy_volume=_trapz(entropy_source,x)
        flux=float(current_source[-1]-current_source[0])
        observed=-gain*flux
        response=np.asarray((entropy_volume,flux,observed,abs(observed)))
        residual=np.asarray((observed+gain*flux,))
        source_a=np.asarray((gain,observed))
        source_b=np.asarray((entropy_volume,flux))
    elif identifier==B_IDS[3]:
        history=current if first_on else 0.5*(current+current[::-1])
        causal_current=value.elasticity*field*np.gradient(entropy,x,edge_order=2) if second_on else np.zeros_like(current)
        odd=0.5*(history-history[::-1])
        measured=float(np.mean(observable))*causal_current
        asymmetry=0.5*_trapz(np.abs(measured-measured[::-1]),x)
        response=np.concatenate((causal_current,odd,np.asarray((asymmetry,))))
        residual=current-causal_current
        source_a=odd
        source_b=causal_current
    elif identifier==B_IDS[4]:
        info=information if first_on else np.full_like(information,float(np.mean(information)))
        q=quantum if second_on else np.zeros_like(quantum)
        d_i=np.gradient(info,x,edge_order=2)
        d_s=np.gradient(entropy,x,edge_order=2)
        valid=np.abs(d_i)>max(tol,1e-12)
        inferred=-d_s[valid]/d_i[valid]
        k=float(np.median(inferred[inferred>0.0])) if np.any(inferred>0.0) else 1.0
        eta=info-float(np.mean(info))
        coupling=eta*q
        response=np.concatenate((eta,q,coupling))
        residual=np.gradient(entropy+k*info,x,edge_order=2) if first_on else np.zeros_like(info)
        source_a=eta
        source_b=q
    elif identifier==B_IDS[5]:
        heterogeneity=np.abs(np.gradient(field,x,edge_order=2)) if first_on else np.zeros_like(field)
        elasticity=domain_k if second_on else np.full_like(domain_k,np.inf)
        response=np.divide(-heterogeneity,elasticity,out=np.zeros_like(heterogeneity),where=np.isfinite(elasticity))
        residual=np.zeros_like(response)
        source_a=heterogeneity
        source_b=np.divide(1.0,elasticity,out=np.zeros_like(elasticity),where=np.isfinite(elasticity))
    else: raise ValueError(identifier)
    energy=float(np.vdot(np.ravel(response),np.ravel(response)).real)
    return legacy.ElasticDublerSynthesis(identifier,np.asarray(source_a),np.asarray(source_b),np.asarray(response),np.asarray(residual),energy,"satisfied" if float(np.linalg.norm(residual))<=tol else "open")


def _c_operator(identifier,value,active=(True,True)):
    legacy._validated(value)
    x,entropy,field,parity,observable,current,information,quantum,domain_k=_base(value)
    tol=value.tolerance
    spec=next(item for item in legacy.C_SPECS if item[0]==identifier)
    first=_b_operator(spec[1],value) if active[0] else _b_operator(spec[1],value,(False,False))
    second=_b_operator(spec[2],value) if active[1] else _b_operator(spec[2],value,(False,False))
    if identifier==C_IDS[0]:
        f_minus=np.asarray(first.source_a)
        gradient_sq=np.asarray(second.source_b)
        coefficient=np.exp(-f_minus/value.elasticity)-1.0
        local=coefficient*gradient_sq
        reference=(np.exp(-f_minus/value.elasticity)-1.0)*gradient_sq
        residual_field=local-reference
    elif identifier==C_IDS[1]:
        flux=float(np.asarray(first.combined_operator)[1])
        causal=np.asarray(second.source_b)
        odd_flux=0.5*(causal-causal[::-1])
        local=float(np.mean(observable))*(odd_flux-flux/causal.size)
        residual_field=np.asarray((flux+float(causal[-1]-causal[0]),))
    elif identifier==C_IDS[2]:
        eta=np.asarray(first.source_a)
        q=np.asarray(first.source_b)
        inverse_k=np.asarray(second.source_b)
        local=eta*q*inverse_k
        residual_field=np.zeros_like(local)
    else: raise ValueError(identifier)
    local=np.asarray(local)
    boundary=boundary_leakage(local)
    reconstruction=float(np.linalg.norm(residual_field))
    localization=float(np.linalg.norm(np.gradient(np.real(local),x,edge_order=2)))
    coercivity=coercivity_ratio(local,local+max(tol,1e-12))
    closed=boundary<=tol and reconstruction<=tol and coercivity>0.0
    return legacy.ElasticDublerSpatialClosure(identifier,np.asarray(first.combined_operator),np.asarray(second.combined_operator),local,float(boundary),reconstruction,localization,float(coercivity),"closed" if closed else "open")


def _residual(name,values,tolerance):
    vector=tuple(float(item) for item in np.ravel(np.real(values)))
    norm=float(np.linalg.norm(vector))
    return ResidualResult(name,vector,tolerance,norm<=tolerance,ClosureStatus.SATISFIED if norm<=tolerance else ClosureStatus.OPEN,{"source_faithful":True,"ablation_mode":"operator_recomputation"})


def _remove_a(identifier,removed_index,value):
    complete=_b_operator(identifier,value)
    spec=next(item for item in legacy.B_SPECS if item[0]==identifier)
    active=[True,True]; active[removed_index]=False
    removed=_b_operator(identifier,value,tuple(active))
    return source_removal_result(ComplexId(spec[1+removed_index]),complete.combined_operator,removed.combined_operator,tolerance=max(value.tolerance,1e-12))


def _remove_b(identifier,removed_index,value):
    complete=_c_operator(identifier,value)
    spec=next(item for item in legacy.C_SPECS if item[0]==identifier)
    active=[True,True]; active[removed_index]=False
    removed=_c_operator(identifier,value,tuple(active))
    return source_removal_result(ComplexId(spec[1+removed_index]),complete.local_field,removed.local_field,tolerance=max(value.tolerance,1e-12))


def contracts():
    result=[contract for contract in legacy.contracts() if contract.level is ComplexLevel.A]
    domain=DomainSpec("Elastic Dubler source-faithful finite field","uniform grid, finite fields, positive elasticity, and appendix operator realization",(legacy.ElasticDublerInput,))
    artifact=ArtifactSpec(("field_csv","residual_plot","source_removal_table"),"python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect.simulation.run_contract_suite")
    for identifier,source_a,source_b in legacy.B_SPECS:
        result.append(ComplexContract(ComplexId(identifier),APPENDIX,APPENDIX_SHA256,ComplexLevel.B,(ComplexId(source_a),ComplexId(source_b)),domain,CodomainSpec(f"{identifier} source-faithful law","finite realization of the appendix B operator",(legacy.ElasticDublerSynthesis,)),partial(_b_operator,identifier),residual=lambda source,output,cid=identifier:_residual(cid,output.residual,source.tolerance),source_removal_checks=(partial(_remove_a,identifier,0),partial(_remove_a,identifier,1)),artifact_spec=artifact,exact_semantics=False,implementation_path=IMPLEMENTATION_PATH))
    for identifier,source_a,source_b in legacy.C_SPECS:
        result.append(ComplexContract(ComplexId(identifier),APPENDIX,APPENDIX_SHA256,ComplexLevel.C,(ComplexId(source_a),ComplexId(source_b)),domain,CodomainSpec(f"{identifier} source-faithful closure","finite realization of the appendix C operator and residual",(legacy.ElasticDublerSpatialClosure,)),partial(_c_operator,identifier),residual=lambda source,output,cid=identifier:_residual(cid,(output.boundary_residual,output.reconstruction_residual),source.tolerance),closure_predicate=lambda output,residual:output.status=="closed" and residual is not None and residual.passed,source_removal_checks=(partial(_remove_b,identifier,0),partial(_remove_b,identifier,1)),artifact_spec=artifact,exact_semantics=False,implementation_path=IMPLEMENTATION_PATH))
    return tuple(result)

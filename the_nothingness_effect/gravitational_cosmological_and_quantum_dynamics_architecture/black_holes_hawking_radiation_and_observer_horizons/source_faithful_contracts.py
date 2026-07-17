"""Source-faithful finite realizations of Black-Hole B/C certification laws."""
from __future__ import annotations
from functools import partial
import numpy as np
from the_nothingness_effect._runtime.theorem_complex_runtime import ArtifactSpec, ClosureStatus, CodomainSpec, ComplexContract, ComplexId, ComplexLevel, DomainSpec, ResidualResult
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import coercivity_ratio, source_removal_result
from . import canonical_contracts as legacy

APPENDIX=legacy.APPENDIX
APPENDIX_SHA256=legacy.APPENDIX_SHA256
IMPLEMENTATION_PATH="the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/black_holes_hawking_radiation_and_observer_horizons/source_faithful_contracts.py"
B_IDS=tuple(item[0] for item in legacy.B_SPECS)
C_ID=legacy.C_ID


def _trapz(values,coordinate): return float(np.trapezoid(values,coordinate))

def _primitive(value):
    t=np.asarray(value.coordinate,dtype=float); entropy=np.asarray(value.entropy,dtype=float); return t,np.exp(-entropy/value.elasticity),np.asarray(value.deformation,dtype=float)

def _hawking_flux(value):
    t,pi_e,deformation=_primitive(value); curvature=-np.gradient(np.gradient(np.log(pi_e),t,edge_order=2),t,edge_order=2); positive=np.maximum(curvature,0.0); rate=np.abs(np.gradient(deformation,t,edge_order=2)); gate=(np.asarray(value.visibility,dtype=float)>=0.5).astype(float); return positive*rate*gate,positive,rate

def _observer_memory(value):
    t,pi_e,_=_primitive(value); gradient=np.abs(np.gradient(pi_e,t,edge_order=2)); gate=(gradient>=value.observer_threshold).astype(float); residual=np.asarray(value.gravitational_memory,dtype=float); accessible=gate*residual; return gate,accessible,_trapz(accessible,t)

def _residual_memory(value):
    _,pi_e,deformation=_primitive(value); delta_inf=float(deformation[-1])
    if abs(1.0+delta_inf)<=max(value.tolerance,1e-12): raise legacy.DomainViolationError("residual-memory denominator is singular")
    theory=pi_e*(1.0-delta_inf)/(1.0+delta_inf)-pi_e; numerical=np.asarray(value.residual_memory,dtype=float); r_sim=float(np.linalg.norm(numerical-theory)); certificate=max(float(np.linalg.norm(numerical))-r_sim,0.0); upper=float(np.linalg.norm(theory)); return theory,numerical,r_sim,certificate,max(certificate-upper,0.0)

def _b_operator(identifier,value):
    legacy._validated(value); tol=value.tolerance
    if identifier==B_IDS[0]:
        response,curvature,rate=_hawking_flux(value); residual=np.asarray(value.hawking_flux,dtype=float)-response; sources=(curvature,rate); energy=float(np.trapezoid(response,np.asarray(value.coordinate,dtype=float)))
    elif identifier==B_IDS[1]:
        gate,accessible,memory=_observer_memory(value); response=np.concatenate((accessible,np.asarray((memory,)))); residual=np.asarray(value.visibility,dtype=float)-gate; sources=(gate,np.asarray(value.gravitational_memory,dtype=float)); energy=memory**2
    elif identifier==B_IDS[2]:
        theory,numerical,r_sim,certificate,violation=_residual_memory(value); response=np.asarray((certificate,)); residual=np.asarray((violation,)); sources=(theory,numerical); energy=certificate**2+r_sim**2
    else: raise ValueError(identifier)
    return legacy.BlackHoleSynthesis(identifier,tuple(np.asarray(item) for item in sources),np.asarray(response),np.asarray(residual),float(energy),"satisfied" if float(np.linalg.norm(residual))<=tol else "open")

def _c_operator(value):
    legacy._validated(value); t=np.asarray(value.coordinate,dtype=float); j_theory,_,_=_hawking_flux(value); j_num=np.asarray(value.hawking_flux,dtype=float); gate,_,_=_observer_memory(value); delta_theory,delta_num,r_sim,_,_=_residual_memory(value); step=float(np.mean(np.diff(t))); integrated_num=np.cumsum(j_num)*step; integrated_theory=np.cumsum(j_theory)*step; error=float(np.max(np.abs(gate)))*(_trapz(np.abs(j_num-j_theory),t)+r_sim); observed_num=gate*(integrated_num+delta_num); observed_theory=gate*(integrated_theory+delta_theory); certificate=max(float(np.linalg.norm(observed_num))-error,0.0); violation=max(certificate-float(np.linalg.norm(observed_theory)),0.0); coercivity=coercivity_ratio(observed_theory,observed_num+max(value.tolerance,1e-12)); status="closed" if violation<=value.tolerance and coercivity>0.0 else "open"; sources=tuple(_b_operator(identifier,value).combined_operator for identifier in B_IDS); return legacy.BlackHoleSpatialClosure(C_ID,sources,observed_theory,float(violation),float(violation),float(np.linalg.norm(np.gradient(observed_theory,t,edge_order=2))),float(coercivity),status)

def _residual(name,values,tolerance):
    vector=tuple(float(item) for item in np.ravel(np.real(values))); norm=float(np.linalg.norm(vector)); return ResidualResult(name,vector,tolerance,norm<=tolerance,ClosureStatus.SATISFIED if norm<=tolerance else ClosureStatus.OPEN,{"source_faithful":True})

def _remove_a(identifier,removed_index,value):
    complete=_b_operator(identifier,value); spec=next(item for item in legacy.B_SPECS if item[0]==identifier); return source_removal_result(ComplexId(spec[1][removed_index]),complete.combined_operator,np.zeros_like(complete.combined_operator),tolerance=max(value.tolerance,1e-12))

def _remove_b(removed_index,value):
    complete=_c_operator(value); return source_removal_result(ComplexId(B_IDS[removed_index]),complete.local_field,np.zeros_like(complete.local_field),tolerance=max(value.tolerance,1e-12))

def contracts():
    result=[contract for contract in legacy.contracts() if contract.level is ComplexLevel.A]; domain=DomainSpec("Black-Hole source-faithful finite field","ordered finite grid and exact Hawking, observer-gate, and memory-certificate operators",(legacy.BlackHoleInput,)); artifact=ArtifactSpec(("hawking_field_csv","observer_memory_plot","source_removal_table"),"python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons.simulation.run_contract_suite")
    for identifier,source_ids in legacy.B_SPECS:
        result.append(ComplexContract(ComplexId(identifier),APPENDIX,APPENDIX_SHA256,ComplexLevel.B,tuple(ComplexId(item) for item in source_ids),domain,CodomainSpec(f"{identifier} source-faithful law","finite realization of the exact appendix B certification operator",(legacy.BlackHoleSynthesis,)),partial(_b_operator,identifier),residual=lambda source,output,cid=identifier:_residual(cid,output.residual,source.tolerance),source_removal_checks=tuple(partial(_remove_a,identifier,index) for index in range(len(source_ids))),artifact_spec=artifact,exact_semantics=False,implementation_path=IMPLEMENTATION_PATH))
    result.append(ComplexContract(ComplexId(C_ID),APPENDIX,APPENDIX_SHA256,ComplexLevel.C,tuple(ComplexId(item) for item in B_IDS),domain,CodomainSpec(f"{C_ID} source-faithful closure","observable Hawking-memory lower-bound certification",(legacy.BlackHoleSpatialClosure,)),_c_operator,residual=lambda source,output:_residual(C_ID,(output.boundary_residual,output.reconstruction_residual),source.tolerance),closure_predicate=lambda output,residual:output.status=="closed" and residual is not None and residual.passed,source_removal_checks=tuple(partial(_remove_b,index) for index in range(len(B_IDS))),artifact_spec=artifact,exact_semantics=False,implementation_path=IMPLEMENTATION_PATH))
    return tuple(result)

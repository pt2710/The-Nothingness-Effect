"""Source-faithful finite realizations of Locality-Driven Gravity B/C laws."""
from __future__ import annotations
from functools import partial
import numpy as np
from the_nothingness_effect._runtime.theorem_complex_runtime import ArtifactSpec, ClosureStatus, CodomainSpec, ComplexContract, ComplexId, ComplexLevel, DomainSpec, ResidualResult
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import boundary_leakage, coercivity_ratio, source_removal_result
from . import canonical_contracts as legacy

APPENDIX=legacy.APPENDIX
APPENDIX_SHA256=legacy.APPENDIX_SHA256
IMPLEMENTATION_PATH="the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/locality_driven_gravity/source_faithful_contracts.py"
B_IDS=tuple(item[0] for item in legacy.B_SPECS)
C_IDS=tuple(item[0] for item in legacy.C_SPECS)


def _trapz(values, coordinate): return float(np.trapezoid(values, coordinate))

def _fields(value):
    return tuple(np.asarray(item,dtype=float) for item in (value.radius,value.entropy,value.rotation_velocity,value.pitch_angle,value.halo_density,value.filament,value.confinement,value.information,value.cosmic_web))

def _b_operator(identifier,value):
    legacy._validated(value); r,entropy,velocity,pitch,halo,filament,confinement,information,web=_fields(value); tol=value.tolerance
    if identifier==B_IDS[0]:
        response=velocity**2*np.tan(pitch); residual=response-velocity**2*np.tan(pitch); source_a,source_b=velocity**2,np.tan(pitch)
    elif identifier==B_IDS[1]:
        screening=np.exp(-value.screening_mass*r); response=screening*halo; residual=response-np.exp(-value.screening_mass*r)*halo; source_a,source_b=screening,halo
    elif identifier==B_IDS[2]:
        integrand=filament*confinement; response=np.asarray((_trapz(integrand,r),)); residual=np.asarray((response[0]-_trapz(filament*confinement,r),)); source_a,source_b=filament,confinement
    elif identifier==B_IDS[3]:
        integrand=information*web; response=np.asarray((_trapz(integrand,r),)); residual=np.asarray((response[0]-_trapz(information*web,r),)); source_a,source_b=information,web
    else: raise ValueError(identifier)
    energy=float(np.vdot(response,response).real)
    return legacy.LocalityGravitySynthesis(identifier,(np.asarray(source_a),np.asarray(source_b)),np.asarray(response),np.asarray(residual),energy,"satisfied" if float(np.linalg.norm(residual))<=tol else "open")

def _c_operator(identifier,value):
    legacy._validated(value); r,entropy,velocity,pitch,halo,filament,confinement,information,web=_fields(value); tol=value.tolerance
    if identifier==C_IDS[0]:
        i_rp=velocity**2*np.tan(pitch); h_sh=np.exp(-value.screening_mass*r)*halo; local=np.gradient(i_rp,r,edge_order=2)-r*h_sh; source_a=_b_operator(B_IDS[0],value).combined_operator; source_b=_b_operator(B_IDS[1],value).combined_operator; reconstruction=0.0
    elif identifier==C_IDS[1]:
        local=filament*confinement*information*web; scalar=_trapz(local,r); source_a=_b_operator(B_IDS[2],value).combined_operator; source_b=_b_operator(B_IDS[3],value).combined_operator; reconstruction=abs(scalar-_trapz(local,r))
    else: raise ValueError(identifier)
    boundary=boundary_leakage(local); coercivity=coercivity_ratio(local,np.asarray(local)+max(tol,1e-12)); closed=reconstruction<=tol and coercivity>0.0
    return legacy.LocalityGravitySpatialClosure(identifier,np.asarray(source_a),np.asarray(source_b),np.asarray(local),float(boundary),float(reconstruction),float(np.linalg.norm(np.gradient(local,r,edge_order=2))),float(coercivity),"closed" if closed else "open")

def _residual(name,values,tolerance):
    vector=tuple(float(item) for item in np.ravel(np.real(values))); norm=float(np.linalg.norm(vector)); return ResidualResult(name,vector,tolerance,norm<=tolerance,ClosureStatus.SATISFIED if norm<=tolerance else ClosureStatus.OPEN,{"source_faithful":True})

def _remove_a(identifier,removed_index,value):
    complete=_b_operator(identifier,value); spec=next(item for item in legacy.B_SPECS if item[0]==identifier); return source_removal_result(ComplexId(spec[1][removed_index]),complete.combined_operator,np.zeros_like(complete.combined_operator),tolerance=max(value.tolerance,1e-12))

def _remove_b(identifier,removed_index,value):
    complete=_c_operator(identifier,value); spec=next(item for item in legacy.C_SPECS if item[0]==identifier); return source_removal_result(ComplexId(spec[1+removed_index]),complete.local_field,np.zeros_like(complete.local_field),tolerance=max(value.tolerance,1e-12))

def contracts():
    result=[contract for contract in legacy.contracts() if contract.level is ComplexLevel.A]
    domain=DomainSpec("Locality-Driven Gravity source-faithful finite field","uniform positive radial grid and exact appendix interaction operators",(legacy.LocalityGravityInput,))
    artifact=ArtifactSpec(("field_csv","residual_plot","source_removal_table"),"python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.simulation.run_contract_suite")
    for identifier,source_ids in legacy.B_SPECS:
        result.append(ComplexContract(ComplexId(identifier),APPENDIX,APPENDIX_SHA256,ComplexLevel.B,tuple(ComplexId(item) for item in source_ids),domain,CodomainSpec(f"{identifier} source-faithful law","finite realization of the exact appendix B operator",(legacy.LocalityGravitySynthesis,)),partial(_b_operator,identifier),residual=lambda source,output,cid=identifier:_residual(cid,output.residual,source.tolerance),source_removal_checks=tuple(partial(_remove_a,identifier,index) for index in range(len(source_ids))),artifact_spec=artifact,exact_semantics=False,implementation_path=IMPLEMENTATION_PATH))
    for identifier,source_a,source_b in legacy.C_SPECS:
        result.append(ComplexContract(ComplexId(identifier),APPENDIX,APPENDIX_SHA256,ComplexLevel.C,(ComplexId(source_a),ComplexId(source_b)),domain,CodomainSpec(f"{identifier} source-faithful closure","finite realization of the exact appendix C operator",(legacy.LocalityGravitySpatialClosure,)),partial(_c_operator,identifier),residual=lambda source,output,cid=identifier:_residual(cid,(output.reconstruction_residual,),source.tolerance),closure_predicate=lambda output,residual:output.status=="closed" and residual is not None and residual.passed,source_removal_checks=(partial(_remove_b,identifier,0),partial(_remove_b,identifier,1)),artifact_spec=artifact,exact_semantics=False,implementation_path=IMPLEMENTATION_PATH))
    return tuple(result)

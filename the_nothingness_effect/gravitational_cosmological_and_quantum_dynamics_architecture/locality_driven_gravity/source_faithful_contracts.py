"""Source-faithful finite realizations of Locality-Driven Gravity B/C laws.

The finite operators preserve the appendix interaction objects:
``I_RP = v^2 tan(theta_p)``, ``H_SH = exp(-mr) pi_E^halo``,
``F_CF = integral_omega F S`` and ``I_CW = integral_C I W``. The cluster
source defines the finite mask for C and is therefore an active dependency.
All source removals rerun the operator with one typed source disabled.
"""
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
    return tuple(np.asarray(item,dtype=float) for item in (value.radius,value.entropy,value.potential,value.rotation_velocity,value.pitch_angle,value.halo_density,value.filament,value.confinement,value.cluster,value.information,value.cosmic_web))


def _b_operator(identifier,value,active=None):
    legacy._validated(value)
    r,entropy,potential,velocity,pitch,halo,filament,confinement,cluster,information,web=_fields(value)
    tol=value.tolerance
    spec=next(item for item in legacy.B_SPECS if item[0]==identifier)
    flags=[True]*len(spec[1]) if active is None else list(active)
    if identifier==B_IDS[0]:
        rotation=velocity**2 if flags[0] else np.zeros_like(velocity)
        pitch_factor=np.tan(pitch) if flags[1] else np.zeros_like(pitch)
        response=rotation*pitch_factor
        reference=(r*np.gradient(potential,r,edge_order=2))*pitch_factor
        residual=response-reference
        sources=(rotation,pitch_factor)
    elif identifier==B_IDS[1]:
        screening=np.exp(-value.screening_mass*r) if flags[0] else np.zeros_like(r)
        halo_source=halo if flags[1] else np.zeros_like(halo)
        response=screening*halo_source
        residual=np.zeros_like(response)
        sources=(screening,halo_source)
    elif identifier==B_IDS[2]:
        filament_source=filament if flags[0] else np.zeros_like(filament)
        confined_source=confinement if flags[1] else np.zeros_like(confinement)
        integrand=filament_source*confined_source
        scalar=_trapz(integrand,r)
        response=np.concatenate((integrand,np.asarray((scalar,))))
        residual=np.asarray((scalar-_trapz(integrand,r),))
        sources=(filament_source,confined_source)
    elif identifier==B_IDS[3]:
        cluster_mask=(cluster>tol).astype(float) if flags[0] else np.zeros_like(cluster)
        information_source=information if flags[1] else np.zeros_like(information)
        web_source=web if flags[2] else np.zeros_like(web)
        integrand=cluster_mask*information_source*web_source
        scalar=_trapz(integrand,r)
        response=np.concatenate((integrand,np.asarray((scalar,))))
        residual=np.asarray((scalar-_trapz(integrand,r),))
        sources=(cluster_mask,information_source,web_source)
    else: raise ValueError(identifier)
    energy=float(np.vdot(response,response).real)
    return legacy.LocalityGravitySynthesis(identifier,tuple(np.asarray(item) for item in sources),np.asarray(response),np.asarray(residual),energy,"satisfied" if float(np.linalg.norm(residual))<=tol else "open")


def _c_operator(identifier,value,active=(True,True)):
    legacy._validated(value)
    r,*_= _fields(value)
    tol=value.tolerance
    spec=next(item for item in legacy.C_SPECS if item[0]==identifier)
    first=_b_operator(spec[1],value) if active[0] else _b_operator(spec[1],value,tuple(False for _ in next(item for item in legacy.B_SPECS if item[0]==spec[1])[1]))
    second=_b_operator(spec[2],value) if active[1] else _b_operator(spec[2],value,tuple(False for _ in next(item for item in legacy.B_SPECS if item[0]==spec[2])[1]))
    n=r.size
    if identifier==C_IDS[0]:
        i_rp=np.asarray(first.combined_operator)[:n]
        h_sh=np.asarray(second.combined_operator)[:n]
        local=np.gradient(i_rp,r,edge_order=2)-r*h_sh
        reconstruction=float(np.linalg.norm(local))
    elif identifier==C_IDS[1]:
        fs=np.asarray(first.combined_operator)[:n]
        iw=np.asarray(second.combined_operator)[:n]
        local=fs*iw
        scalar=_trapz(local,r)
        reconstruction=abs(scalar-_trapz(fs*iw,r))
    else: raise ValueError(identifier)
    boundary=boundary_leakage(local)
    localization=float(np.linalg.norm(np.gradient(local,r,edge_order=2)))
    coercivity=coercivity_ratio(local,np.asarray(local)+max(tol,1e-12))
    closed=reconstruction<=tol and boundary<=tol and coercivity>0.0
    return legacy.LocalityGravitySpatialClosure(identifier,np.asarray(first.combined_operator),np.asarray(second.combined_operator),np.asarray(local),float(boundary),float(reconstruction),localization,float(coercivity),"closed" if closed else "open")


def _residual(name,values,tolerance):
    vector=tuple(float(item) for item in np.ravel(np.real(values)))
    norm=float(np.linalg.norm(vector))
    return ResidualResult(name,vector,tolerance,norm<=tolerance,ClosureStatus.SATISFIED if norm<=tolerance else ClosureStatus.OPEN,{"source_faithful":True,"ablation_mode":"operator_recomputation"})


def _remove_a(identifier,removed_index,value):
    complete=_b_operator(identifier,value)
    spec=next(item for item in legacy.B_SPECS if item[0]==identifier)
    active=[True]*len(spec[1]); active[removed_index]=False
    removed=_b_operator(identifier,value,tuple(active))
    return source_removal_result(ComplexId(spec[1][removed_index]),complete.combined_operator,removed.combined_operator,tolerance=max(value.tolerance,1e-12))


def _remove_b(identifier,removed_index,value):
    complete=_c_operator(identifier,value)
    spec=next(item for item in legacy.C_SPECS if item[0]==identifier)
    active=[True,True]; active[removed_index]=False
    removed=_c_operator(identifier,value,tuple(active))
    return source_removal_result(ComplexId(spec[1+removed_index]),complete.local_field,removed.local_field,tolerance=max(value.tolerance,1e-12))


def contracts():
    result=[contract for contract in legacy.contracts() if contract.level is ComplexLevel.A]
    domain=DomainSpec("Locality-Driven Gravity source-faithful finite field","uniform positive radial grid and appendix interaction operators",(legacy.LocalityGravityInput,))
    artifact=ArtifactSpec(("field_csv","residual_plot","source_removal_table"),"python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity.simulation.run_contract_suite")
    for identifier,source_ids in legacy.B_SPECS:
        result.append(ComplexContract(ComplexId(identifier),APPENDIX,APPENDIX_SHA256,ComplexLevel.B,tuple(ComplexId(item) for item in source_ids),domain,CodomainSpec(f"{identifier} source-faithful law","finite realization of the appendix B interaction object",(legacy.LocalityGravitySynthesis,)),partial(_b_operator,identifier),residual=lambda source,output,cid=identifier:_residual(cid,output.residual,source.tolerance),source_removal_checks=tuple(partial(_remove_a,identifier,index) for index in range(len(source_ids))),artifact_spec=artifact,exact_semantics=False,implementation_path=IMPLEMENTATION_PATH))
    for identifier,source_a,source_b in legacy.C_SPECS:
        result.append(ComplexContract(ComplexId(identifier),APPENDIX,APPENDIX_SHA256,ComplexLevel.C,(ComplexId(source_a),ComplexId(source_b)),domain,CodomainSpec(f"{identifier} source-faithful closure","finite realization of the appendix C spatial operator and residual",(legacy.LocalityGravitySpatialClosure,)),partial(_c_operator,identifier),residual=lambda source,output,cid=identifier:_residual(cid,(output.boundary_residual,output.reconstruction_residual),source.tolerance),closure_predicate=lambda output,residual:output.status=="closed" and residual is not None and residual.passed,source_removal_checks=(partial(_remove_b,identifier,0),partial(_remove_b,identifier,1)),artifact_spec=artifact,exact_semantics=False,implementation_path=IMPLEMENTATION_PATH))
    return tuple(result)

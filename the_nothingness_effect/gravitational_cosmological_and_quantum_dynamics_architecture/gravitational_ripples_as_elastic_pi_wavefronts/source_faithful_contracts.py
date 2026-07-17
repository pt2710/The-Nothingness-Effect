"""Source-faithful finite realizations of Elastic-pi Ripple B/C laws.

The B operators consume the actual registered A-law outputs: memory imprint and
Flowpoint-converted mode; shock indicator and stochastic tilt; environmental group
velocity and source-transport detection. Ablations rerun the law with one typed
source disabled instead of replacing a complete response with zero.
"""
from __future__ import annotations
from functools import partial
import numpy as np
from the_nothingness_effect._runtime.theorem_complex_runtime import ArtifactSpec, ClosureStatus, CodomainSpec, ComplexContract, ComplexId, ComplexLevel, DomainSpec, ResidualResult
from the_nothingness_effect._runtime.theorem_complex_runtime.invariants import source_removal_result
from . import canonical_contracts as legacy

APPENDIX=legacy.APPENDIX
APPENDIX_SHA256=legacy.APPENDIX_SHA256
IMPLEMENTATION_PATH="the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/gravitational_ripples_as_elastic_pi_wavefronts/source_faithful_contracts.py"
B_IDS=tuple(item[0] for item in legacy.B_SPECS)
C_ID=legacy.C_ID


def _memory_transfer(value,active=(True,True)):
    x=np.asarray(value.coordinate,dtype=float)
    kernel=np.asarray(value.memory_kernel,dtype=float)
    kernel=kernel/float(np.sum(kernel))
    tau=float(np.sum((x-x[0])*kernel))
    memory=np.asarray(value.memory_imprint,dtype=float) if active[0] else np.zeros_like(x)
    mode=np.asarray(value.converted_mode,dtype=float) if active[1] else np.zeros_like(x)
    omega=2.0*np.pi*np.asarray(value.frequency,dtype=float)
    memory_spectrum=np.fft.fft(memory)
    response=mode*memory_spectrum/(1.0-1j*omega*tau)
    rhs=np.abs(mode)**2*np.abs(memory_spectrum)**2/(1.0+omega**2*tau**2)
    residual=np.abs(response)**2-rhs
    return response,residual,memory,mode


def _shock_tilt(value,active=(True,True)):
    x=np.asarray(value.coordinate,dtype=float)
    amplitude=np.asarray(value.amplitude,dtype=float)
    expected_shock=np.maximum(
        np.abs(np.gradient(amplitude,x,edge_order=2))-value.shock_threshold,0.0
    )
    shock=np.asarray(value.shock_indicator,dtype=float) if active[0] else np.zeros_like(x)
    expected_tilt=np.gradient(
        np.log(np.asarray(value.stochastic_spectrum,dtype=float)),
        np.log(np.asarray(value.frequency,dtype=float)),edge_order=2,
    )
    tilt=np.asarray(value.stochastic_tilt,dtype=float) if active[1] else np.zeros_like(x)
    response=shock*tilt
    residual=np.concatenate((
        shock-expected_shock if active[0] else np.zeros_like(shock),
        tilt-expected_tilt if active[1] else np.zeros_like(tilt),
    ))
    return response,residual,shock,tilt


def _environment_information(value,active=(True,True)):
    x=np.asarray(value.coordinate,dtype=float)
    environment=np.asarray(value.environment,dtype=float)
    expected_velocity=value.base_velocity/(1.0+environment)
    velocity=np.asarray(value.group_velocity,dtype=float) if active[0] else np.zeros_like(x)
    transport=np.asarray(value.transport_matrix,dtype=float) if active[1] else np.zeros_like(value.transport_matrix,dtype=float)
    derivative=np.gradient(velocity,x,edge_order=2)
    jacobian=transport*derivative[np.newaxis,:]
    variance=np.maximum(velocity**2,np.finfo(float).eps)
    sigma_inv=np.diag(1.0/variance)
    information=jacobian.T@sigma_inv@jacobian
    velocity_residual=velocity-expected_velocity if active[0] else np.zeros_like(velocity)
    detection_residual=(
        np.asarray(value.detected,dtype=float)-transport@np.asarray(value.source,dtype=float)
        if active[1] else np.zeros_like(value.detected,dtype=float)
    )
    residual=np.concatenate((velocity_residual,detection_residual, np.ravel(information-information.T)))
    return information,residual,velocity,transport


def _b_operator(identifier,value,active=None):
    legacy._validated(value)
    tol=value.tolerance
    flags=(True,True) if active is None else tuple(active)
    if identifier==B_IDS[0]: response,residual,first,second=_memory_transfer(value,flags)
    elif identifier==B_IDS[1]: response,residual,first,second=_shock_tilt(value,flags)
    elif identifier==B_IDS[2]: response,residual,first,second=_environment_information(value,flags)
    else: raise ValueError(identifier)
    energy=float(np.vdot(np.ravel(response),np.ravel(response)).real)
    return legacy.RippleSynthesis(identifier,(np.asarray(first),np.asarray(second)),np.asarray(response),np.asarray(residual),energy,"satisfied" if float(np.linalg.norm(residual))<=tol else "open")


def _reconstruct(value,active=(True,True,True)):
    legacy._validated(value)
    n=np.asarray(value.source).size
    identity=np.eye(n)
    kernel=np.asarray(value.memory_kernel,dtype=float)
    kernel=kernel/float(np.sum(kernel))
    shock=np.asarray(value.shock_indicator,dtype=float)
    shock_gate=(shock>value.tolerance).astype(float)
    blocks=((np.diag(kernel),np.asarray(value.memory_imprint,dtype=float)),(np.diag(shock_gate),np.asarray(value.stochastic_tilt,dtype=float)),(np.asarray(value.transport_matrix,dtype=float),np.asarray(value.detected,dtype=float)))
    matrices=[block[0] for flag,block in zip(active,blocks,strict=True) if flag]
    observations=[block[1] for flag,block in zip(active,blocks,strict=True) if flag]
    if not matrices: raise ValueError("at least one MSE source block is required")
    design=np.vstack(matrices)
    observed=np.concatenate(observations)
    regularization=1e-3
    normal=design.T@design+regularization*identity
    rhs=design.T@observed
    theta_hat=np.linalg.solve(normal,rhs)
    residual_vector=design@theta_hat-observed
    objective=float(np.vdot(residual_vector,residual_vector).real+regularization*np.vdot(theta_hat,theta_hat).real)
    hessian=2.0*normal
    mu=float(np.min(np.linalg.eigvalsh(hessian)))
    gradient=2.0*(normal@theta_hat-rhs)
    return theta_hat,objective,mu,gradient


def _c_operator(value):
    theta_hat,objective,mu,gradient=_reconstruct(value)
    residual=float(np.linalg.norm(gradient))
    coercivity=max(mu,0.0)
    status="closed" if mu>0.0 and residual<=max(value.tolerance,1e-10) else "open"
    responses=tuple(_b_operator(identifier,value).combined_operator for identifier in B_IDS)
    return legacy.RippleSpatialClosure(C_ID,responses,np.asarray(theta_hat),residual,residual,objective,coercivity,status)


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


def _remove_b(removed_index,value):
    complete=_c_operator(value)
    active=[True,True,True]; active[removed_index]=False
    removed_theta,_,_,_=_reconstruct(value,tuple(active))
    return source_removal_result(ComplexId(B_IDS[removed_index]),complete.local_field,removed_theta,tolerance=max(value.tolerance,1e-12))


def contracts():
    result=[contract for contract in legacy.contracts() if contract.level is ComplexLevel.A]
    domain=DomainSpec("Elastic-pi Ripple source-faithful finite field","uniform finite wave grid and exact memory, shock, tomography, and MSE operators",(legacy.RippleInput,))
    artifact=ArtifactSpec(("wave_field_csv","tomography_matrix","reconstruction_table"),"python -m the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts.simulation.run_contract_suite")
    for identifier,source_ids in legacy.B_SPECS:
        result.append(ComplexContract(ComplexId(identifier),APPENDIX,APPENDIX_SHA256,ComplexLevel.B,tuple(ComplexId(item) for item in source_ids),domain,CodomainSpec(f"{identifier} source-faithful law","finite realization of the exact appendix B operator",(legacy.RippleSynthesis,)),partial(_b_operator,identifier),residual=lambda source,output,cid=identifier:_residual(cid,output.residual,source.tolerance),source_removal_checks=tuple(partial(_remove_a,identifier,index) for index in range(len(source_ids))),artifact_spec=artifact,exact_semantics=False,implementation_path=IMPLEMENTATION_PATH))
    result.append(ComplexContract(ComplexId(C_ID),APPENDIX,APPENDIX_SHA256,ComplexLevel.C,tuple(ComplexId(item) for item in B_IDS),domain,CodomainSpec(f"{C_ID} source-faithful closure","finite coercive MSE reconstruction with all three residual blocks",(legacy.RippleSpatialClosure,)),_c_operator,residual=lambda source,output:_residual(C_ID,(output.boundary_residual,output.reconstruction_residual),max(source.tolerance,1e-10)),closure_predicate=lambda output,residual:output.status=="closed" and output.coercivity>0.0 and residual is not None and residual.passed,source_removal_checks=tuple(partial(_remove_b,index) for index in range(len(B_IDS))),artifact_spec=artifact,exact_semantics=False,implementation_path=IMPLEMENTATION_PATH))
    return tuple(result)

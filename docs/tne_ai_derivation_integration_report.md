# TNE AI derivation integration report

## Result

The canonical AI runtime is CPU-testable and differentiable through PyTorch.
It implements three bounded, source-complete 4A→2B→1C chains: seven QENN,
seven PGQENN, and seven SOInet theorem complexes. The remaining 50 AI-appendix
complexes remain `proxy_only`; no legacy prototype is promoted by file
existence alone.

The audit's cross-appendix AI derivation matrix has 280 verified rows. Eleven
shared primitives are currently marked `integrated_shared_primitive`; 269 stay
`planned`. The matrix excludes the AI appendix's own 71 rows, whose direct
implementation state is recorded in the 351-row theorem matrix.

## Canonical structure

```text
shared Flowpoint / C2 / DFI / pDFI / Elastic-pi / spectral primitives
    ├── QENN: reversible state, projectors, spectral memory, collapse readout
    ├── PGQENN: prime/parity growth, typed 2-adic depth, graph messages
    └── SOInets: multiple QENN+PGQENN subnetworks, memory and meta-closure
```

QENN uses exact `F(x)=-x`, invariant/anti-invariant projectors, bias-free
C2-equivariant maps, fail-closed normalized DFI, exact unclipped Elastic-π
gains, finite Fourier reconstruction, observation/collapse probabilities, and
residual-based arbitration.

PGQENN uses a deterministic prime/parity/2-adic growth law. The former
`random.sample` behavior is isolated as the seeded
`stochastic_comparison_ablation`; it is not the canonical graph law. Message
passing is Flowpoint/C2 equivariant and combines parity-conditioned pDFI,
Elastic-π gains, graph locality, and Parseval diagnostics without an optional
graph framework.

SOInets runs multiple QENN and PGQENN subnetworks, aggregates their collapse
readouts, transfers memory in both directions, and evaluates spectral, spatial,
boundary, observability, and subnetwork completeness residuals. Its actual
appendix source dependencies are B19=A01+A13, B20=A02+A14, and C29=B19+B20.

## Observable output capabilities

Six bounded output capabilities now connect these shared primitives to
deterministic visual and auditory evidence: color classification, sound
classification, bidirectional color classification, bidirectional sound
classification, color cloning, and sound cloning. Each implementation owns a
colocated `test/` and `simulation/` producer with compact data, figures,
animations, manifests, and representative audio where applicable. The folder
mapping, semantics, results, and regeneration commands are documented in
`docs/tne_ai_output_capabilities.md`.

In addition, QENN, PGQENN, and SOInets each own architecture-local test and
simulation runners that import the respective model, record native architecture
residuals, and execute all six output groups. This demonstrates that the six
observable capabilities are reachable through every canonical AI architecture,
while retaining their bounded synthetic-fixture claim boundary.

These are numerical capability demonstrations, not additional theorem-complex
certifications. Their manifests therefore reference related implemented source
laws without changing the 351-row implementation inventory.

## Shared derivations currently wired

The integrated rows include the canonical Flowpoint involution, finite parity
and 2-adic coding, spectral history/Fourier reconstruction,
invariant/anti-invariant channels, normalized DFI, parity-conditioned pDFI,
the pDFI–Elastic interface, and Elastic-π graph curvature. Exact IDs and usage
evidence are in `docs/data/ai_derivation_integration_matrix.csv`.

## Failure and claim boundaries

- NaN and infinity raise typed obstructions; they are not neutralized.
- DFI/pDFI zero denominators or predecessors fail closed.
- Elastic-π evaluation is unclipped in the canonical differentiable gate.
- Every implemented B law has two source-removal witnesses and a positive
  non-cancelling residual energy.
- Every implemented C law has a spatial/local operator, boundary/localization,
  reconstruction, coercivity or observability diagnostics, and both-B
  ablations.
- Successful finite C evaluations remain `numerical_candidate`.

## Commands

```bash
python -m pip install -r requirements-ai.txt
python -m pytest -q tests/numerical/test_qenn_model.py tests/numerical/test_pgqenn_model.py tests/numerical/test_soinets_model.py
python -m pytest -q tests/contracts/test_qenn_contracts.py tests/contracts/test_pgqenn_contracts.py tests/contracts/test_soinets_contracts.py
python -m pytest -q the_nothingness_effect/artificial_intelligence/*/test
```

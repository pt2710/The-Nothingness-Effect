# TNE multimodal architecture

## Visible repository module

The canonical trainable product is now directly visible at
`the_nothingness_effect/artificial_intelligence/multimodal/`:

```text
multimodal/
  model.py
  axes.py
  rbm.py
  growth.py
  data.py
  training.py
  validation.py
  evaluation.py
  artifacts.py
  network_artifacts.py
  test/run_pipeline.py
  test/artifacts/
  simulation/run_pipeline.py
  simulation/artifacts/
```

`TNETrainableMultimodalModel` adds per-sample classification and shared-token
reconstruction heads over the complete `TNEMultimodalSOInet` backbone. The
older `soinets/multimodal.py` location remains the typed backbone and
compatibility import; it is no longer the only discoverable multimodal entry.

## Canonical dataflow

`TNEMultimodalSOInet` implements the following bounded, differentiable chain:

```text
named raw modalities
  -> per-modality observation/collapse
  -> common finite energy-token carrier
  -> one shared encoder
  -> normalized DFI modality fields
  -> exact Elastic-pi and Elastic Dubler ratios
  -> learned shared/private modality axes with forward/reverse cycle residual
  -> local per-axis Gaussian-Bernoulli RBM energy states
  -> Elastic-Dubler/RBM-regulated modality weights
  -> bounded modality-specific prototype clusters and deterministic growth
  -> global cross-axis RBM regulator
  -> weighted superposition and latent collapse
  -> SOInets(QENN, PGQENN)
  -> observation/collapse readout and shared token reconstructions
```

The encoder and decoder are shared across color, sound, vision, or any other finite tensor modality. Modality names provide the explicit domains for the Dubler comparison; they do not select private feature extractors.

The modality-axis network learns a shared comparison sector and a private
coordinate sector for each named input. Pairwise transport is computed from
the shared coordinates, while a reverse map exposes cycle and identity
residuals. Local RBMs encode slow energy statistics per axis; a global RBM
couples all axis latents and regulates the fusion precision. The RBM is an
external numerical realization, not a TNE source law, and its free energy,
contrastive-divergence quantity, and visible reconstruction residual remain
explicit.

`AdaptiveModalityClusterNetwork` grows bounded modality-specific prototypes
when novelty crosses a declared threshold. Its centroids, assignments,
connectivity, capacity, coverage residual, and spawn/update events are
observable. Cluster context contributes to the final hidden state; it is not a
diagnostic-only sidecar.

The ratio-preserving fusion law is

```text
w_A / w_B = pi_E(A) / pi_E(B) = exp(-(S_A - S_B) / K_D).
```

It is evaluated without exponent clipping. Exchange, diagonal, additive log-cocycle, ratio identity, and normalization residuals are explicit. The bridge uses these ratios as modality precision, but does not reinterpret them as physical frequencies, learning rates, or proof of cross-modal equivalence.

## Inherited dependency chain

- QENN uses Flowpoint projectors, DFI, pDFI, exact Elastic-pi, the Elastic-pi transition norm, the Elastic Dubler feature-window bridge, DTQC, spectral memory/Parseval, observation/collapse, and completeness arbitration.
- PGQENN consumes the complete QENN output and the pinned MPL-TC prime/motif stream.
- SOInets aggregate QENN and PGQENN subnetworks, bidirectional memory, spatial/spectral residuals, and meta-level observation/collapse.
- The multimodal wrapper supplies modality-level observation, Dubler fusion, latent collapse, and shared token reconstruction without redefining any upstream source law.

## External design context

The uploaded `tne_multimodal.zip` was inspected outside the Git root. Its
working RBM, axis-bank and modal-superposition prototypes, together with its
explicitly labelled axis-graph and cluster-growth plans, supplied design
context. The repository implementation was rebuilt independently: the axis
transport is cycle-checked, cluster state affects inference, and canonical TNE
operators replace clipped Elastic-pi and minimal QENN/PGQENN proxies. No source
or artifact was copied. The authoritative appendix laws and current typed
repository runtime take precedence. The source ZIP hash and reuse boundary are
recorded in `docs/data/multimodal_reference_context_manifest.json`.

## Artifacts and commands

The canonical train/validate/evaluate producers write beneath the visible
multimodal package:

```bash
python -m the_nothingness_effect.artificial_intelligence.multimodal.test.run_pipeline
python -m the_nothingness_effect.artificial_intelligence.multimodal.simulation.run_pipeline
```

Each producer writes nine machine-readable tables, eighteen static figures,
ten GIF animations, and two provenance manifests. Evidence includes loss and
accuracy curves, gradient norms, modality-weight trajectories, held-out
confusion, calibration, latent PCA, modality similarity, exact Elastic-Dubler
ratios, reconstruction error, the TNE residual spectrum, and named
observation, Elastic-Dubler, modality-axis, RBM-regulator, and cluster-context
source-removal comparisons. The additional network evidence includes the full
executable topology, axis transport and cycle matrices, a local/global RBM
bipartite graph, cluster topology, and the RBM energy landscape. The animations show
loss, latent geometry, modality weights, confusion, and cross-modal token
reconstruction across training, plus topology activation, network assembly,
axis learning, cluster self-growth, and visible-hidden-visible RBM
reconstruction.

The test producer uses 12 epochs; the simulation producer uses 40. With seed 0
the current deterministic synthetic fixture reaches 100% held-out
classification accuracy after 40 epochs. This is pipeline evidence, not an
empirical generalization claim: the calibration and reconstruction metrics
remain explicit, and mathematical closure remains open.

# TNE multimodal architecture

## Visible repository module

The canonical trainable product is now directly visible at
`the_nothingness_effect/artificial_intelligence/multimodal/`:

```text
multimodal/
  model.py
  data.py
  training.py
  validation.py
  evaluation.py
  artifacts.py
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
  -> ratio-preserving modality weights
  -> weighted superposition and latent collapse
  -> SOInets(QENN, PGQENN)
  -> observation/collapse readout and shared token reconstructions
```

The encoder and decoder are shared across color, sound, vision, or any other finite tensor modality. Modality names provide the explicit domains for the Dubler comparison; they do not select private feature extractors.

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

The uploaded `tne_multimodal.zip` was inspected outside the Git root. It suggested the raw-observation → shared-encoder → Dubler-weighted-superposition organization. Its QENN, PGQENN, and clipped Elastic-pi implementations were proxy code and were not copied. The authoritative appendix laws and current typed repository runtime take precedence. The source ZIP hash and reuse boundary are recorded in `docs/data/multimodal_reference_context_manifest.json`.

## Artifacts and commands

The canonical train/validate/evaluate producers write beneath the visible
multimodal package:

```bash
python -m the_nothingness_effect.artificial_intelligence.multimodal.test.run_pipeline
python -m the_nothingness_effect.artificial_intelligence.multimodal.simulation.run_pipeline
```

Each producer writes seven machine-readable tables, twelve static figures, five
GIF animations, and one provenance manifest. Evidence includes loss and
accuracy curves, gradient norms, modality-weight trajectories, held-out
confusion, calibration, latent PCA, modality similarity, exact Elastic-Dubler
ratios, reconstruction error, the TNE residual spectrum, and named
observation/Elastic-Dubler source-removal comparisons. The animations show
loss, latent geometry, modality weights, confusion, and cross-modal token
reconstruction across training.

The test producer uses 12 epochs; the simulation producer uses 40. With seed 0
the current deterministic synthetic fixture reaches 100% held-out
classification accuracy after 40 epochs. This is pipeline evidence, not an
empirical generalization claim: the calibration and reconstruction metrics
remain explicit, and mathematical closure remains open.

# TNE multimodal architecture

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

The producers write only beneath the SOInets folders:

```bash
python -m the_nothingness_effect.artificial_intelligence.soinets.test.run_multimodal
python -m the_nothingness_effect.artificial_intelligence.soinets.simulation.run_multimodal
```

Each producer writes a metrics table, Dubler ratio/weight figure, and provenance manifest. The simulation producer additionally writes a small modality-weight animation. Synthetic fixtures demonstrate finite computational behavior only; the untrained reconstruction residual remains visible and the aggregate model status remains open.

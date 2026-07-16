# TNE AI output capabilities

## Result

The Artificial Intelligence runtime now produces six bounded, deterministic
output groups. Each group owns its implementation and has separate `test/` and
`simulation/` producers. CSV/JSON data, figures, animations, and representative
audio files are written beside the script that generated them.

The former `tne_concepts/SOInet/test_*_data` directories were legacy result
dumps rather than implementations. They contained 1,566 tracked files
(83,879,697 bytes) and were removed. Repository-root copies created as an
import-time side effect were also removed. The entire historical `tne_concepts`
tree is absent; canonical producers no longer create root output folders.

## Meaning preserved from the removed names

| Removed legacy directory | Intended AI output | Canonical location |
| --- | --- | --- |
| `test_color_classification_data` | Classify color to demonstrate bounded visual perception | `the_nothingness_effect/artificial_intelligence/color_classification/` |
| `test_sound_classification_data` | Classify tonal sound to demonstrate bounded auditory perception | `the_nothingness_effect/artificial_intelligence/sound_classification/` |
| `test_bidirectional_color_classification_data` | RGB image → label → RGB prototype → label closure | `the_nothingness_effect/artificial_intelligence/bidirectional_color_classification/` |
| `test_bidirectional_sound_classification_data` | Waveform → label → prototype tone → label closure | `the_nothingness_effect/artificial_intelligence/bidirectional_sound_classification/` |
| `test_image_cloning_data` | Clone finite color-image content | `the_nothingness_effect/artificial_intelligence/color_cloning/` |
| `test_sound_cloning_data` | Clone finite sound-wave content | `the_nothingness_effect/artificial_intelligence/sound_cloning/` |

## Organization standard

Every capability follows the same repository-local form:

```text
<capability>/
    __init__.py
    model.py
    test/
        test_capability.py
        <capability>_test_results.csv
        <capability>_test_figure.png
        <capability>_test_manifest.json
    simulation/
        run_simulation.py
        <capability>_simulation_results.csv
        <capability>_simulation_figure.png
        <capability>_simulation_animation.gif
        <capability>_simulation_manifest.json
        [representative .wav files for auditory capabilities]
```

The test script imports the implementation from its parent capability. The
simulation script does the same. Neither producer writes to the repository
root, a shared generic artifact directory, or another capability's folder.

QENN, PGQENN, and SOInets also each own an architecture-level `test/` and
`simulation/` suite. Those scripts import the respective model, evaluate its
native residuals and observation/collapse output, then run all six capability
groups into architecture-local subdirectories.

SOInets additionally supplies the backbone for a canonical multimodal model. Named color, sound,
vision, or other finite tensor modalities pass through observation/collapse,
one shared encoder, exact Elastic-Dubler weighting, latent fusion/collapse,
and the complete QENN/PGQENN SOInet backbone. Its metrics, figure, simulation
GIF, and manifest remain under `soinets/test/artifacts/multimodal` and
`soinets/simulation/artifacts/multimodal` as compact backbone evidence.

The separately discoverable trainable product lives at
`artificial_intelligence/multimodal`. Its test and simulation producers train,
validate, and evaluate batch-level classification plus shared-token
reconstruction, and each writes 7 tables, 12 figures, 5 animations, and a
provenance manifest beneath its own `artifacts` directory.

## Implemented semantics

- Color classification consumes normalized RGB images and observes one of six
  prototypes: red, green, blue, cyan, magenta, or yellow.
- Sound classification consumes finite normalized waveforms and observes one
  of three tonal prototypes: 250 Hz, 500 Hz, or 1,000 Hz.
- Bidirectional classification requires exact label roundtrip closure. The
  reverse modality is the observed class prototype, not a claim of exact input
  recovery; its separate modality RMSE remains visible.
- Color and sound cloning use a finite FFT, the Flowpoint dual `F(x)=-x`, the
  inverse Flowpoint, and an inverse FFT. Reconstruction, imaginary leakage,
  Parseval, and involution residuals are explicit.
- Classification composes Flowpoint anti-invariant projection, normalized DFI,
  exact unclipped Elastic-π gain, and normalized observation/collapse.
- NaN, infinity, invalid shapes, out-of-range RGB/amplitude values, silent
  audio, and invalid parameters fail closed.

All successful outputs remain `numerical_candidate`. The synthetic fixtures
demonstrate finite visual/auditory behavior and do not establish general-world
vision, hearing, generative intelligence, or a formal theorem proof.

## Current deterministic results

| Capability | Test result | Simulation result |
| --- | --- | --- |
| Color classification | accuracy 1.0 | accuracy 1.0 |
| Sound classification | accuracy 1.0 | accuracy 1.0 |
| Bidirectional color classification | accuracy 1.0; roundtrip 1.0 | accuracy 1.0; roundtrip 1.0 |
| Bidirectional sound classification | accuracy 1.0; roundtrip 1.0 | accuracy 1.0; roundtrip 1.0 |
| Color cloning | RMSE `4.63e-8` | RMSE `6.02e-8` |
| Sound cloning | RMSE `5.69e-8` | RMSE `5.30e-8` |

## Regeneration

Replace `<capability>` with any canonical location from the mapping table.

```bash
python -m the_nothingness_effect.artificial_intelligence.<capability>.test.test_capability
python -m the_nothingness_effect.artificial_intelligence.<capability>.simulation.run_simulation
```

Run all six colocated tests with:

```bash
python -m pytest -q the_nothingness_effect/artificial_intelligence/*/test
```

Run all six output groups through each complete architecture with:

```bash
python -m the_nothingness_effect.artificial_intelligence.qenn.test.run_all_capabilities
python -m the_nothingness_effect.artificial_intelligence.qenn.simulation.run_all_capabilities
python -m the_nothingness_effect.artificial_intelligence.pgqenn.test.run_all_capabilities
python -m the_nothingness_effect.artificial_intelligence.pgqenn.simulation.run_all_capabilities
python -m the_nothingness_effect.artificial_intelligence.soinets.test.run_all_capabilities
python -m the_nothingness_effect.artificial_intelligence.soinets.simulation.run_all_capabilities
python -m the_nothingness_effect.artificial_intelligence.soinets.test.run_multimodal
python -m the_nothingness_effect.artificial_intelligence.soinets.simulation.run_multimodal
python -m the_nothingness_effect.artificial_intelligence.multimodal.test.run_pipeline
python -m the_nothingness_effect.artificial_intelligence.multimodal.simulation.run_pipeline
```

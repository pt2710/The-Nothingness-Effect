# TNE multimodal AI

This is the visible trainable multimodal architecture. It combines aligned
color, sound and vision inputs through the canonical SOInet backbone and adds
batch-level classification and shared-token reconstruction heads.

The package separates `model.py`, `data.py`, `training.py`, `validation.py`,
`evaluation.py`, and `artifacts.py`. Test and simulation producers write their
metrics, figures, animations, and provenance beneath their own `artifacts`
directories.

```bash
python -m the_nothingness_effect.artificial_intelligence.multimodal.test.run_pipeline
python -m the_nothingness_effect.artificial_intelligence.multimodal.simulation.run_pipeline
```

The bundled data are deterministic synthetic fixtures for runtime QA. They are
not empirical training data and do not establish formal mathematical closure.

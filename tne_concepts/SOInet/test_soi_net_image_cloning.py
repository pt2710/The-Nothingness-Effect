"""Deprecated entry point for canonical color cloning evidence."""

from __future__ import annotations

import warnings

from equations.artificial_intelligence.color_cloning.test.test_capability import run_test


def main() -> int:
    warnings.warn(
        "test_soi_net_image_cloning.py is a compatibility entry point; use "
        "equations.artificial_intelligence.color_cloning.test.test_capability",
        DeprecationWarning,
        stacklevel=2,
    )
    outputs = run_test()
    print(f"generated_files={len(outputs['generated_files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

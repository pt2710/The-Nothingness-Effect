"""Replace legacy workstation paths in tracked JSON manifests.

The transformation is deliberately narrow: it recognizes the two historical
repository prefixes and maps them to canonical repository-relative paths.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PREFIX = re.compile(
    r"[A-Za-z]:[/\\][^\"\r\n]*?[/\\]the_nothingness_effect[/\\]the_nothingness_effect[/\\]",
    re.IGNORECASE,
)
HAWKING_PREFIX = re.compile(
    r"[A-Za-z]:[/\\][^\"\r\n]*?[/\\]the_nothingness_effect[/\\]"
    r"theoretical_benchmarks[/\\]hawking[/\\](?:simulation|comparison)[/\\]",
    re.IGNORECASE,
)
HAWKING_DESTINATION = (
    "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
    "black_holes_hawking_radiation_and_observer_horizons/hawking/simulation/"
    "theoretical_benchmarks/"
)


def transform(value: Any) -> Any:
    if isinstance(value, str):
        original = value
        for prefix in (str(ROOT), ROOT.as_posix()):
            value = value.replace(prefix + "\\", "").replace(prefix + "/", "")
        value = HAWKING_PREFIX.sub(HAWKING_DESTINATION, value)
        value = PACKAGE_PREFIX.sub("the_nothingness_effect/", value)
        return value.replace("\\", "/") if value != original else value
    if isinstance(value, list):
        return [transform(item) for item in value]
    if isinstance(value, dict):
        return {key: transform(item) for key, item in value.items()}
    return value


def main() -> int:
    changed = 0
    for path in ROOT.rglob("*.json"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            original = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        updated = transform(original)
        if updated != original:
            path.write_text(
                json.dumps(updated, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            changed += 1
    print(f"sanitized_manifest_files={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

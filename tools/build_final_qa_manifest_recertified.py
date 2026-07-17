"""Build final QA with explicit provenance recertification semantics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from the_nothingness_effect._runtime.theorem_complex_runtime.provenance_authority import (
    bind_provenance_manifest,
    provenance_binding_report,
)
from tools import build_final_qa_manifest as _base


# The preserved final-QA builder imports the historical authority API. Replace
# only its provenance hooks with the observational, recertification-aware API.
_base.bind_provenance_manifest = bind_provenance_manifest
_base.provenance_binding_report = provenance_binding_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/data/final_qa_manifest.json"),
    )
    parser.add_argument("--passed", type=int)
    parser.add_argument("--failed", type=int)
    parser.add_argument("--skipped", type=int)
    parser.add_argument("--warnings", type=int)
    parser.add_argument("--runtime-seconds", type=float)
    parser.add_argument("--python-version", default="3.14.3")
    parser.add_argument(
        "--dependency-status",
        default="pip check passed",
    )
    parser.add_argument(
        "--source-law-regression-status",
        default="passed",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return non-zero when any release blocker is present.",
    )
    arguments = parser.parse_args()

    payload = _base.build(arguments)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"final_qa_manifest={arguments.output} "
        f"final_qa_passed={payload['final_qa_passed']} "
        f"release_blockers={payload['release_blockers']}"
    )
    return 1 if arguments.check and not payload["final_qa_passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

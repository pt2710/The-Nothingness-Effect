"""Build a fail-closed ledger for OPEN and NUMERICAL_CANDIDATE contracts.

The ledger does not promote a runtime implementation to mathematical closure.
It records the exact residual/tolerance state and the additional evidence required
before each status may change.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
from typing import Any


OPEN_STATUSES={"open","numerical_candidate"}


def _norm(values: Any) -> float:
    if not isinstance(values,list): return 0.0
    return sum(float(item)**2 for item in values)**0.5


def _tolerance(manifest: dict[str,Any]) -> float:
    raw=manifest.get("numeric_tolerances",{})
    if not isinstance(raw,dict) or not raw: return 0.0
    return max(float(item) for item in raw.values())


def _requirements(status: str, exact: bool, validation: str) -> list[str]:
    requirements=[]
    if status=="open":
        requirements.extend((
            "resolve the failing invariant, residual, domain boundary, or closure predicate",
            "rerun positive and counterexample witnesses after the mathematical correction",
        ))
    elif status=="numerical_candidate":
        requirements.extend((
            "establish attainment or explicitly retain candidate status",
            "establish uniqueness/identifiability or report the nullspace",
            "supply convergence, discretization and boundary-leakage evidence",
        ))
    if not exact:
        requirements.append("prove finite realization equivalence or retain exact_semantics=false")
    if validation!="empirical":
        requirements.append("supply independent empirical evidence before any empirical claim")
    return requirements


def build(status_path: Path,provenance_path: Path,csv_output: Path,json_output: Path) -> dict[str,object]:
    status_payload=json.loads(status_path.read_text(encoding="utf-8"))
    provenance=json.loads(provenance_path.read_text(encoding="utf-8"))
    status_records=status_payload.get("records")
    manifests=provenance.get("manifests")
    if not isinstance(status_records,list) or not isinstance(manifests,list):
        raise RuntimeError("status/provenance record list missing")
    status_by_id={str(item["complex_id"]):item for item in status_records if isinstance(item,dict)}
    manifest_by_id={str(item["theorem_complex_id"]):item for item in manifests if isinstance(item,dict)}
    rows=[]
    for identifier,status_record in sorted(status_by_id.items()):
        closure=str(status_record.get("closure_status","untested"))
        if closure not in OPEN_STATUSES: continue
        manifest=manifest_by_id.get(identifier)
        if manifest is None: raise RuntimeError(f"missing provenance for open contract: {identifier}")
        approximation=manifest.get("approximation_metadata",{})
        exact=bool(approximation.get("exact_semantics",False)) if isinstance(approximation,dict) else False
        residual=manifest.get("residual_vector",[])
        validation=str(status_record.get("validation_status","untested"))
        requirements=_requirements(closure,exact,validation)
        rows.append({
            "complex_id":identifier,
            "appendix_file":str(status_record.get("appendix_file","")),
            "level":str(status_record.get("level","")),
            "runtime_status":str(status_record.get("runtime_status","")),
            "source_exactness":str(status_record.get("source_exactness","")),
            "closure_status":closure,
            "validation_status":validation,
            "artifact_status":str(status_record.get("artifact_status","")),
            "exact_semantics":exact,
            "residual_norm":_norm(residual),
            "tolerance":_tolerance(manifest),
            "residual_component_count":len(residual) if isinstance(residual,list) else 0,
            "required_evidence":"; ".join(requirements),
            "implementation_path":str(status_record.get("implementation_path","")),
        })
    csv_output.parent.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0]) if rows else ["complex_id"]
    with csv_output.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    counts=dict(Counter(str(row["closure_status"]) for row in rows))
    report={
        "schema_version":"1.0",
        "open_or_numerical_candidate_count":len(rows),
        "counts":counts,
        "all_open_states_represented":len(rows)==int(status_payload.get("open_and_numerical_candidate_preserved",-1)),
        "policy":"runtime implementation does not imply mathematical closure or empirical validation",
        "records":rows,
    }
    json_output.parent.mkdir(parents=True,exist_ok=True)
    json_output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if not report["all_open_states_represented"]:
        raise RuntimeError("closure obligation ledger is incomplete")
    return report


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status",type=Path,default=Path("reports/release_status_dimensions.json"))
    parser.add_argument("--provenance",type=Path,default=Path("reports/effective_artifact_provenance_manifest.json"))
    parser.add_argument("--csv-output",type=Path,default=Path("reports/closure_obligation_ledger.csv"))
    parser.add_argument("--json-output",type=Path,default=Path("reports/closure_obligation_ledger.json"))
    args=parser.parse_args()
    report=build(args.status,args.provenance,args.csv_output,args.json_output)
    print(f"closure_obligation_ledger=passed rows={report['open_or_numerical_candidate_count']}")
    return 0


if __name__=="__main__": raise SystemExit(main())

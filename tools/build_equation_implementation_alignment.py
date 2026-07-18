"""Build a one-to-one appendix-equation to executable-contract alignment matrix."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from the_nothingness_effect._runtime.theorem_complex_runtime.authority import (
    bind_inventory_rows,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.catalog import (
    active_contracts,
)


DEFAULT_MATRIX=Path("docs/data/theorem_complex_implementation_matrix.csv")
SOURCE_FAITHFUL_OVERRIDE=Path("docs/data/authority_overrides/source_faithful_higher_order.json")
SPECIALIZED_EVIDENCE_PATHS={
    "parity_elastic_spectral_spatial_closure": (
        "the_nothingness_effect/gravitational_cosmological_and_quantum_dynamics_architecture/"
        "the_elastic_dubler_effect/parity_elastic_spectral_contract.py"
    ),
}


def _callable_name(value: Any) -> tuple[str,str]:
    if value is None: return "",""
    module=str(getattr(value,"__module__",type(value).__module__))
    name=str(getattr(value,"__qualname__",getattr(value,"__name__",type(value).__qualname__)))
    return module,name


def build(matrix_path: Path,csv_output: Path,json_output: Path) -> dict[str,object]:
    with matrix_path.open(newline="",encoding="utf-8-sig") as handle:
        source_rows=list(csv.DictReader(handle))
    rows=bind_inventory_rows(source_rows)
    registry={str(contract.complex_id):contract for contract in active_contracts()}
    override_payload=json.loads(SOURCE_FAITHFUL_OVERRIDE.read_text(encoding="utf-8"))
    correction_records=override_payload["implementation_status_overrides"]
    corrected_ids=set(correction_records)
    unknown_specialized=set(SPECIALIZED_EVIDENCE_PATHS)-corrected_ids
    if unknown_specialized:
        raise RuntimeError(
            f"specialized evidence without source-faithful correction: {sorted(unknown_specialized)}"
        )
    records=[]
    errors=[]
    for row in rows:
        identifier=row["complex_id"]
        contract=registry.get(identifier)
        if contract is None:
            errors.append(f"missing_contract:{identifier}")
            continue
        operator_module,operator_name=_callable_name(contract.operator)
        residual_module,residual_name=_callable_name(contract.residual)
        implementation_path=contract.implementation_path or row.get("implementation_path","")
        path_exists=bool(implementation_path) and Path(implementation_path).is_file()
        first_label=row.get("first_label","").strip()
        equation_labels=[item.strip() for item in row.get("equation_labels","").split(";") if item.strip()]
        source_ids=[str(item) for item in contract.source_ids]
        declared_evidence_path=(
            SPECIALIZED_EVIDENCE_PATHS.get(identifier)
            or correction_records.get(identifier,{}).get("evidence_path","")
        )
        evidence_path_exists=(
            bool(declared_evidence_path)
            and Path(declared_evidence_path).is_file()
        )
        evidence_path_matches=(
            identifier not in corrected_ids
            or implementation_path == declared_evidence_path
        )
        source_faithful=(
            identifier not in corrected_ids
            or (evidence_path_exists and evidence_path_matches)
        )
        mapping_complete=all((
            bool(first_label),path_exists,bool(operator_module),bool(operator_name),
            contract.appendix==row.get("appendix_file",""),
            contract.appendix_source_sha256==row.get("appendix_source_sha256",""),
            source_faithful,
        ))
        if not mapping_complete: errors.append(f"incomplete_mapping:{identifier}")
        records.append({
            "complex_id":identifier,"appendix_file":row.get("appendix_file",""),
            "level":row.get("level",""),"first_label":first_label,
            "equation_labels":";".join(equation_labels),"equation_label_count":len(equation_labels),
            "appendix_source_sha256":contract.appendix_source_sha256,
            "source_exactness":row.get("source_exactness",""),
            "source_ids":";".join(source_ids),"source_count":len(source_ids),
            "implementation_path":implementation_path,"implementation_path_exists":path_exists,
            "operator_module":operator_module,"operator_qualname":operator_name,
            "residual_module":residual_module,"residual_qualname":residual_name,
            "exact_semantics":bool(contract.exact_semantics),
            "source_faithful_formula_correction":identifier in corrected_ids,
            "declared_evidence_path":declared_evidence_path,
            "evidence_path_exists":evidence_path_exists,
            "evidence_path_matches":evidence_path_matches,
            "mapping_complete":mapping_complete,
        })
    csv_output.parent.mkdir(parents=True,exist_ok=True)
    with csv_output.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)
    report={
        "schema_version":"1.1","rows":len(records),
        "complete_mappings":sum(bool(row["mapping_complete"]) for row in records),
        "source_faithful_corrections":sum(bool(row["source_faithful_formula_correction"]) for row in records),
        "specialized_evidence_paths":len(SPECIALIZED_EVIDENCE_PATHS),
        "first_labels":sum(bool(row["first_label"]) for row in records),
        "equation_labels":sum(int(row["equation_label_count"]) for row in records),
        "errors":errors,"passed":len(records)==351 and not errors,
        "claim_boundary":"callable, label, and declared evidence-path binding; not a formal equivalence proof",
        "records":records,
    }
    json_output.parent.mkdir(parents=True,exist_ok=True)
    json_output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if not report["passed"]: raise RuntimeError(f"equation implementation alignment failed: {errors[:5]}")
    return report


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix",type=Path,default=DEFAULT_MATRIX)
    parser.add_argument("--csv-output",type=Path,default=Path("reports/equation_implementation_alignment.csv"))
    parser.add_argument("--json-output",type=Path,default=Path("reports/equation_implementation_alignment.json"))
    args=parser.parse_args()
    report=build(args.matrix,args.csv_output,args.json_output)
    print(f"equation_implementation_alignment=passed rows={report['rows']} labels={report['equation_labels']}")
    return 0


if __name__=="__main__": raise SystemExit(main())

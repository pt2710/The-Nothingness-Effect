"""Source-faithful PGQENN theorem/failure dual and product certificates."""

from __future__ import annotations

from the_nothingness_effect._runtime.theorem_complex_runtime import ArtifactSpec
from the_nothingness_effect._runtime.theorem_complex_runtime.authoritative_dual_products import build_contracts

from . import contracts as base
from . import source_contracts as extended
from .derived_contracts import B_SPECS, C_SPECS


APPENDIX = base.APPENDIX
APPENDIX_SHA256 = base.APPENDIX_SHA256
IMPLEMENTATION_PATH = "the_nothingness_effect/artificial_intelligence/pgqenn/authoritative_contracts.py"
A_IDS = tuple(str(item) for item in (*base.A_IDS, *extended.SOURCE_IDS))
B_IDS = tuple(str(item) for item in base.B_IDS) + tuple(item[0] for item in B_SPECS)
C_IDS = tuple(str(item) for item in base.C_IDS) + tuple(item[0] for item in C_SPECS)
B_SOURCE_GROUPS = (
    tuple(str(item) for item in base.A_IDS[:2]),
    tuple(str(item) for item in base.A_IDS[2:4]),
    *(tuple(item) for _identifier, item in B_SPECS),
)
C_SOURCE_GROUPS = (
    tuple(str(item) for item in base.B_IDS),
    *(tuple(item) for _identifier, item in C_SPECS),
)


def _source_law(index: int, value: base.PGQENNContractInput):
    if index < len(base.A_IDS):
        return base.source_operator(index, value)
    return extended.source_operator(index - len(base.A_IDS), value)


def contracts():
    return build_contracts(
        appendix=APPENDIX,
        appendix_sha256=APPENDIX_SHA256,
        implementation_path=IMPLEMENTATION_PATH,
        input_type=base.PGQENNContractInput,
        input_name="PGQENN prime-graph theorem/failure field",
        input_description="finite pinned MPL-TC prime graph and aligned finite node features",
        source_ids=A_IDS,
        b_ids=B_IDS,
        c_ids=C_IDS,
        b_source_groups=B_SOURCE_GROUPS,
        c_source_groups=C_SOURCE_GROUPS,
        source_law=_source_law,
        artifact_spec=ArtifactSpec(
            ("branch_classification_table", "projection_table", "source_removal_table"),
            "python -m the_nothingness_effect.artificial_intelligence.pgqenn.simulation.run_contract_suite",
        ),
    )

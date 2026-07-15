"""Apply the deterministic one-time import/path migration to tracked text files."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MODULE_MAP = {
    "equations.gravitational_cosmological_quantum_dynamics": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture",
    "equations.elastic_dubler_interferometry": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.elastic_dubler_interferometry_probing_gravitational_curvature",
    "equations.cosmological_spark_dynamics": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.emergent_cosmological_spark_dynamics",
    "equations.elastic_dubler_effect": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect",
    "equations.black_hole_dynamics": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons",
    "equations.locality_driven_gravity": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity",
    "equations.elastic_pi_ripples": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts",
    "equations.dtqc": "the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.discrete_time_quasicrystals_in_the_flowpoint",
    "equations.fluctuation_elastic_dynamics": "the_nothingness_effect.fluctuation_and_elastic_dynamics",
    "equations.dynamic_fluctuation_index": "the_nothingness_effect.fluctuation_and_elastic_dynamics.dynamic_fluctuation_index",
    "equations.parity_dfi": "the_nothingness_effect.fluctuation_and_elastic_dynamics.parity_adapted_dynamic_fluctuation_index",
    "equations.elastic_pi_norm": "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi_norm",
    "equations.elastic_pi": "the_nothingness_effect.fluctuation_and_elastic_dynamics.elastic_pi",
    "equations.mathematical_closure": "the_nothingness_effect.mathematical_architecture",
    "equations.flowpoint_math_operations": "the_nothingness_effect.mathematical_architecture.flowpoint_math_operations",
    "equations.flowpoint_trigonometry": "the_nothingness_effect.mathematical_architecture.flowpoint_trigonometry",
    "equations.flowpoint_pi": "the_nothingness_effect.mathematical_architecture.flowpoint_pi_approximation",
    "equations.observation_and_collapse": "the_nothingness_effect.foundational_architecture.observation_and_collapse",
    "equations.spectrum_of_infinities": "the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities",
    "equations.uncountable_infinity": "the_nothingness_effect.foundational_architecture.uncountable_infinity",
    "equations.countable_infinity": "the_nothingness_effect.foundational_architecture.countable_infinity",
    "equations.spatiality": "the_nothingness_effect.foundational_architecture.spatiality",
    "equations.symmetry": "the_nothingness_effect.foundational_architecture.symmetry",
    "equations.duality": "the_nothingness_effect.foundational_architecture.duality",
    "equations.flowpoint": "the_nothingness_effect.canonical_self_negating_involution.the_flowpoint",
    "equations.artificial_intelligence": "the_nothingness_effect.artificial_intelligence",
    "equations.completeness_theorem": "the_nothingness_effect.the_completeness_theorem",
    "equations.noether_tne": "the_nothingness_effect.the_completeness_theorem.noether_structure",
    "tne_runtime": "the_nothingness_effect._runtime",
}

BARE_IMPORT_MAP = {
    "from flowpoint import ": "from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint import ",
    "from flowpoint.flowpoint import ": "from the_nothingness_effect.canonical_self_negating_involution.the_flowpoint.flowpoint import ",
    "from flowpoint_pi.fp_pi_approximation import ": "from the_nothingness_effect.mathematical_architecture.flowpoint_pi_approximation.fp_pi_approximation import ",
    "from flowpoint_trigonometry import ": "from the_nothingness_effect.mathematical_architecture.flowpoint_trigonometry import ",
    "from flowpoint_trigonometry.fp_trigonometry import ": "from the_nothingness_effect.mathematical_architecture.flowpoint_trigonometry.fp_trigonometry import ",
    "from symmetry import ": "from the_nothingness_effect.foundational_architecture.symmetry import ",
    "from symmetry.symmetry import ": "from the_nothingness_effect.foundational_architecture.symmetry.symmetry import ",
    "from duality import ": "from the_nothingness_effect.foundational_architecture.duality import ",
    "from duality.duality import ": "from the_nothingness_effect.foundational_architecture.duality.duality import ",
    "from spatiality import ": "from the_nothingness_effect.foundational_architecture.spatiality import ",
    "from spatiality.spatiality import ": "from the_nothingness_effect.foundational_architecture.spatiality.spatiality import ",
    "from countable_infinity import ": "from the_nothingness_effect.foundational_architecture.countable_infinity import ",
    "from countable_infinity.countable_infinity import ": "from the_nothingness_effect.foundational_architecture.countable_infinity.countable_infinity import ",
    "from uncountable_infinity.uncountable_infinity import ": "from the_nothingness_effect.foundational_architecture.uncountable_infinity.uncountable_infinity import ",
    "from spectrum_of_infinities.spectrum_of_infinities import ": "from the_nothingness_effect.foundational_architecture.the_spectrum_of_infinities.spectrum_of_infinities import ",
    "from observation_and_collapse import ": "from the_nothingness_effect.foundational_architecture.observation_and_collapse import ",
}

TEXT_SUFFIXES = {
    ".cfg",
    ".csv",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def replacements() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = list(BARE_IMPORT_MAP.items())
    for old, new in MODULE_MAP.items():
        pairs.append((old, new))
        pairs.append((old.replace(".", "/"), new.replace(".", "/")))
        pairs.append((old.replace(".", "\\"), new.replace(".", "\\")))
    return sorted(pairs, key=lambda item: len(item[0]), reverse=True)


def migrate() -> tuple[int, int]:
    changed_files = 0
    replacement_count = 0
    pairs = replacements()
    for path in tracked_files():
        if path.suffix.lower() not in TEXT_SUFFIXES or not path.exists():
            continue
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        migrated = text
        for old, new in pairs:
            count = migrated.count(old)
            if count:
                migrated = migrated.replace(old, new)
                replacement_count += count
        if migrated != text:
            path.write_bytes(migrated.encode("utf-8"))
            changed_files += 1
    return changed_files, replacement_count


if __name__ == "__main__":
    files, replacements_applied = migrate()
    print(f"changed_files={files} replacements={replacements_applied}")

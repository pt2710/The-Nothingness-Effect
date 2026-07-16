"""Fail if an authoritative appendix source is present or tracked in the repo."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess


AUTHORITATIVE_FILENAMES = {
    "appendix_canonical_self_negating_involution_flowpoint.tex",
    "appendix_tne_mathematical_closure_architecture.tex",
    "appendix_tne_foundational_closure_architecture.tex",
    "appendix_tne_fluctuation_and_elastic_dynamics.tex",
    "appendix_tne_gravitational_cosmological_quantum_dynamics.tex",
    "appendix_tne_artificial_intelligence_architechture.tex",
    "appendix_the_completeness_theorem.tex",
    "appendix_theorem_complex_commentary.tex",
    "appendix_tne_research_relations_implications.tex",
}
AUTHORITATIVE_SHA256 = {
    "5c44d82b34cd4c5d05d01253a62987f2f6099d582bf954a4cbdbc13b52b52206",
    "3f428e24ed9518655f94145dcd8667f979aa03c74f75695d8273da273e2538d0",
    "2679b61a1d98100ed3a13669c16c299cd9b09807bc3847d383d559c9251189ea",
    "63e5684e4c4bb016a2cc62d46574c2174fbe14eb5f50c16db825ca33b0836389",
    "3a75d4bfdbf9779255d01dd3ae3db6a848a4dc1fa67455ca1f22d5abcadf866a",
    "d711e5c4260fb61bff1ef3e7ea3be14ef093370a9ff22607d2a54e74ba8b166b",
    "8b277a89cd62e5f9843997a86d8bd35fbfce780ac3e32f56bd534052009d0038",
    "97ef1bea887e96dda531efa063ee630f89e3c7422c7c4ca306634afd1e51b585",
    "3cd520d5b025f6f241c7eb09417528276f0c6904e07aa088057c7b57803bf011",
    "5e459eed3eca36d1342bc879fc8ac3962f3c801bfd1aab733f3db081a7ed0c69",
    "3277f0ffffcc27dc37ed17f7ecf721ba32234706544ceb5cfbeb5538846f2ba2",
    "c946e19a4266f8c5c3e3dd49ed6b98740d3764cac729536e5b84c42fefba304d",
    "8847de0e94ce317e52280e075e3fb42516d2b07ddb76cc6c4ff6e507545c3842",
    "7bcc6a4b64bc688b1599c490890e4da1db10e62a9403c6fbb19fbb2638632549",
    "f0f87435af715ebacf51f58fd87c978f22355a4856ddec73061e3c500cb29a41",
    "1973d00e76f03858ed58c0ad6457e0773f17a2b8609cdb57328f7f5bb664d7aa",
}
AUTHORITATIVE_SIDECAR_FILENAMES = {
    sidecar
    for filename in AUTHORITATIVE_FILENAMES
    for sidecar in (f"{filename}.sha256", f"{Path(filename).stem}.sha256")
}


def tracked_paths(repository: Path) -> list[Path]:
    completed = subprocess.run(
        ["git", "-C", str(repository), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [repository / item.decode("utf-8") for item in completed.stdout.split(b"\0") if item]


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main() -> int:
    repository = Path.cwd().resolve()
    tracked = tracked_paths(repository)
    forbidden_names = [
        path
        for path in tracked
        if path.name in AUTHORITATIVE_FILENAMES or path.name in AUTHORITATIVE_SIDECAR_FILENAMES
    ]
    forbidden_hashes = [
        path for path in tracked if path.is_file() and digest(path) in AUTHORITATIVE_SHA256
    ]
    working_tree_copies = [
        path
        for path in repository.rglob("*")
        if ".git" not in path.parts
        and path.is_file()
        and (path.name in AUTHORITATIVE_FILENAMES or path.name in AUTHORITATIVE_SIDECAR_FILENAMES)
    ]
    if forbidden_names or forbidden_hashes or working_tree_copies:
        print("authoritative appendix security gate failed")
        for path in sorted(set(forbidden_names + forbidden_hashes + working_tree_copies)):
            print(path.relative_to(repository))
        return 1
    tracked_tex = [path for path in tracked if path.suffix.lower() == ".tex"]
    print(
        "authoritative_appendix_files=0 authoritative_content_hash_matches=0 "
        f"tracked_tex_files={len(tracked_tex)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Move generated module outputs below their producer-local artifacts directory."""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "the_nothingness_effect"
OUTPUT_SUFFIXES = {".csv", ".json", ".png", ".gif", ".wav", ".npz", ".npy", ".mp4"}


def is_tracked(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    return subprocess.run(
        ["git", "ls-files", "--error-unmatch", relative],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def move(path: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if is_tracked(path):
            raise FileExistsError(destination)
        shutil.copy2(path, destination)
        path.unlink()
        return
    if is_tracked(path):
        subprocess.run(
            ["git", "mv", path.relative_to(ROOT).as_posix(), destination.relative_to(ROOT).as_posix()],
            cwd=ROOT,
            check=True,
        )
    else:
        shutil.move(path, destination)


def mode_root(path: Path) -> Path | None:
    current = path.parent
    while current != PACKAGE and PACKAGE in current.parents:
        if current.name in {"test", "simulation"}:
            return current
        current = current.parent
    return None


def move_mode_outputs() -> int:
    candidates = [
        path for path in PACKAGE.rglob("*")
        if path.is_file()
        and path.suffix.lower() in OUTPUT_SUFFIXES
        and "artifacts" not in path.parts
        and "theorem_complex" not in path.parts
        and "__pycache__" not in path.parts
    ]
    moved = 0
    for path in sorted(candidates, key=lambda item: len(item.parts), reverse=True):
        root = mode_root(path)
        if root is None:
            continue
        relative = path.relative_to(root)
        move(path, root / "artifacts" / relative)
        moved += 1
    return moved


def move_completeness_supplementary() -> int:
    source = PACKAGE / "the_completeness_theorem" / "supplementary"
    destination = PACKAGE / "the_completeness_theorem" / "simulation" / "artifacts" / "supplementary"
    if not source.exists():
        return 0
    moved = 0
    for path in sorted((item for item in source.rglob("*") if item.is_file()), key=lambda item: len(item.parts), reverse=True):
        move(path, destination / path.relative_to(source))
        moved += 1
    for directory in sorted((item for item in source.rglob("*") if item.is_dir()), key=lambda item: len(item.parts), reverse=True):
        if not any(directory.iterdir()):
            directory.rmdir()
    if source.exists() and not any(source.iterdir()):
        source.rmdir()
    return moved


def update_default_outputs() -> int:
    replacements = {
        "Path(__file__).resolve().parents[1] / \"supplementary\"":
            "Path(__file__).resolve().parent / \"artifacts\" / \"supplementary\"",
        "beside this script when run directly": "under this test module's artifacts directory",
        "keep all outputs beside this producer": "keep all outputs under this producer's artifacts directory",
    }
    changed = 0
    for path in PACKAGE.rglob("*.py"):
        original = path.read_text(encoding="utf-8")
        updated = original
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        while '/ "artifacts" / "artifacts"' in updated:
            updated = updated.replace('/ "artifacts" / "artifacts"', '/ "artifacts"')
        updated = re.sub(
            r"Path\(output_dir\) if output_dir is not None else "
            r"Path\(__file__\)\.resolve\(\)\.parent(?!\s*/\s*[\"']artifacts[\"'])",
            'Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent / "artifacts"',
            updated,
        )
        updated = re.sub(
            r"Path\(__file__\)\.resolve\(\)\.parent(?!\s*/\s*[\"']artifacts[\"']) "
            r"if output_dir is None else Path\(output_dir\)",
            'Path(__file__).resolve().parent / "artifacts" if output_dir is None else Path(output_dir)',
            updated,
        )
        updated = re.sub(
            r"(os\.path\.join\(script_dir,\s*)"
            r"(?:[\"']artifacts[\"']\s*,\s*){2,}",
            r'\1"artifacts", ',
            updated,
        )
        updated = re.sub(
            r"os\.path\.join\(script_dir,(?!\s*[\"']artifacts[\"']\s*,)\s*",
            'os.path.join(script_dir, "artifacts", ',
            updated,
        )
        updated = re.sub(
            r"SCRIPT_DIR\s*/\s*([\"'][^\"']+\.(?:csv|json|png|gif|wav|npz|npy|mp4)[\"'])",
            r'SCRIPT_DIR / "artifacts" / \1',
            updated,
        )
        updated = re.sub(
            r"else SCRIPT_DIR(?!\s*/\s*[\"']artifacts[\"'])",
            'else SCRIPT_DIR / "artifacts"',
            updated,
        )
        updated = re.sub(
            r'default=Path\(__file__\)\.resolve\(\)\.parent\)',
            'default=Path(__file__).resolve().parent / "artifacts")',
            updated,
        )
        updated = re.sub(
            r'default=Path\(["\']artifacts/[^"\']+["\']\)\)',
            'default=Path(__file__).resolve().parent / "artifacts")',
            updated,
        )
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    readme = PACKAGE / "the_completeness_theorem" / "README.md"
    if readme.is_file():
        original = readme.read_text(encoding="utf-8")
        updated = original
        while "simulation/artifacts/simulation/artifacts/supplementary/" in updated:
            updated = updated.replace(
                "simulation/artifacts/simulation/artifacts/supplementary/",
                "simulation/artifacts/supplementary/",
            )
        updated = re.sub(
            r"(?<!simulation/artifacts/)supplementary/",
            "simulation/artifacts/supplementary/",
            updated,
        )
        if updated != original:
            readme.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    return changed


def main() -> int:
    moved = move_mode_outputs()
    supplementary = move_completeness_supplementary()
    changed = update_default_outputs()
    print(f"moved_mode_outputs={moved} moved_supplementary={supplementary} updated_producers={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

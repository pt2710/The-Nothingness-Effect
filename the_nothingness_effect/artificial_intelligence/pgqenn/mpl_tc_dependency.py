"""Fail-closed adapter for the pinned pt2710/MPL-TC repository dependency."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType


MPL_TC_REPOSITORY_URL = "https://github.com/pt2710/MPL-TC.git"
MPL_TC_COMMIT = "056e346824e9ec9785ab45b642b3b842c88f6e56"
MPL_TC_MODULE_SHA256 = "016e7476606ba4c364dc5daa8ac1bcd77a418b1d5e244137559609e157f04dc9"
MPL_TC_SUBMODULE_PATH = "dependencies/MPL-TC"


class MPLTCDependencyError(RuntimeError):
    """Raised when the canonical MPL-TC dependency cannot be verified."""


@dataclass(frozen=True)
class MPLTCPrefix:
    primes: tuple[int, ...]
    gaps: tuple[int, ...]
    motifs: tuple[str, ...]
    motif_runs: tuple[int, ...]
    repository_url: str = MPL_TC_REPOSITORY_URL
    repository_commit: str = MPL_TC_COMMIT
    module_sha256: str = MPL_TC_MODULE_SHA256


def _default_repository() -> Path:
    configured = os.environ.get("MPL_TC_REPOSITORY")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[3] / MPL_TC_SUBMODULE_PATH


class MPLTCMotifProvider:
    """Load the bounded canonical motif API from the pinned MPL-TC checkout."""

    def __init__(self, repository: str | Path | None = None) -> None:
        self.repository = Path(repository).expanduser().resolve() if repository else _default_repository()
        self.module_path = self.repository / "mccrackns_prime_law.py"
        self._module: ModuleType | None = None
        self._verify()

    def _verify(self) -> None:
        if not self.module_path.is_file():
            raise MPLTCDependencyError(
                "MPL-TC dependency is unavailable; run `git submodule update --init --recursive` "
                "or set MPL_TC_REPOSITORY to the pinned checkout"
            )
        digest = hashlib.sha256(self.module_path.read_bytes()).hexdigest()
        if digest != MPL_TC_MODULE_SHA256:
            raise MPLTCDependencyError(
                f"MPL-TC source checksum mismatch: expected {MPL_TC_MODULE_SHA256}, received {digest}"
            )
        result = subprocess.run(
            ["git", "-C", str(self.repository), "rev-parse", "HEAD"],
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
        commit = result.stdout.strip()
        if result.returncode != 0 or commit != MPL_TC_COMMIT:
            raise MPLTCDependencyError(
                f"MPL-TC dependency must be pinned to {MPL_TC_COMMIT}; received {commit or 'unverified'}"
            )

    def _load(self) -> ModuleType:
        if self._module is not None:
            return self._module
        dependency_module = sys.modules.get("numbers_domains")
        if dependency_module is not None:
            dependency_file = Path(getattr(dependency_module, "__file__", "")).resolve()
            if dependency_file.parent != self.repository:
                raise MPLTCDependencyError("an incompatible top-level numbers_domains module is already loaded")
        module_name = "_tne_pinned_mpl_tc_mccrackns_prime_law"
        spec = importlib.util.spec_from_file_location(module_name, self.module_path)
        if spec is None or spec.loader is None:
            raise MPLTCDependencyError("unable to construct the MPL-TC module loader")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        sys.path.insert(0, str(self.repository))
        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            sys.modules.pop(module_name, None)
            raise MPLTCDependencyError(f"MPL-TC module import failed: {exc}") from exc
        finally:
            try:
                sys.path.remove(str(self.repository))
            except ValueError:
                pass
        self._module = module
        return module

    def prefix(self, count: int) -> MPLTCPrefix:
        if not isinstance(count, int) or count < 2:
            raise ValueError("MPL-TC motif prefix requires at least two nodes")
        module = self._load()
        law_class = getattr(module, "McCracknsPrimeLaw", None)
        if law_class is None:
            raise MPLTCDependencyError("pinned MPL-TC checkout does not expose McCracknsPrimeLaw")
        if count > int(law_class.max_supported_primes()):
            raise MPLTCDependencyError(
                f"requested {count} MPL-TC motifs, but the pinned finite runtime supports "
                f"{law_class.max_supported_primes()}"
            )
        law = law_class(n_primes=count, verbose=False)
        primes = tuple(int(value) for value in law.generate())
        gaps = (0, *(int(value) for value in law.get_gaps()))
        motif_rows = tuple(law.get_motifs())
        motifs = ("U1", *(str(label) for label, _run in motif_rows))
        motif_runs = (1, *(int(run) for _label, run in motif_rows))
        if not (len(primes) == len(gaps) == len(motifs) == len(motif_runs) == count):
            raise MPLTCDependencyError("MPL-TC returned an internally inconsistent motif prefix")
        return MPLTCPrefix(primes, gaps, motifs, motif_runs)

    @property
    def metadata(self) -> dict[str, str]:
        return {
            "repository": MPL_TC_REPOSITORY_URL,
            "commit": MPL_TC_COMMIT,
            "module_sha256": MPL_TC_MODULE_SHA256,
            "dependency_mode": "pinned_git_submodule",
        }

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
from typing import Literal


MPL_TC_REPOSITORY_URL = "https://github.com/pt2710/MPL-TC.git"
MPL_TC_COMMIT = "056e346824e9ec9785ab45b642b3b842c88f6e56"
MPL_TC_MODULE_SHA256 = "484e8a6326e99657eacc3e3a02b245e4709d51e11c5f743208632e8993124046"
MPL_TC_TRIADIC_MODULE_SHA256 = "28e92714bd17c83f03c1208758caf3313f6e6f0ca5c211a596d067893af80592"
MPL_TC_SUBMODULE_PATH = "dependencies/MPL-TC"
TCStreamKind = Literal[
    "pure_even_lift",
    "first_order_odd",
    "lpf_odd_composite",
    "mixed_even_composite",
]


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


@dataclass(frozen=True)
class MPLTCAxisPlacement:
    value: int
    domain: str
    axis: str
    stream_kind: TCStreamKind
    least_prime_factor: int | None = None
    cofactor: int | None = None
    dyadic_depth: int = 0


@dataclass(frozen=True)
class MPLTCTriadicStreams:
    pure_even_lifts: tuple[MPLTCAxisPlacement, ...]
    first_order_odds: tuple[MPLTCAxisPlacement, ...]
    lpf_odd_composites: tuple[MPLTCAxisPlacement, ...]
    mixed_even_composites: tuple[MPLTCAxisPlacement, ...]
    finite_limit: int
    repository_url: str = MPL_TC_REPOSITORY_URL
    repository_commit: str = MPL_TC_COMMIT
    module_sha256: str = MPL_TC_TRIADIC_MODULE_SHA256

    @property
    def placements(self) -> tuple[MPLTCAxisPlacement, ...]:
        return (
            *self.pure_even_lifts,
            *self.first_order_odds,
            *self.lpf_odd_composites,
            *self.mixed_even_composites,
        )


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
        self.triadic_module_path = self.repository / "triadic_domains.py"
        self._module: ModuleType | None = None
        self._triadic_module: ModuleType | None = None
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
        if not self.triadic_module_path.is_file():
            raise MPLTCDependencyError("MPL-TC triadic domain module is unavailable")
        triadic_digest = hashlib.sha256(self.triadic_module_path.read_bytes()).hexdigest()
        if triadic_digest != MPL_TC_TRIADIC_MODULE_SHA256:
            raise MPLTCDependencyError(
                "MPL-TC triadic source checksum mismatch: expected "
                f"{MPL_TC_TRIADIC_MODULE_SHA256}, received {triadic_digest}"
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

    def _load_triadic(self) -> ModuleType:
        if self._triadic_module is not None:
            return self._triadic_module
        module_name = "_tne_pinned_mpl_tc_triadic_domains"
        spec = importlib.util.spec_from_file_location(module_name, self.triadic_module_path)
        if spec is None or spec.loader is None:
            raise MPLTCDependencyError("unable to construct the MPL-TC triadic loader")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            sys.modules.pop(module_name, None)
            raise MPLTCDependencyError(f"MPL-TC triadic module import failed: {exc}") from exc
        self._triadic_module = module
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
                f"at most {law_class.max_supported_primes()} primes"
            )
        law = law_class()
        result = law.generate_prime_sequence(count)
        primes = tuple(int(value) for value in result["primes"])
        gaps = tuple(int(value) for value in result["gaps"])
        motifs = tuple(str(value) for value in result["motifs"])
        motif_runs = tuple(int(value) for value in result["motif_runs"])
        return MPLTCPrefix(primes, gaps, motifs, motif_runs)

    def triadic_streams(self, limit: int) -> MPLTCTriadicStreams:
        if not isinstance(limit, int) or limit < 2:
            raise ValueError("triadic stream limit must be an integer >= 2")
        prefix_count = min(max(2, limit), 256)
        prefix = self.prefix(prefix_count)
        module = self._load_triadic()
        triadic_class = getattr(module, "TriadicDomains", None)
        if triadic_class is None:
            raise MPLTCDependencyError("pinned MPL-TC checkout does not expose TriadicDomains")
        domains = triadic_class(prefix.primes)
        placements: list[MPLTCAxisPlacement] = []
        for value in range(1, limit + 1):
            placement = domains.place(value)
            depth = 0
            reduced = value
            while reduced > 0 and reduced % 2 == 0:
                depth += 1
                reduced //= 2
            if placement.domain == "E":
                stream_kind: TCStreamKind = "pure_even_lift" if reduced == 1 else "mixed_even_composite"
            elif placement.kind == "odd-prime":
                stream_kind = "first_order_odd"
            else:
                stream_kind = "lpf_odd_composite"
            placements.append(
                MPLTCAxisPlacement(
                    value=value,
                    domain=placement.domain,
                    axis=placement.axis,
                    stream_kind=stream_kind,
                    least_prime_factor=placement.least_prime_factor,
                    cofactor=placement.cofactor,
                    dyadic_depth=depth,
                )
            )
        return MPLTCTriadicStreams(
            tuple(item for item in placements if item.stream_kind == "pure_even_lift"),
            tuple(item for item in placements if item.stream_kind == "first_order_odd"),
            tuple(item for item in placements if item.stream_kind == "lpf_odd_composite"),
            tuple(item for item in placements if item.stream_kind == "mixed_even_composite"),
            limit,
        )

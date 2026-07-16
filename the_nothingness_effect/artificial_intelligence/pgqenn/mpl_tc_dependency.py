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
MPL_TC_TRIADIC_MODULE_SHA256 = "1c988099a21e4c4440fca8220b11f3989408d5eb18e9f57e431d5732e5e2a6af"
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

    @staticmethod
    def _dyadic_depth(value: int) -> tuple[int, int]:
        depth = 0
        odd_face = int(value)
        while odd_face % 2 == 0:
            depth += 1
            odd_face //= 2
        return depth, odd_face

    def triadic_streams(
        self,
        count: int,
        *,
        limit: int | None = None,
    ) -> MPLTCTriadicStreams:
        """Expose the four finite-prefix TC number streams without relabeling them."""

        prefix = self.prefix(count)
        finite_limit = int(limit or max(64, 2 * prefix.primes[-1]))
        if finite_limit < prefix.primes[-1]:
            raise ValueError("triadic stream limit must include the requested prime prefix")
        module = self._load_triadic()
        domains_class = getattr(module, "TriadicDomains", None)
        if domains_class is None:
            raise MPLTCDependencyError("pinned MPL-TC checkout does not expose TriadicDomains")
        domains = domains_class(prefix.primes)

        pure_even: list[MPLTCAxisPlacement] = []
        value = 2
        while value <= finite_limit:
            placement = domains.place(value)
            depth, odd_face = self._dyadic_depth(value)
            if odd_face != 1:
                raise MPLTCDependencyError("pure even lift unexpectedly left the Unity face")
            pure_even.append(
                MPLTCAxisPlacement(
                    value, placement.domain, placement.axis, "pure_even_lift",
                    cofactor=placement.cofactor, dyadic_depth=depth,
                )
            )
            value *= 2

        first_order = tuple(
            MPLTCAxisPlacement(
                prime, "O", "O1", "first_order_odd", dyadic_depth=0
            )
            for prime in prefix.primes
            if prime != 2
        )
        odd_composites = tuple(
            MPLTCAxisPlacement(
                placement.value,
                placement.domain,
                placement.axis,
                "lpf_odd_composite",
                placement.least_prime_factor,
                placement.cofactor,
                0,
            )
            for placement in domains.odd_composite_stream(finite_limit)
        )

        odd_faces = sorted(
            {placement.value for placement in (*first_order, *odd_composites)}
        )
        mixed: list[MPLTCAxisPlacement] = []
        for odd_face in odd_faces:
            value = 2 * odd_face
            while value <= finite_limit:
                placement = domains.place(value)
                depth, resolved_odd_face = self._dyadic_depth(value)
                if resolved_odd_face != odd_face:
                    raise MPLTCDependencyError("mixed-even stream lost its odd face")
                odd_placement = domains.place(odd_face)
                mixed.append(
                    MPLTCAxisPlacement(
                        value,
                        placement.domain,
                        placement.axis,
                        "mixed_even_composite",
                        odd_placement.least_prime_factor,
                        odd_face,
                        depth,
                    )
                )
                value *= 2
        mixed.sort(key=lambda placement: (placement.value, placement.dyadic_depth))
        streams = MPLTCTriadicStreams(
            tuple(pure_even),
            first_order,
            odd_composites,
            tuple(mixed),
            finite_limit,
        )
        if any(not stream for stream in (
            streams.pure_even_lifts,
            streams.first_order_odds,
            streams.lpf_odd_composites,
            streams.mixed_even_composites,
        )):
            raise MPLTCDependencyError("finite TC prefix did not realize all four number streams")
        return streams

    @property
    def metadata(self) -> dict[str, str]:
        return {
            "repository": MPL_TC_REPOSITORY_URL,
            "commit": MPL_TC_COMMIT,
            "module_sha256": MPL_TC_MODULE_SHA256,
            "triadic_module_sha256": MPL_TC_TRIADIC_MODULE_SHA256,
            "dependency_mode": "pinned_git_submodule",
        }

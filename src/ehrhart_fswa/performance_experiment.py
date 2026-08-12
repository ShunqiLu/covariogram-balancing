"""Deterministic wall-time and Python-heap measurements for exact routines."""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import tracemalloc
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable, Sequence

from .counts import (
    cross_polytope_overlap_count,
    hybrid_l1_radius,
    truncated_l1_lattice_count,
)
from .polytope import rational_octagon
from .samplers import rank_truncated_l1, unrank_truncated_l1


@dataclass(frozen=True)
class PerformanceRow:
    operation: str
    parameters: str
    exact_result_digest: str
    wall_seconds: float
    python_peak_mib: float
    arithmetic_complexity: str
    notes: str


@dataclass(frozen=True)
class EnvironmentInfo:
    python_version: str
    python_executable: str
    operating_system: str
    windows_build: str
    cpu: str
    physical_cores: str
    logical_processors: str
    ram_gib: str
    wsl: bool
    power_scheme: str


def _powershell_value(expression: str) -> str:
    """Return one read-only Windows system value, or ``unavailable``."""

    if platform.system() != "Windows":
        return "not applicable"
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", expression],
            check=True,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "unavailable"
    # Decode explicitly instead of relying on the host ANSI code page.  Native
    # utilities such as ``powercfg`` may emit localized UTF-8 text even when
    # Python's preferred Windows encoding is GBK.
    value = completed.stdout.decode("utf-8", errors="replace").strip()
    return value if value else "unavailable"


def collect_environment() -> EnvironmentInfo:
    """Collect enough host metadata to interpret, but not normalize, timings."""

    cpu = _powershell_value("(Get-CimInstance Win32_Processor | Select-Object -First 1).Name")
    physical_cores = _powershell_value(
        "(Get-CimInstance Win32_Processor | Select-Object -First 1).NumberOfCores"
    )
    logical_processors = _powershell_value(
        "(Get-CimInstance Win32_Processor | Select-Object -First 1).NumberOfLogicalProcessors"
    )
    ram_bytes = _powershell_value(
        "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"
    )
    try:
        ram_gib = f"{int(ram_bytes) / (1024**3):.2f}"
    except ValueError:
        ram_gib = ram_bytes
    windows_build = _powershell_value(
        "(Get-CimInstance Win32_OperatingSystem).BuildNumber"
    )
    power_scheme = _powershell_value("powercfg /getactivescheme")
    balanced_guid = "381b4222-f694-41f0-9685-ff5bb260df2e"
    if balanced_guid in power_scheme.lower():
        power_scheme = f"Balanced ({balanced_guid})"
    is_wsl = bool(os.environ.get("WSL_DISTRO_NAME")) or "microsoft" in (
        platform.release().lower()
    )
    return EnvironmentInfo(
        python_version=platform.python_version(),
        python_executable=sys.executable,
        operating_system=platform.platform(),
        windows_build=windows_build,
        cpu=cpu,
        physical_cores=physical_cores,
        logical_processors=logical_processors,
        ram_gib=ram_gib,
        wsl=is_wsl,
        power_scheme=power_scheme,
    )


def _measure(
    operation: str,
    parameters: str,
    function: Callable[[], int],
    complexity: str,
    notes: str,
) -> PerformanceRow:
    tracemalloc.start()
    started = perf_counter()
    result = function()
    elapsed = perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    # A short exact fingerprint makes silent changes visible without flooding
    # the table with thousand-digit counts.
    digest = f"digits={len(str(abs(result)))},mod2^64={result % (1 << 64)}"
    return PerformanceRow(
        operation,
        parameters,
        digest,
        elapsed,
        peak / (1024 * 1024),
        complexity,
        notes,
    )


def run_benchmarks() -> list[PerformanceRow]:
    octagon = rational_octagon()

    def rank_roundtrips() -> int:
        total = truncated_l1_lattice_count(16, 16, 64)
        checksum = 0
        for index in range(64):
            rank = (index * (total - 1)) // 63
            point = unrank_truncated_l1(rank, 16, 16, 64)
            recovered = rank_truncated_l1(point, 16, 64)
            if recovered != rank:
                raise AssertionError("rank/unrank mismatch")
            checksum ^= recovered
        return checksum

    return [
        _measure(
            "cross-overlap bivariate DP",
            "d=4,t=40,u=(6,0,0,0)",
            lambda: cross_polytope_overlap_count(40, (6, 0, 0, 0)),
            "O(d t^3) naive sparse-truncated arithmetic; O(t^2) states",
            "exact Python integers; signed-permutation canonical cache",
        ),
        _measure(
            "truncated-l1 count",
            "d=32,B=608,L=floor(608*sqrt(32))",
            lambda: truncated_l1_lattice_count(608, 32, hybrid_l1_radius(608, 32)),
            "O(d L) arithmetic and O(L) coefficient storage",
            "sliding-window univariate DP",
        ),
        _measure(
            "generic rational H-enumeration",
            "rational octagon,d=2,t=80,u=(1,0)",
            lambda: octagon.overlap_count(80, (1, 0)),
            "O((2t+1)^d * number_of_facets)",
            "independent low-dimensional reference enumerator",
        ),
        _measure(
            "rank/unrank round trips",
            "64 deterministic ranks,d=16,B=16,L=64",
            rank_roundtrips,
            "O(samples*d*B) completion-count queries after DP caching",
            "reference implementation; no constant-time claim",
        ),
    ]


def write_outputs(
    rows: Sequence[PerformanceRow], prefix: Path, environment: EnvironmentInfo
) -> None:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    with prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    lines = [
        "# Exact-routine performance and memory\n\n",
        f"Environment: Python {environment.python_version}, "
        f"{environment.operating_system} (build {environment.windows_build}), "
        f"executable `{environment.python_executable}`; CPU "
        f"{environment.cpu} ({environment.physical_cores} physical cores, "
        f"{environment.logical_processors} logical processors); "
        f"{environment.ram_gib} GiB RAM; WSL={environment.wsl}; active power "
        f"scheme `{environment.power_scheme}`. "
        "Times are one deterministic reference run; memory is the peak Python "
        "heap reported by `tracemalloc`, not process RSS. These figures are "
        "reproducibility diagnostics, not optimized implementation claims.\n\n",
        "| operation | parameters | seconds | peak MiB | result fingerprint |\n",
        "|---|---|---:|---:|---|\n",
    ]
    for row in rows:
        lines.append(
            f"| {row.operation} | `{row.parameters}` | {row.wall_seconds:.6f} | "
            f"{row.python_peak_mib:.3f} | `{row.exact_result_digest}` |\n"
        )
    lines.append("\n## Complexity model\n\n")
    for row in rows:
        lines.append(
            f"- **{row.operation}:** {row.arithmetic_complexity}. {row.notes}.\n"
        )
    prefix.with_suffix(".md").write_text("".join(lines), encoding="utf-8")
    environment_path = prefix.with_name(f"{prefix.name}_environment.json")
    environment_path.write_text(
        json.dumps(asdict(environment), indent=2, sort_keys=True), encoding="utf-8"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-prefix", type=Path, default=Path("results") / "performance"
    )
    args = parser.parse_args(argv)
    rows = run_benchmarks()
    environment = collect_environment()
    write_outputs(rows, args.output_prefix, environment)
    print(
        f"wrote {len(rows)} measurements to {args.output_prefix}.[csv|md] "
        "and an environment JSON"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

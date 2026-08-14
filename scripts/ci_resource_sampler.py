"""Resource sampler for the CI pytest step (Sb_OPS_CI_RUNNER_STABILITY_01, WS1).

Emits machine-greppable `CI_RESOURCE` lines to **stdout** every few seconds
while pytest runs.

**Why stdout and not an artifact.** Three runner shutdowns killed the job before
any upload step could run — `Skip evaluate condition on runner shutdown` was
printed for every subsequent step, artifact upload included. A measurement that
only exists in a file we never get to upload is a measurement we do not have.
Streaming to the live log means the last sample before the runner dies is
already in the log we can read afterwards.

Reads `/proc` directly rather than depending on `psutil`, so it adds no
dependency to the CI image and cannot itself fail on an import.

**It never fails the build.** Every probe is individually guarded: a missing
file, an unreadable cgroup or a process that exits mid-sample degrades that one
field to `na`, never raises, and never touches the pytest exit code. Diagnostics
that can turn a red build green — or a green build red — are worse than no
diagnostics.

No secrets, no environment dump: only counters.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

#: Prefix every line so the whole series can be extracted from a noisy CI log
#: with a single grep, even interleaved with pytest's progress output.
PREFIX = "CI_RESOURCE"

#: Sampling period. Fast enough to catch the last seconds before a shutdown,
#: slow enough that the sampler is not itself a load source.
DEFAULT_INTERVAL_S = 12.0

#: Prefix used by the `client` fixture in tests/conftest.py.
TMP_PREFIX = "workout-test-"

_KB_PER_MB = 1024


def _read_text(path: str) -> str | None:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _meminfo() -> dict[str, int]:
    """`/proc/meminfo` in MB. Empty dict when unavailable (non-Linux)."""
    raw = _read_text("/proc/meminfo")
    if not raw:
        return {}
    out: dict[str, int] = {}
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].endswith(":"):
            try:
                out[parts[0][:-1]] = int(parts[1]) // _KB_PER_MB
            except ValueError:
                continue
    return out


def _loadavg() -> str:
    raw = _read_text("/proc/loadavg")
    if not raw:
        return "na"
    return raw.split()[0]


def _proc_rss_mb(pid: int) -> int | None:
    """RSS of one process, MB. `None` if it exited between listing and read."""
    raw = _read_text(f"/proc/{pid}/status")
    if not raw:
        return None
    for line in raw.splitlines():
        if line.startswith("VmRSS:"):
            parts = line.split()
            if len(parts) >= 2:
                try:
                    return int(parts[1]) // _KB_PER_MB
                except ValueError:
                    return None
    return None


def _pytest_tree() -> list[tuple[int, int]]:
    """`(pid, rss_mb)` for every live pytest/xdist process.

    Identified by command line rather than by walking a parent tree: xdist
    workers are re-executed and can be reparented, so a tree walk from the
    controller misses them exactly when they matter most.
    """
    found: list[tuple[int, int]] = []
    try:
        pids = [entry for entry in os.listdir("/proc") if entry.isdigit()]
    except OSError:
        return found
    for entry in pids:
        cmdline = _read_text(f"/proc/{entry}/cmdline")
        if not cmdline:
            continue
        flat = cmdline.replace("\x00", " ")
        if "pytest" not in flat and "execnet" not in flat:
            continue
        rss = _proc_rss_mb(int(entry))
        if rss is not None:
            found.append((int(entry), rss))
    return found


def _cgroup_memory() -> dict[str, str]:
    """cgroup v2 memory counters, or an explicit `na` — never invented."""
    base = Path("/sys/fs/cgroup")
    out: dict[str, str] = {}
    for key, name in (
        ("cg_current_mb", "memory.current"),
        ("cg_peak_mb", "memory.peak"),
        ("cg_max", "memory.max"),
    ):
        raw = _read_text(str(base / name))
        if raw is None:
            out[key] = "na"
            continue
        value = raw.strip()
        if value == "max":
            out[key] = "max"
            continue
        try:
            out[key] = str(int(value) // (_KB_PER_MB * _KB_PER_MB))
        except ValueError:
            out[key] = "na"
    return out


def _tmp_usage() -> tuple[int, int]:
    """`(directory count, cumulative MB)` for fixture-created temp dirs."""
    root = Path(tempfile.gettempdir())
    count = 0
    total = 0
    try:
        entries = list(root.glob(f"{TMP_PREFIX}*"))
    except OSError:
        return (0, 0)
    for entry in entries:
        count += 1
        try:
            for path in entry.rglob("*"):
                if path.is_file():
                    total += path.stat().st_size
        except OSError:
            continue
    return (count, total // (_KB_PER_MB * _KB_PER_MB))


def _disk_free_mb() -> int | str:
    try:
        return shutil.disk_usage("/").free // (_KB_PER_MB * _KB_PER_MB)
    except OSError:
        return "na"


def emit_host_header() -> None:
    """One-shot host facts. Printed before pytest so they survive any death."""
    mem = _meminfo()
    cgroup = _cgroup_memory()
    nproc = "na"
    try:
        nproc = str(len(os.sched_getaffinity(0)))  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        nproc = str(os.cpu_count() or "na")
    print(
        f"{PREFIX}_HOST cpu_count={os.cpu_count()} affinity={nproc} "
        f"mem_total_mb={mem.get('MemTotal', 'na')} "
        f"swap_total_mb={mem.get('SwapTotal', 'na')} "
        f"disk_free_mb={_disk_free_mb()} "
        f"cg_max={cgroup['cg_max']}",
        flush=True,
    )


def emit_sample() -> None:
    mem = _meminfo()
    tree = _pytest_tree()
    cgroup = _cgroup_memory()
    tmp_dirs, tmp_mb = _tmp_usage()
    aggregate = sum(rss for _, rss in tree)
    largest = max((rss for _, rss in tree), default=0)
    print(
        f"{PREFIX} ts={int(time.time())} "
        f"mem_available_mb={mem.get('MemAvailable', 'na')} "
        f"swap_free_mb={mem.get('SwapFree', 'na')} "
        f"disk_free_mb={_disk_free_mb()} "
        f"load1={_loadavg()} "
        f"procs={len(tree)} tree_rss_mb={aggregate} max_proc_rss_mb={largest} "
        f"cg_current_mb={cgroup['cg_current_mb']} cg_peak_mb={cgroup['cg_peak_mb']} "
        f"tmp_dirs={tmp_dirs} tmp_mb={tmp_mb}",
        flush=True,
    )


def main() -> int:
    interval = float(os.environ.get("CI_SAMPLE_INTERVAL_S", DEFAULT_INTERVAL_S))
    emit_host_header()
    while True:
        try:
            emit_sample()
        except Exception as exc:  # noqa: BLE001 — a probe must never kill the job
            print(f"{PREFIX}_ERROR kind={type(exc).__name__}", flush=True)
        time.sleep(interval)


if __name__ == "__main__":  # pragma: no cover - entry point
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
